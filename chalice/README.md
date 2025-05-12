# Serverless API with AWS Chalice
## Table of Contents

- [Introduction](#introduction)
  - [AWS Chalice](#aws-chalice)
  - [Streamlit](#streamlit)
  - [AWS DynamoDB](#aws-dynamodb)
- [Tutorial](#tutorial)
  - [Project Structure](#project-structure)
  - [Step 1: Create and Configure DynamoDB Table](#step-1-create-and-configure-dynamodb-table)
  - [Step 2: Set Up AWS Credentials for Development](#step-2-set-up-aws-credentials-for-development)
  - [Step 3: Create the Chalice Backend](#step-3-create-the-chalice-backend)
  - [Step 4: Create frontend with Streamlit](#step-4-create-frontend-with-streamlit)
  - [Step 5: Deploying the Streamlit frontend](#step-5-deploying-the-streamlit-frontend)
  - [Final Result](#final-result)
- [Conclusion](#conclusion)

## Introduction

In this tutorial, we will build and deploy a full-stack serverless To-Do application with AWS Chalice, DynamoDB, and Streamlit

The backend API is built using Chalice and Amazon DynamoDB. The frontend user interface is created with Streamlit and will be deployed to Streamlit Community Cloud and hosted on github.

All deployed and available through API Gateway public URLs.

<img src="images/App_landing_2.png" width="60%" style="display: block; margin: 0 auto">

### AWS Chalice

<img src="images/chalice.png" width="50%" style="display: block; margin: 0 auto">

AWS Chalice is a microframework developed by Amazon to help developers create and deploy serverless applications in Python quickly and easily.

With Chalice, you can write Python code that is automatically deployed to AWS Lambda and exposed via API Gateway, allowing you to create REST APIs, web applications, and event-driven services without managing servers.

It is designed to work smoothly with various AWS services, such as:

- AWS Lambda (to run your Python functions in the cloud)
- API Gateway (to expose your functions as HTTP endpoints)
- S3, SQS, SNS, DynamoDB, and more (to integrate with other AWS services)

You can think of Chalice as similar to frameworks like Flask or FastAPI, but instead of running on your own server, it is optimized for creating serverless applications that scale automatically and require no infrastructure management.

In summary:

- It allows writing simple Python code and deploying it directly to AWS.
- It automatically handles deployment, IAM permissions, and API Gateway configuration.
- It is ideal for creating microservices, REST APIs, and event-driven architectures in a serverless way.

### Streamlit

<img src="images/streamlit-logo-primary-colormark-lighttext.png" width="50%" style="display: block; margin: 0 auto">

**What is Streamlit?**
Streamlit is an open-source Python library that makes it easy to create and share beautiful, custom web applications for machine learning, data science, or any Python project that needs a user interface. It allows you to turn data scripts into shareable web apps in minutes, often with just a few lines of code.

**Core Concepts:**

- **Script Execution Model:** Streamlit apps are Python scripts that run from top to bottom every time a user interacts with a widget or the app needs to update. This simple execution model makes it easy to reason about.
- **Widgets:** Streamlit provides a wide range of interactive widgets (e.g., `st.button`, `st.text_input`, `st.slider`, `st.selectbox`, `st.file_uploader`) that can be added to your app with simple Python function calls. User interaction with these widgets triggers a rerun of the script.
- **State Management:**
  - **Implicit State:** Widget values are implicitly part of Streamlit's state.
  - **Session State (`st.session_state`):** Allows you to store variables and state across script reruns for a single user session, enabling more complex, multi-step interactions.
- **Layout:** Streamlit offers commands for organizing your app's layout, such as `st.sidebar`, `st.columns`, `st.expander`, and `st.container`.

**Key Features:**

- **Simplicity:** Write apps using only Python. No HTML, CSS, or JavaScript knowledge is required to get started.
- **Fast Iteration:** Apps update live as you edit and save your Python script.
- **Interactive Widgets:** A rich set of widgets allows for easy user input and interaction.
- **Data Display:** Excellent support for displaying data (tables, charts, text, images, audio, video).
- **Caching:** Built-in caching (`st.cache_data`, `st.cache_resource`) optimizes performance for expensive computations or data loading.
- **Custom Components:** Ability to create or use third-party custom components to extend functionality.

**How it Works:**
You write a standard Python script (`.py` file). When you run it with `streamlit run your_app.py`, Streamlit starts a local web server. This server executes your script and renders the output as a web page. When a user interacts with a widget, the script reruns from top to bottom, and Streamlit intelligently updates only the parts of the UI that have changed.

**Benefits:**

- **Ease of Use:** Extremely low learning curve for Python developers.
- **Rapid Prototyping:** Quickly build and iterate on UIs for data-driven applications or tools.
- **Python Ecosystem:** Seamlessly integrates with popular Python libraries like Pandas, NumPy, Matplotlib, Scikit-learn, etc.
- **Sharing:** Easy to share apps locally, and platforms like Streamlit Community Cloud make public deployment straightforward.

### AWS DynamoDB

<img src="images/amazon-dynamodb-logo.png" width="50%" style="display: block; margin: 0 auto">

**What is DynamoDB?**
Amazon DynamoDB is a fully managed, serverless, NoSQL key-value and document database designed for high-performance applications at any scale.

**Key Features:**

- **Serverless:** No servers to provision, patch, or manage. DynamoDB automatically scales capacity to meet workload demands and you pay for what you use (or provisioned capacity).
- **Scalability:** Delivers single-digit millisecond performance at any scale, capable of handling trillions of requests per day.
- **Flexible Schema:** Being a NoSQL database, you don't need to define all your columns upfront (except for the primary key). Each item can have a different set of attributes.
- **Data Model:** Supports both key-value (using a primary key) and document (JSON-like nested data structures) models.
- **High Availability and Durability:** Data is automatically replicated across multiple Availability Zones in an AWS Region.
- **Integrations:** Integrates well with other AWS services, including AWS Lambda.

**Use Case in This Project:**
In our To-Do application, DynamoDB is used to store the individual task items. Each task will be an item in a DynamoDB table, with attributes like `taskId` (primary key), `title`, `dueDate`, `completed`, `createdAt`, and `updatedAt`. Chalice backend functions will use `boto3` to interact with this DynamoDB table to create, read, update, and delete tasks.

[Back to top](#)

## Tutorial

### Project Structure

We will create a main project directory containing subdirectories for the backend and frontend:

```bash
todo_app_project/
│
├── chalice-env/                   # Virtual env for Chalice but a general venv can also be used
├── chalice-todo-backend/          # Chalice backend project
│   ├── .chalice/
│   │   ├── config.json
│   │   └── policy-dev.json
│   ├── app.py
│   └── requirements.txt
│
├── streamlit-env/                 # Virtual env for Chalice but a general venv can also be used
│── streamlit-frontend/            # Streamlit frontend project
│   ├── todo_streamlit_app.py
│   └── requirements.txt
```

[Back to top](#)

You can choose to use one shared virtual environment for both, but ensure the `requirements.txt` files within each project folder are specific to that project's deployment needs.

### Step 1: Create and Configure DynamoDB Table

1.  Go to the **AWS Management Console**.
2.  Search for and navigate to the **DynamoDB** service.
3.  Click **Create table**.
4.  **Table name:** `ChaliceTodoListTable`.
5.  **Partition key (Primary Key):**
    - Name: `taskId`
    - Type: `String`
6.  **Table settings:** You can leave "Default settings" or choose "Customize settings" to select "On-demand" capacity mode, which is often simpler for development.
7.  Click **Create table**. Wait for the table status to become "Active".

### Step 2: Set Up AWS Credentials for Development

This was covered in the Prerequisites. Ensure your `aws configure` is set up correctly with an IAM user that has permissions for Lambda, API Gateway, IAM (for role creation), and DynamoDB. For initial development, policies like `AWSLambda_FullAccess`, `AmazonAPIGatewayAdministrator`, `IAMFullAccess` (or more granular permissions for role creation), and `AmazonDynamoDBFullAccess` might be used on a development IAM user, but always follow the principle of least privilege in production.

```bash
$ aws configure
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

[Back to top](#)

### Step 3: Create the Chalice Backend

1.  Open your terminal and navigate to where you want to create your main project directory (`todo_app_project`).
    ```bash
    mkdir todo_app_project
    cd todo_app_project
    ```
2.  Create and activate a virtual environment for the Chalice backend:
    ```bash
    python3 -m venv chalice-env
    source chalice-env/bin/activate  # On macOS/Linux
    # .\chalice-env\Scripts\activate  # On Windows
    ```
3.  Install Chalice and Boto3:
    ```bash
    pip install chalice boto3
    ```
4.  Create a new Chalice project:
    ```bash
    chalice new-project chalice-todo-backend
    cd chalice-todo-backend
    ```

#### Step 3.1: Write the application code (`app.py`)

Replace the contents of `chalice-todo-backend/app.py` with the following code:

```python
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
    ):
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
```

#### Step 3.2: Define Dependencies (`requirements.txt` for backend)

Create a file named `requirements.txt` in your `chalice-todo-backend` directory with the following content. This file lists the Python packages your Chalice application needs.

```txt
chalice
boto3
```

#### Step 3.3: Configure IAM Permissions for Chalice

Chalice needs permissions to create Lambda functions and API Gateway endpoints. The Lambda function, in turn, needs permissions to access DynamoDB and CloudWatch Logs. We will provide a custom policy for this.

1.  Edit .chalice/config.json:
    This file is created automatically by Chalice when you create a new project. Open it and modify it. Pay attention to the dev stage (or your current working stage). We set autogen_policy to false to tell Chalice we will provide our own policy file.

    ```json
    {
      "version": "2.0",
      "app_name": "chalice-todo-backend",
      "stages": {
        "dev": {
          "api_gateway_stage": "api",
          "autogen_policy": false
        }
      }
    }
    ```

2.  Create .chalice/policy-dev.json:
    In the .chalice directory (same level as config.json), create a new file named policy-dev.json (if your stage is dev). Add the following JSON content.
    Important:
    _ Replace YOUR_AWS_REGION with your actual AWS region (e.g., us-east-1).
    _ Replace YOUR_AWS_ACCOUNT_ID with your 12-digit AWS Account ID. \* Ensure ChaliceTodoListTable matches the name of the DynamoDB table you created.

    ```json
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "dynamodb:PutItem",
            "dynamodb:GetItem",
            "dynamodb:UpdateItem",
            "dynamodb:DeleteItem",
            "dynamodb:Scan",
            "dynamodb:Query"
          ],
          "Resource": [
            "arn:aws:dynamodb:YOUR_AWS_REGION:YOUR_AWS_ACCOUNT_ID:table/ChaliceTodoListTable"
          ]
        },
        {
          "Effect": "Allow",
          "Action": [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ],
          "Resource": "arn:aws:logs:*:*:*"
        }
      ]
    }
    ```

#### Step 3.4: Deploy the Chalice Backend

Ensure your Chalice virtual environment is active and you are in the chalice-todo-backend directory.

```bash
chalice deploy
```

After successful deployment, Chalice will output several pieces of information, including the Rest API URL. Copy this URL (e.g., https://xxxxxxxxx.execute-api.your-region.amazonaws.com/api/). You will need this for the Streamlit frontend. You can also retrieve it later using chalice url.

#### Step 3.4: Test deployment

After you run chalice deploy, there are several ways to verify that your deployment was successful and your AWS Chalice application is working correctly in the cloud:

1. Examine the chalice deploy Output:
   - No Errors: The most basic check is to ensure the chalice deploy command completed without any error messages in your terminal.
   - Rest API URL: Chalice will print out the resources it deployed. Crucially, it will display the Rest API URL. It will look something like https://ab12cd34ef.execute-api.your-region.amazonaws.com/api/. The presence of this URL is a strong indicator that the API Gateway and Lambda function were set up. Note this URL down.
2. Test API Endpoints Directly:
   This is the most direct way to verify the backend functionality. You can use tools like curl (from your terminal), Postman, Insomnia, or even your web browser for simple GET requests

   - Get the API Base URL: Use the URL from the chalice deploy output or run chalice url in your project directory (with the virtual environment activated). Let's say it's https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/api.

   - Test the root endpoint (if you have one):

   ```bash
   curl https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/api/
   ```

   This should return: {"message": "Welcome to the Chalice To-Do List API!"}

3. Check the AWS Management Console:

   - API Gateway:

     - Navigate to the API Gateway service.
     - Find your API (e.g., chalice-todo-backend).
     - Check its "Stages" (e.g., api).
     - Verify that your routes (/, /tasks, /tasks/{taskId}) and their methods (GET, POST, PUT, DELETE) are present and \* correctly integrated with your Lambda function. You can even use the "Test" feature within API Gateway to invoke methods.

       <img src="images/API_gateway.png" width="75%" style="display: block; margin: 0 auto">

   - AWS Lambda:

     - Go to the Lambda service.
     - Find your function (e.g., chalice-todo-backend-dev).
     - Check its configuration (runtime, handler, memory, timeout).
     - Look at the "Monitor" tab for recent invocations, errors, and duration after you've sent some test requests.

       <img src="images/lambda.png" width="75%" style="display: block; margin: 0 auto">

   - IAM:
     Go to the IAM service -> Roles.
     Find the execution role created by Chalice (e.g., chalice-todo-backend-dev-lambda_role).
     Verify its attached policies allow access to DynamoDB (ChaliceTodoListTable) and CloudWatch Logs, as defined in your .chalice/policy-dev.json (if you used a custom policy).

   <img src="images/IAM.png" width="75%" style="display: block; margin: 0 auto">

[Back to top](#)

### Step 4: Create frontend with Streamlit

#### Step 4.1: Set Up the Streamlit Project

Navigate back to your main project directory (todo_app_project) and create a directory for the Streamlit frontend and navigate into it:

```bash
mkdir streamlit-frontend
cd streamlit-frontend
```

Create and activate a separate virtual environment for the Streamlit app:

```bash
python3 -m venv streamlit-env
source streamlit-env/bin/activate  # On macOS/Linux
# .\streamlit-env\Scripts\activate   # On Windows
```

Install Streamlit and the requests library (for making HTTP calls):

```bash
pip install streamlit requests
```

#### Step 4.2: Write the Streamlit application code (todo_streamlit_app.py)

Create a file named todo_streamlit_app.py in the streamlit-frontend directory and add the following code.

Important: Find the line USER_DEPLOYED_API_BASE_URL_DEFAULT = "YOUR_CHALICE_API_BASE_URL_HERE" and replace "YOUR_CHALICE_API_BASE_URL_HERE" with the actual Rest API URL (base URL) you copied after deploying your Chalice app (e.g., https://xxxxxxxxx.execute-api.your-region.amazonaws.com/api – the /tasks part will be appended by the code).

```python
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Cloud To-Do List", layout="wide")
st.title("☁️ My Cloud To-Do List")
st.caption("Powered by AWS Chalice & Streamlit")


# --- Configuration ---
# User's actual deployed API endpoint that should preferably end with /tasks,
# or be the base /api path (the code below will try to append /tasks if it's not there).
USER_DEPLOYED_API_URL_DEFAULT = (
    "https://xxxxxxxxx.execute-api.your-region.amazonaws.com/api/tasks"
)

# This variable will hold the string value from the text_input
chalice_api_url_from_user = st.text_input(
    "Enter your Chalice API URL (base path or specific /tasks endpoint):",  # Corrected Label
    USER_DEPLOYED_API_URL_DEFAULT,  # User's default
)

# TASK_ENDPOINT will be the URL used for requests, ensuring it points to the /tasks resource.
TASK_ENDPOINT = ""  # Initialize
if chalice_api_url_from_user:
    # Normalize by removing trailing slash before checking/appending
    base_url_for_logic = chalice_api_url_from_user.strip("/")
    if base_url_for_logic.endswith("/tasks"):
        TASK_ENDPOINT = base_url_for_logic
    else:
        TASK_ENDPOINT = base_url_for_logic + "/tasks"
else:
    # This state will be caught by is_api_configured()
    pass


# --- Helper Functions to Interact with Backend ---
def is_api_configured():
    """Checks if the API endpoint seems minimally configured."""
    if (
        not TASK_ENDPOINT or "execute-api" not in TASK_ENDPOINT
    ):  # Basic check for AWS API Gateway URL
        st.sidebar.warning(
            "Please enter a valid Chalice API URL above to enable app functionality."
        )
        return False
    return True


def get_all_tasks():
    if not is_api_configured():
        return []
    try:
        response = requests.get(TASK_ENDPOINT)
        response.raise_for_status()
        # Assuming Chalice returns {'tasks': [...]}
        return response.json().get("tasks", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching tasks: {e}")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred while fetching tasks: {e}")
        return []



def update_existing_task(task_id, title=None, due_date=None, completed=None):
    if not is_api_configured():
        st.error("API URL not configured. Cannot update task.")
        return None

    payload = {}
    if (
        title is not None
    ):  # Only add if not None (Streamlit inputs might send empty strings for text)
        payload["title"] = title
    if due_date is not None:
        payload["dueDate"] = due_date
    if completed is not None:
        payload["completed"] = completed

    # --- Add this for debugging ---
    st.write("--- Streamlit: update_existing_task ---")
    st.write(f"Task ID: {task_id}")
    st.write(f"Payload being sent: {payload}")
    st.write(f"Attempting to PUT to: {TASK_ENDPOINT}/{task_id}")
    st.write("--- End Streamlit Debug ---")
    # --- End debugging ---

    if not payload:  # No actual changes were passed other than potentially None values
        st.warning(
            "No actual changes to update (e.g., title wasn't changed or was cleared)."
        )
        if not completed is None:  # If only 'completed' was changed, proceed
            pass  # allow just completed status to change
        else:
            pass

    if not payload:
        st.warning("No changes detected to update.")
        return None  # Or just return the original task if no changes.

    try:
        response = requests.put(f"{TASK_ENDPOINT}/{task_id}", json=payload)
        response.raise_for_status()
        updated_task_data = response.json().get("task", {})
        updated_title = updated_task_data.get("title", task_id)
        st.success(f"Task '{updated_title}' updated successfully!")
        return updated_task_data
    except requests.exceptions.RequestException as e:
        error_detail = ""
        try:
            error_detail = response.json().get(
                "Message", response.json().get("message", response.text)
            )
        except:
            error_detail = (
                response.text
                if "response" in locals() and hasattr(response, "text")
                else "No additional details."
            )
        st.error(f"Error updating task: {e} - Details: {error_detail}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while updating task: {e}")
        return None


def add_new_task(title, due_date):
    if not is_api_configured():
        st.sidebar.error("API URL not configured. Cannot add task.")
        return None
    payload = {"title": title, "dueDate": due_date}
    try:
        response = requests.post(TASK_ENDPOINT, json=payload)

        # --- BEGIN DEBUGGING ---
        st.write("--- Add Task Debug Info (Frontend) ---")
        st.write(f"Request URL: POST {TASK_ENDPOINT}")
        st.write(f"Request Payload: {payload}")
        st.write(f"Response Status Code: {response.status_code}")
        st.write(f"Response Headers: {response.headers}")
        try:
            parsed_json_response = response.json()
            st.write(f"Response Parsed JSON Type: {type(parsed_json_response)}")
            st.write(f"Response Parsed JSON Content: {parsed_json_response}")
        except requests.exceptions.JSONDecodeError as json_err:
            st.error(f"Response Failed to parse as JSON: {json_err}")
            st.write(f"Response Raw Text: {response.text}")
            st.error(
                f"Error adding task: Backend response was not valid JSON. Raw text: {response.text}"
            )
            return None  # Exit early if not valid JSON
        st.write("--- End Add Task Debug Info (Frontend) ---")
        # --- END DEBUGGING ---

        response.raise_for_status()  # Check for HTTP errors (4xx or 5xx)

        # Use the parsed_json_response from the debugging block
        # This is the line that was likely causing the error if parsed_json_response is a list
        added_task_data = parsed_json_response.get(
            "task", {}
        )  # This line will error if parsed_json_response is a list
        added_title = added_task_data.get("title", title)

        st.success(f"Task '{added_title}' added successfully!")
        return added_task_data
    except requests.exceptions.RequestException as e:
        # ... (rest of your error handling) ...
        error_detail = ""
        try:
            error_detail = response.json().get(
                "Message", response.json().get("message", response.text)
            )
        except:
            error_detail = (
                response.text
                if "response" in locals() and hasattr(response, "text")
                else "No additional details."
            )
        st.error(f"Error adding task (HTTP Error): {e} - Details: {error_detail}")
        return None
    except AttributeError as ae:
        st.error(
            f"An unexpected error occurred while processing the response from adding a task (AttributeError): {ae}"
        )
        st.error(
            "This usually means the backend sent data in an unexpected format (e.g., a list where a dictionary was expected)."
        )
        st.error(
            "Please check the debug output above if available, and your Chalice backend logs."
        )
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while adding task: {e}")
        return None


def delete_existing_task(task_id):
    if not is_api_configured():
        return None
    try:
        # TASK_ENDPOINT is like ".../tasks", so we append "/{task_id}"
        response = requests.delete(f"{TASK_ENDPOINT}/{task_id}")
        response.raise_for_status()
        # Chalice delete returns a message like {'message': "Task 'id' deleted successfully."}
        st.success(
            response.json().get("message", f"Task '{task_id}' deleted successfully!")
        )
        return True
    except requests.exceptions.RequestException as e:
        error_detail = ""
        try:
            error_detail = response.json().get(
                "Message", response.json().get("message", response.text)
            )
        except:
            error_detail = (
                response.text
                if "response" in locals() and hasattr(response, "text")
                else "No additional details."
            )
        st.error(f"Error deleting task: {e} - Details: {error_detail}")
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred while deleting task: {e}")
        return False


# --- Streamlit UI Layout ---

# Initialize session state for editing if it doesn't exist
# Put this near the top of your script, after imports but before UI elements generally
if "editing_task_id" not in st.session_state:
    st.session_state.editing_task_id = (
        None  # Will store the ID of the task being edited, or None
    )

# --- Sidebar for adding new tasks ---
# (Your sidebar code remains the same)
with st.sidebar:
    st.header("➕ Add New Task")
    with st.form("new_task_form", clear_on_submit=True):
        new_title = st.text_input("Title", key="new_title_input")
        new_due_date_val = st.date_input(
            "Due Date", value=datetime.today(), key="new_due_date_input"
        )
        submitted = st.form_submit_button("Add Task")

        if submitted:
            if not is_api_configured():
                # Warning shown by is_api_configured or individual functions
                pass
            elif new_title and new_due_date_val:
                if add_new_task(new_title, new_due_date_val.strftime("%Y-%m-%d")):
                    st.session_state.editing_task_id = (
                        None  # Close any open editor after adding
                    )
                    st.rerun()
            else:
                st.warning("Please provide both title and due date.")


# --- Main area for displaying tasks ---
if not is_api_configured():
    st.warning(
        "Please enter your Chalice API URL in the text input above to load and manage tasks."
    )
else:
    tasks = get_all_tasks()

    if not tasks:
        st.info("No tasks yet, or failed to load. Add one from the sidebar!")
    else:
        st.subheader("Your Tasks:")

        pending_tasks = [t for t in tasks if not t.get("completed", False)]
        completed_tasks = [t for t in tasks if t.get("completed", False)]

        if pending_tasks:
            st.markdown("---")
            st.markdown("### ⏳ Pending")
            for task in pending_tasks:
                task_id = task.get("taskId")
                # Unique prefix for keys based on task ID
                unique_key_prefix = f"pending_{task_id}"

                col1, col2, col3, col4 = st.columns([0.05, 0.4, 0.25, 0.3])

                # --- Column 1: Checkbox ---
                with col1:
                    is_checked_by_user = st.checkbox(
                        "", value=False, key=f"{unique_key_prefix}_check"
                    )
                    if is_checked_by_user:
                        # If completing a task that was being edited, close the editor
                        if st.session_state.editing_task_id == task_id:
                            st.session_state.editing_task_id = None
                        update_existing_task(task_id, completed=True)
                        st.rerun()

                # --- Column 2: Title and Date ---
                with col2:
                    st.markdown(f"**{task.get('title', 'N/A')}**")
                    st.caption(f"Due: {task.get('dueDate', 'N/A')}")

                # --- Column 3: Edit Button ---
                with col3:
                    # Edit button now just sets the session state flag
                    if st.button("Edit", key=f"{unique_key_prefix}_edit_action"):
                        st.session_state.editing_task_id = (
                            task_id  # Set which task to edit
                        )
                        st.rerun()  # Rerun to display the editor

                # --- Column 4: Delete Button ---
                with col4:
                    if st.button(
                        "Delete 🗑️", key=f"{unique_key_prefix}_del", type="secondary"
                    ):
                        # If deleting a task that was being edited, close the editor
                        if st.session_state.editing_task_id == task_id:
                            st.session_state.editing_task_id = None
                        if delete_existing_task(task_id):
                            st.rerun()

                # --- Conditionally Display Edit Form based on Session State ---
                if st.session_state.editing_task_id == task_id:
                    # Use an expander or just draw the form directly
                    with st.expander("✏️ Edit Task Details", expanded=True):
                        # Use st.form for the edit inputs and save button
                        with st.form(key=f"{unique_key_prefix}_edit_form"):
                            edit_title = st.text_input(
                                "New Title",
                                value=task.get("title"),  # Pre-fill with current title
                                key=f"{unique_key_prefix}_edit_title_input",
                            )
                            current_due_date_str = task.get("dueDate")
                            current_due_date_obj = (
                                datetime.strptime(current_due_date_str, "%Y-%m-%d")
                                if current_due_date_str
                                else datetime.today()
                            )
                            edit_due_date = st.date_input(
                                "New Due Date",
                                value=current_due_date_obj,  # Pre-fill with current date
                                key=f"{unique_key_prefix}_edit_date_input",
                            )

                            # The button inside the form triggers the form submission
                            save_submitted = st.form_submit_button("Save Changes")

                            if save_submitted:
                                st.write(
                                    f"--- Save Changes Submitted for task {task_id}! ---"
                                )  # Debug
                                success = update_existing_task(
                                    task_id,
                                    title=edit_title,  # Use current value from input
                                    due_date=edit_due_date.strftime(
                                        "%Y-%m-%d"
                                    ),  # Use current value from input
                                )
                                if (
                                    success
                                ):  # update_existing_task returns the updated task dict on success, None on failure
                                    st.session_state.editing_task_id = (
                                        None  # Close the editor
                                    )
                                    st.rerun()  # Refresh list
                                # Error messages are handled within update_existing_task

                        # Add a separate "Cancel" button outside the form
                        if st.button(
                            "Cancel Edit", key=f"{unique_key_prefix}_cancel_edit"
                        ):
                            st.session_state.editing_task_id = (
                                None  # Clear the editing flag
                            )
                            st.rerun()  # Rerun to hide the editor

                st.markdown("---")  # Separator after each task item / editor

        else:
            # Only show this if the API is configured but no tasks are pending
            if is_api_configured():
                st.info("No pending tasks!")

        # --- Completed Tasks Section ---
        # (Your code for completed tasks remains the same)
        if completed_tasks:
            st.markdown("---")
            st.markdown("### ✅ Completed")
            for task in completed_tasks:
                # ... (display completed tasks - no edit needed here typically) ...
                task_id = task.get("taskId")
                unique_key_prefix = f"completed_{task_id}"

                col1, col2, col3 = st.columns([0.05, 0.65, 0.3])
                with col1:
                    is_still_checked = st.checkbox(
                        "", value=True, key=f"{unique_key_prefix}_check"
                    )
                    if not is_still_checked:
                        # If unchecking a task that was being edited (unlikely but possible), close editor
                        if st.session_state.editing_task_id == task_id:
                            st.session_state.editing_task_id = None
                        update_existing_task(task_id, completed=False)
                        st.rerun()
                with col2:
                    st.markdown(f"~~{task.get('title', 'N/A')}~~")
                    st.caption(f"Completed (Due: {task.get('dueDate', 'N/A')})")
                with col3:
                    if st.button(
                        "Delete 🗑️", key=f"{unique_key_prefix}_del", type="secondary"
                    ):
                        # If deleting a task that was being edited (unlikely but possible), close editor
                        if st.session_state.editing_task_id == task_id:
                            st.session_state.editing_task_id = None
                        if delete_existing_task(task_id):
                            st.rerun()
                st.markdown("---")

        # If tasks list is empty overall (and API was configured)
        elif not tasks and is_api_configured():
            st.info("No tasks found. Add one from the sidebar!")
```

#### Step 4.3: Define Dependencies (requirements.txt for frontend)

Create a file requirements.txt in your streamlit-frontend directory with the following content:

```
streamlit
requests
```

#### Step 4.4: Run Streamlit Locally (for test purpose before deployment)

1. Ensure your Streamlit virtual environment is active and you are in the streamlit-frontend directory.
2. Run the app:
   ```bash
   streamlit run todo_streamlit_app.py
   ```
3. Your browser should open the app. Important: Paste your deployed Chalice API Base URL (e.g., https://xxxxxxxxx.execute-api.your-region.amazonaws.com/api – note, this is the base URL, the /tasks part will be appended by the Streamlit code) into the text input field at the top of the Streamlit app.
4. Test all functionalities: adding, viewing, editing, completing, and deleting tasks. Use any debug information printed in the Streamlit app and the CloudWatch Logs for your Chalice backend to troubleshoot.

[Back to top](#)

### Step 5: Deploying the Streamlit frontend

To share your Streamlit app, you can deploy it using Streamlit Community Cloud. This requires your app code to be in a public GitHub repository.

#### Step 5.1: Create a GitHub Repository

1. Go to GitHub and create a new public repository (e.g., my-todo-app-streamlit-frontend).
2. Navigate to your local streamlit-frontend directory in your terminal.
3. Initialize a Git repository, add your files, commit, and push them to your new GitHub repository:

```bash
# Make sure you are in the streamlit-frontend directory
git init
git add todo_streamlit_app.py requirements.txt
git commit -m "Initial version of Streamlit to-do app frontend"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

#### Step 5.2: Deploy to Streamlit Community Cloud

1. Go to share.streamlit.io and sign in with your GitHub account.
2. Click "New app" (or "Deploy an app" if we have deployed before).
3. Choose "Deploy from existing repo".
4. Select the GitHub repository you just created.
5. Branch: main (or our default branch).
6. Main file path: todo_streamlit_app.py.
7. Click "Deploy!".

[Back to top](#)

### Final result

To visualize and test the application, you can go on your [Streamlit account](https://share.streamlit.io/) and find your application listed.

<img src="images/App_profil.png" width="80%" style="display: block; margin: 0 auto">

Select your application to start it

<img src="images/App_landing_2.png" width="80%" style="display: block; margin: 0 auto">

Each item is imported in DynamoDB:
<img src="images/dynamo.png" width="80%" style="display: block; margin: 0 auto">

## Conclusion

On the frontend, we have built an interactive and user-friendly web interface using **Streamlit**, allowing users to manage their tasks seamlessly. This frontend communicates with the Chalice backend via HTTP requests and demonstrates how to manage UI state and user interactions purely within Python. Finally, we learned how to deploy both components: the backend to the AWS cloud and the frontend to Streamlit Community Cloud, making our application accessible.

**Key Learnings from This Project:**

- **Serverless Backend Development (AWS Chalice & Lambda):**

  - We have experienced the power of serverless architecture, focusing on writing application logic (Python functions) without managing underlying server infrastructure.
  - We learned how to define RESTful API endpoints (`@app.route`) with Chalice, map them to Lambda functions, and handle HTTP methods (`GET`, `POST`, `PUT`, `DELETE`).
  - We gained hands-on experience interacting with DynamoDB from Lambda using the `boto3` SDK for Python, performing operations like `put_item`, `scan`, `get_item`, `update_item`, and `delete_item`.
  - We understood the importance of IAM permissions and how to configure policies (`policy-dev.json`) to grant our Lambda functions the necessary access to other AWS services securely.
  - We have seen Chalice's deployment process (`chalice deploy`) and how it automates the creation and configuration of Lambda and API Gateway resources.
  - We have touched upon debugging serverless applications by inspecting CloudWatch Logs to understand backend behavior and troubleshoot errors.

- **Interactive Frontend Development (Streamlit):**

  - We discovered how to build a complete web user interface using only Python, leveraging Streamlit's intuitive API.
  - You utilized various Streamlit widgets (`st.text_input`, `st.date_input`, `st.button`, `st.checkbox`, `st.form`, `st.expander`, `st.columns`) to create an interactive user experience.
  - We learned how a frontend application makes HTTP API calls (using the `requests` library) to a backend service to fetch and manipulate data.
  - We practiced deploying a Streamlit application to a public platform (Streamlit Community Cloud via GitHub), making our work shareable. We made the choice to deploy our application on Streamlit Community to display the possibilities but the application can be deplay within AWS.

  - Streamlit proved to be an excellent choice for the frontend in this application for several reasons:

    1.  **Python-Native Development:** It allowed us to build the entire user interface using Python, the same language used for the backend. This is a huge advantage for developers who are primarily Python-focused, as it removes the need to learn and manage complex JavaScript frameworks, HTML, and CSS for building a functional UI.
    2.  **Speed of Development and Iteration:** Streamlit's "write a script, see it update live" model allows for incredibly fast prototyping and iteration. We were able to build interactive elements, forms, and data displays with minimal code.
    3.  **Simplified State Management:** While complex state requires `st.session_state` (as we implemented for the edit functionality), basic widget interactions are handled almost transparently by Streamlit, reducing boilerplate.
    4.  **Ease of Integration:** Making API calls with the `requests` library and then displaying the results or updating the UI based on backend responses is straightforward within a Streamlit script.
    5.  **Focus on Functionality:** Streamlit abstracts away many of the underlying web development complexities, allowing us to focus on the application's logic and user experience rather than on web server configurations or intricate frontend build processes.
    6.  **Effortless Sharing (with Streamlit Community Cloud):** Deploying a public version of our app directly from a GitHub repository is incredibly simple, making it easy to showcase our work or share tools.

- **NoSQL Database Interaction (Amazon DynamoDB):**

  - We got a practical introduction to using a serverless NoSQL database, understanding its key-value nature with a flexible schema.
  - We learned how to define a simple data model for tasks and interact with it using primary keys (`taskId`).

- **Full-Stack Integration & Cloud Computing Principles:**
  - This project is a microcosm of modern **cloud computing**. We have directly worked with core cloud concepts:
    - **Serverless Computing:** The entire backend (Lambda, API Gateway, DynamoDB) operates without us managing any physical or virtual servers. This leads to reduced operational burden, automatic scaling based on demand, and a pay-per-use cost model, making it highly efficient.
    - **Microservices Architecture (Conceptual):** Our Chalice backend acts as a self-contained microservice dedicated to managing to-do tasks. This API-first approach allows for decoupling the frontend and backend, enabling them to be developed, deployed, and scaled independently.
    - **API-Driven Development:** The frontend and backend communicate exclusively through a well-defined API. This is a standard pattern for building scalable and maintainable applications.
    - **Scalability and High Availability:** By using AWS managed services like Lambda, API Gateway, and DynamoDB, our application inherits their inherent capabilities for scaling to handle load and maintaining high availability without manual intervention.
    - **Infrastructure as Code (Implicitly):** Chalice automates the provisioning of the necessary AWS infrastructure (Lambda functions, API Gateway configurations, IAM roles) based on our Python code and configuration files. This aligns with IaC principles, making our deployments repeatable and versionable.

In conclusion, this project has equipped us with valuable skills in building and deploying serverless applications using a powerful combination of AWS services and Python frameworks. We have seen how to separate concerns between a backend API and a frontend UI, and how to leverage the strengths of each technology to create a complete application. The principles and tools we have used are highly relevant in today's cloud-native development landscape.

[Back to top](#)
