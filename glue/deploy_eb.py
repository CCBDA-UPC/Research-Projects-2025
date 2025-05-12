"""
This script deploys the application to AWS Elastic Beanstalk.
It does the following:
1. Creates an ECR repository for the application with the name provided in the arguments.
2. Logs in to the ECR registry.
3. Builds the Docker image for the application using the Dockerfile in the current directory, and tags it  with the ECR
    repository URI.
5. Pushes the Docker image to the ECR repository.
6. Creates an Elastic Beanstalk application.
7. Creates an Elastic Beanstalk environment for the application.
8. Deploys the Docker image to the Elastic Beanstalk environment.
9. Waits for the environment to be ready.
10. Prints the URL of the deployed application.
"""

import argparse
import contextlib
import json
import os
import time
from tempfile import TemporaryDirectory

import boto3
import botocore
import dotenv
import yaml


def main(ecr_name: str, eb_app_name: str, eb_env_name: str, eb_bucket: str, version: str):
    """
    Deploy the application to AWS Elastic Beanstalk.
    Args:
        ecr_name (str): The name of the ECR repository.
        eb_app_name (str): The name of the Elastic Beanstalk application.
        eb_env_name (str): The name of the Elastic Beanstalk environment.
    """
    dotenv_path = os.path.join(".", "src", ".env")
    if os.path.exists(dotenv_path):
        dotenv_vars = dotenv.dotenv_values(dotenv_path)
    else:
        print(f"Error: No .env file found at {dotenv_path}")
        exit(1)

    # Create an ECR client
    ecr_client = boto3.client("ecr")

    # Create an ECR repository
    try:
        response = ecr_client.create_repository(repositoryName=ecr_name)
        repo_uri = response["repository"]["repositoryUri"]
        print(f"Created ECR repository: {repo_uri}")
    except ecr_client.exceptions.RepositoryAlreadyExistsException:
        print(f"ECR repository {ecr_name} already exists.")
        try:
            response = ecr_client.describe_repositories(repositoryNames=[ecr_name])
            repo_uri = response["repositories"][0]["repositoryUri"]
            print(f"Using existing ECR repository: {repo_uri}")
        except Exception as e:
            print(f"Error describing ECR repository: {e}")
            exit(1)

    # Log in to the ECR registry
    ecr_login_command = (
        f"aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin {repo_uri}"
    )
    print(f"Logging in to ECR registry: {ecr_login_command}")
    exit_value = os.system(ecr_login_command)
    if exit_value != 0:
        print(f"Error logging in to ECR registry: {exit_value}")
        exit(1)

    # Build the Docker image
    with contextlib.chdir("src"):
        docker_build_command = f"docker build -t {repo_uri}:{version} ."
        print(f"Building Docker image: {docker_build_command}")
        exit_value = os.system(docker_build_command)
        if exit_value != 0:
            print(f"Error building Docker image: {exit_value}")
            exit(1)

    # Push the Docker image to the ECR repository
    docker_push_command = f"docker push {repo_uri}:{version}"
    print(f"Pushing Docker image to ECR: {docker_push_command}")
    exit_value = os.system(docker_push_command)
    if exit_value != 0:
        print(f"Error pushing Docker image to ECR: {exit_value}")
        exit(1)

    # Create the S3 bucket for the application version
    s3_client = boto3.client("s3")
    try:
        response = s3_client.create_bucket(Bucket=eb_bucket)
        print(f"Created S3 bucket: {eb_bucket}")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"S3 bucket {eb_bucket} already exists.")
        try:
            response = s3_client.head_bucket(Bucket=eb_bucket)
            print(f"Using existing S3 bucket: {eb_bucket}")
        except Exception as e:
            print(f"Error describing S3 bucket: {e}")
            exit(1)
    except Exception as e:
        print(f"Error creating S3 bucket: {e}")
        exit(1)

    # Create a new zip file with the application definition (Dockerrun.aws.json)
    with TemporaryDirectory() as temp_dir, contextlib.chdir(temp_dir):
        with open("Dockerrun.aws.json", "w") as f:
            json.dump(
                {
                    "AWSEBDockerrunVersion": "1",
                    "Image": {"Name": f"{repo_uri}:{version}", "Update": "true"},
                    "Ports": [{"ContainerPort": 8000}],
                },
                f,
                indent=4,
            )
        # Zip the contents of the temporary directory
        exit_value = os.system(f"zip -r deployment.zip Dockerrun.aws.json")
        if exit_value != 0:
            print(f"Error creating zip file: {exit_value}")
            exit(1)

        # Upload the zip file to S3
        try:
            s3_client.upload_file(
                Filename="deployment.zip",
                Bucket=eb_bucket,
                Key=f"{eb_app_name}/{version}/deployment.zip",
            )
            print(f"Uploaded deployment package to S3: s3://{eb_bucket}/{eb_app_name}/{version}/deployment.zip")
        except Exception as e:
            print(f"Error uploading deployment package to S3: {e}")
            exit(1)

    # Create an Elastic Beanstalk client
    eb_client = boto3.client("elasticbeanstalk")

    # Create an Elastic Beanstalk application
    try:
        response = eb_client.create_application(ApplicationName=eb_app_name)
        print(f"Created Elastic Beanstalk application: {eb_app_name}")
    except eb_client.exceptions.ClientError as e:
        print(f"Elastic Beanstalk application {eb_app_name} already exists.")
        try:
            response = eb_client.describe_applications(ApplicationNames=[eb_app_name])
            print(f"Using existing Elastic Beanstalk application: {eb_app_name}")
        except Exception as e:
            print(f"Error describing Elastic Beanstalk application: {e}")
            exit(1)

    # Create a new application version
    try:
        response = eb_client.create_application_version(
            ApplicationName=eb_app_name,
            VersionLabel=version,
            SourceBundle={
                "S3Bucket": eb_bucket,
                "S3Key": f"{eb_app_name}/{version}/deployment.zip",
            },
            Process=True,
        )
        print(f"Created Elastic Beanstalk application version: {version}")
    except botocore.exceptions.ClientError as e:
        print(f"Elastic Beanstalk application version {version} already exists.")
        try:
            response = eb_client.describe_application_versions(ApplicationName=eb_app_name, VersionLabels=[version])
            print(f"Using existing Elastic Beanstalk application version: {version}")
        except Exception as e:
            print(f"Error describing Elastic Beanstalk application version: {e}")
            exit(1)
    except Exception as e:
        print(f"Error creating Elastic Beanstalk application version: {e}")
        exit(1)

    # Wait for the application version to be ready
    while True:
        response = eb_client.describe_application_versions(ApplicationName=eb_app_name, VersionLabels=[version])
        status = None
        for v in response["ApplicationVersions"]:
            if version == v["VersionLabel"]:
                status = v["Status"]
                break
        if status is None:
            print(f"Error: Application version {version} not found.")
            exit(1)
        if status == "PROCESSED":
            break
        elif status == "PROCESSING":
            print(f"Waiting for application version {version} to be ready...")
            time.sleep(10)
        else:
            print(f"Application version {version} failed to create.")
            exit(1)

    print(f"Application version {version} is ready.")

    with open("eb_options.yaml", "r") as f:
        eb_config = yaml.safe_load(f)
        eb_options = []
        for namespace, configs in eb_config.items():
            for key, value in configs.items():
                eb_options.append({"Namespace": namespace, "OptionName": key, "Value": value})

    for key, value in dotenv_vars.items():
        eb_options.append(
            {"Namespace": "aws:elasticbeanstalk:application:environment", "OptionName": key, "Value": value}
        )

    try:
        response = eb_client.create_environment(
            ApplicationName=eb_app_name,
            EnvironmentName=eb_env_name,
            VersionLabel=version,
            SolutionStackName="64bit Amazon Linux 2023 v4.5.1 running Docker",
            OptionSettings=eb_options,
        )
        print(f"Created Elastic Beanstalk environment: {eb_env_name}")
    except botocore.exceptions.ClientError as e:
        print(f"Elastic Beanstalk environment {eb_env_name} already exists.")
        try:
            response = eb_client.describe_environments(EnvironmentNames=[eb_env_name])
            print(f"Using existing Elastic Beanstalk environment: {eb_env_name}")
        except Exception as e:
            print(f"Error describing Elastic Beanstalk environment: {e}")
            exit(1)
    except Exception as e:
        print(f"Error creating Elastic Beanstalk environment: {e}")
        exit(1)

    # Wait for the environment to be ready
    while True:
        response = eb_client.describe_environments(EnvironmentNames=[eb_env_name])
        status = None
        for env in response["Environments"]:
            if eb_env_name == env["EnvironmentName"]:
                status = env["Status"]
                break
        if status is None:
            print(f"Error: Environment {eb_env_name} not found.")
            exit(1)
        if status == "Ready":
            break
        elif status == "Launching":
            print(f"Waiting for environment {eb_env_name} to be ready...")
            time.sleep(10)
        else:
            print(f"Environment {eb_env_name} failed to create.")
            exit(1)
        print(f"Environment {eb_env_name} is {status}.")
    print(f"Environment {eb_env_name} is ready.")

    # Print the URL of the deployed application
    response = eb_client.describe_environments(EnvironmentNames=[eb_env_name])
    url = None
    for env in response["Environments"]:
        if eb_env_name == env["EnvironmentName"]:
            url = env["CNAME"]
            break
    if url is None:
        print(f"Error: Environment {eb_env_name} not found.")
        exit(1)

    # Update the environment variable 'DJANGO_ALLOWED_HOSTS' with the URL
    print(f"Updating environment variable 'DJANGO_ALLOWED_HOSTS' with value: {url}")
    eb_client.update_environment(
        EnvironmentName=eb_env_name,
        OptionSettings=[
            {
                "Namespace": "aws:elasticbeanstalk:application:environment",
                "OptionName": "DJANGO_ALLOWED_HOSTS",
                "Value": url,
            }
        ],
    )
    # Wait for the environment to be updated
    while True:
        response = eb_client.describe_environments(EnvironmentNames=[eb_env_name])
        status = None
        for env in response["Environments"]:
            if eb_env_name == env["EnvironmentName"]:
                status = env["Status"]
                break
        if status is None:
            print(f"Error: Environment {eb_env_name} not found.")
            exit(1)
        if status == "Ready":
            break
        elif status == "Updating":
            print(f"Waiting for environment {eb_env_name} to be updated...")
            time.sleep(10)
        else:
            print(f"Environment {eb_env_name} failed to update.")
            exit(1)
        print(f"Environment {eb_env_name} is {status}.")
    print(f"Environment {eb_env_name} is updated.")

    print(f"Application deployed at: http://{url}")
    # Clean up the Docker image
    os.system(f"docker rmi {repo_uri}:{version}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy the application to AWS Elastic Beanstalk.")
    parser.add_argument("--ecr-name", type=str, help="The name of the ECR repository.", required=True)
    parser.add_argument("--eb-app-name", type=str, help="The name of the Elastic Beanstalk application.", required=True)
    parser.add_argument("--eb-env-name", type=str, help="The name of the Elastic Beanstalk environment.", required=True)
    parser.add_argument("--eb-bucket", type=str, help="The name of the S3 bucket for the application.", required=True)
    parser.add_argument("--eb-version", type=str, help="The version of the Application.", required=True)
    args = parser.parse_args()

    main(args.ecr_name, args.eb_app_name, args.eb_env_name, args.eb_bucket, args.eb_version)
