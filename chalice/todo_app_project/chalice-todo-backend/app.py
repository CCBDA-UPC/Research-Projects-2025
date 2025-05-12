from chalice import Chalice, NotFoundError, BadRequestError
import boto3
import uuid
from datetime import datetime
import os  # For environment variables (optional for table name)

app = Chalice(app_name="chalice-todo-backend")
app.debug = True  # Optional: for more detailed error messages during development

# Option 1: Get table name from environment variable (recommended for flexibility)
# DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'ChaliceTodoListTable')
# Option 2: Hardcode table name (simpler for this example)
DYNAMODB_TABLE_NAME = (
    "ChaliceTodoListTable"  # <<< MAKE SURE THIS MATCHES YOUR TABLE NAME
)

dynamodb = None
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):  # Check if running in AWS Lambda
    dynamodb = boto3.resource("dynamodb")
else:  # For local development, ensure your AWS CLI is configured
    # You might need to specify region if not in default AWS CLI config
    # session = boto3.Session(region_name='your-aws-region')
    # dynamodb = session.resource('dynamodb')
    dynamodb = boto3.resource("dynamodb")  # Assumes default session is fine

table = dynamodb.Table(DYNAMODB_TABLE_NAME)


@app.route("/", methods=["GET"])
def index():
    return {"message": "Welcome to the Chalice To-Do List API!"}


@app.route("/tasks", methods=["POST"])
def add_task():
    task_data = app.current_request.json_body
    title = task_data.get("title")
    due_date_str = task_data.get("dueDate")  # Expected format: YYYY-MM-DD

    if not title or not due_date_str:
        raise BadRequestError("Task 'title' and 'dueDate' (YYYY-MM-DD) are required.")

    try:
        datetime.strptime(due_date_str, "%Y-%m-%d")
    except ValueError:
        raise BadRequestError("Invalid 'dueDate' format. Please use YYYY-MM-DD.")

    task_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    item = {
        "taskId": task_id,
        "title": title,
        "dueDate": due_date_str,
        "completed": False,
        "createdAt": timestamp,
        "updatedAt": timestamp,
    }

    try:
        table.put_item(Item=item)
        app.log.info(f"Task added: {task_id} - {title}")
        return {"message": "Task added successfully", "task": item}, 201
    except Exception as e:
        app.log.error(f"Error adding task: {e}")
        raise ChaliceViewError("Could not add task")


@app.route("/tasks", methods=["GET"])
def list_tasks():
    try:
        # For a real app, consider pagination for large datasets
        response = table.scan()
        # Sort by due date, then by creation date if due dates are the same
        tasks = sorted(
            response.get("Items", []), key=lambda x: (x["dueDate"], x["createdAt"])
        )
        return {"tasks": tasks}
    except Exception as e:
        app.log.error(f"Error listing tasks: {e}")
        raise ChaliceViewError("Could not list tasks")


@app.route("/tasks/{task_id}", methods=["GET"])
def get_task(task_id):
    try:
        response = table.get_item(Key={"taskId": task_id})
        if "Item" not in response:
            raise NotFoundError(f"Task with ID '{task_id}' not found.")
        return {"task": response["Item"]}
    except Exception as e:
        app.log.error(f"Error getting task {task_id}: {e}")
        if isinstance(e, NotFoundError):
            raise
        raise ChaliceViewError(f"Could not get task {task_id}")


@app.route("/tasks/{task_id}", methods=["PUT"])
def update_task(task_id):
    updates = app.current_request.json_body
    app.log.info(
        f"Received update request for task {task_id} with payload: {updates}"
    )  # Log received payload

    if not updates:
        raise BadRequestError(
            "No update data provided. Provide 'title', 'dueDate', or 'completed'."
        )

    # Check if task exists
    try:
        response = table.get_item(Key={"taskId": task_id})
        if "Item" not in response:
            raise NotFoundError(f"Task with ID '{task_id}' not found.")
    except NotFoundError:  # Specifically catch NotFoundError to re-raise
        app.log.warn(f"Task {task_id} not found for update.")
        raise
    except Exception as e:
        app.log.error(f"Error finding task {task_id} for update: {e}")
        raise ChaliceViewError(
            f"Could not find task {task_id} to update due to an internal issue."
        )

    update_expression_parts = []
    expression_attribute_values = {}
    expression_attribute_names = {}

    # Only add attributes to be updated if they are present in the payload AND not None
    if "title" in updates and updates["title"] is not None:
        update_expression_parts.append("#t = :title")
        expression_attribute_names["#t"] = "title"
        expression_attribute_values[":title"] = updates["title"]
    elif "title" in updates and updates["title"] is None:
        # If you want to allow removing an attribute by setting it to None,
        # you'd use the REMOVE action in UpdateExpression.
        # For simplicity here, we are only SETting non-None values.
        # Or, you could raise a BadRequestError if None is not allowed for a required field.
        app.log.info(
            f"Received null for 'title' for task {task_id}, not updating this field."
        )

    if "dueDate" in updates and updates["dueDate"] is not None:
        try:
            datetime.strptime(updates["dueDate"], "%Y-%m-%d")
            update_expression_parts.append(
                "#dd = :dueDate"
            )  # Using placeholder for consistency
            expression_attribute_names["#dd"] = "dueDate"
            expression_attribute_values[":dueDate"] = updates["dueDate"]
        except ValueError:
            raise BadRequestError("Invalid 'dueDate' format. Please use YYYY-MM-DD.")
    elif "dueDate" in updates and updates["dueDate"] is None:
        app.log.info(
            f"Received null for 'dueDate' for task {task_id}, not updating this field."
        )

    if "completed" in updates and isinstance(
        updates["completed"], bool
    ):  # Check for bool specifically
        update_expression_parts.append(
            "#c = :completed"
        )  # Using placeholder for consistency
        expression_attribute_names["#c"] = "completed"
        expression_attribute_values[":completed"] = updates["completed"]
    elif (
        "completed" in updates and updates["completed"] is None
    ):  # If explicitly sent as null
        app.log.info(
            f"Received null for 'completed' for task {task_id}, not updating this field."
        )

    # If only nulls were provided for updatable fields (or no valid fields),
    # we will still update 'updatedAt'.
    if not update_expression_parts and not (
        "updatedAt" in updates and updates["updatedAt"] is not None
    ):  # Avoid adding updatedAt twice if provided
        # If you require at least one field to be changed other than updatedAt:
        # raise BadRequestError("No valid fields or non-null values provided for update.")
        # For now, we'll allow an "update" that only touches updatedAt if no other fields are validly set.
        app.log.info(
            f"No specific fields to update for task {task_id} other than 'updatedAt'."
        )

    # Always attempt to update the 'updatedAt' timestamp
    update_expression_parts.append("#ua = :updatedAt")
    expression_attribute_names["#ua"] = "updatedAt"
    expression_attribute_values[":updatedAt"] = datetime.utcnow().isoformat()

    update_expression = "SET " + ", ".join(update_expression_parts)

    # CRITICAL LOGGING: See exactly what's being sent to DynamoDB
    app.log.info(f"Attempting UpdateItem for task {task_id}:")
    app.log.info(f"  UpdateExpression: {update_expression}")
    app.log.info(f"  ExpressionAttributeValues: {expression_attribute_values}")
    app.log.info(
        f"  ExpressionAttributeNames: {expression_attribute_names if expression_attribute_names else 'Not Used'}"
    )

    try:
        updated_item_response = table.update_item(
            Key={"taskId": task_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=(
                expression_attribute_names if expression_attribute_names else None
            ),  # Pass None if empty
            ReturnValues="ALL_NEW",
        )
        app.log.info(f"Task updated successfully in DynamoDB: {task_id}")
        return {
            "message": "Task updated successfully",
            "task": updated_item_response["Attributes"],
        }
    except Exception as e:
        # This is where your current error message is coming from
        app.log.error(
            f"DynamoDB UpdateItem call failed for task {task_id}: {e}"
        )  # More specific log
        # Log the full traceback for easier debugging in CloudWatch
        import traceback

        app.log.error(traceback.format_exc())
        raise ChaliceViewError(f"Could not update task {task_id} in the database.")


@app.route("/tasks/{task_id}", methods=["DELETE"])
def delete_task(task_id):
    try:
        # Ensure task exists before attempting delete for a clearer error
        response = table.get_item(Key={"taskId": task_id})
        if "Item" not in response:
            raise NotFoundError(f"Task with ID '{task_id}' not found.")

        table.delete_item(Key={"taskId": task_id})
        app.log.info(f"Task deleted: {task_id}")
        return {"message": f"Task '{task_id}' deleted successfully."}
    except Exception as e:
        app.log.error(f"Error deleting task {task_id}: {e}")
        if isinstance(e, NotFoundError):
            raise
        raise ChaliceViewError(f"Could not delete task {task_id}")
