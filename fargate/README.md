# AWS Fargate - Research Project 
# 1. Fully Understand AWS Fargate

## What is AWS Fargate?
**AWS Fargate** is a serverless compute engine provided by Amazon Web Services (AWS) that allows you to run containers without managing servers or clusters.  
You focus on developing and deploying your applications, while AWS automatically handles the provisioning, configuration, scaling, and management of the compute infrastructure.

> Simply put: You build your application, AWS Fargate runs it without you worrying about the servers.

![](../screenshots/1-what_AWS_fargate.png)

---

## How it works technically (basic architecture)
AWS Fargate integrates with two major container orchestration services:
- **Amazon ECS (Elastic Container Service)**: AWS's proprietary orchestration system.
- **Amazon EKS (Elastic Kubernetes Service)**: Managed Kubernetes service on AWS.

When using Fargate:
1. You define your container using an OCI-compliant image. (An OCI image is a standardised format for containers such as those built with Docker)
2. Specify resource requirements (vCPU and memory).
3. Set up networking and security policies.
4. Fargate runs each task (ECS) or pod (EKS) in an isolated environment without you provisioning servers.

Each task or pod has its **own runtime environment**, ensuring **strong security and isolation**.

---

## When and why it is used (main use cases)

**When to use Fargate:**
- When you want to run containerized applications without managing infrastructure.
- When automatic scalability is needed depending on application load.
- When application components must be strongly isolated.
- When you want to reduce time spent on server management.

**Main use cases:**
- **Web applications and APIs**: running scalable services without managing servers.
- **Microservices architectures**: easily deploying multiple isolated services.
- **Data processing**: batch or real-time data workflows.
- **AI/ML applications**: training or inference jobs in isolated, scalable environments.

---

## Differences compared to other container management methods (e.g., EC2, manually managed Kubernetes)

| Feature                        | AWS Fargate                                       | EC2 / Manually managed Kubernetes                   |
|:--------------------------------|:--------------------------------------------------|:----------------------------------------------------|
| **Server management**           | No management needed; serverless.                 | Requires provisioning and managing virtual machines. |
| **Scalability**                 | Automatic, managed by AWS.                        | Manual or script-based scaling configuration needed. |
| **Isolation**                   | Each task/pod runs in a dedicated environment.     | Requires advanced configurations for strong isolation. |
| **Cost model**                  | Pay only for CPU and memory used.                  | Pay for full EC2 instances, even if underutilized. |
| **Configuration effort**        | Minimal; focus on container and resource setup.    | High; detailed infrastructure configuration needed. |

---

## Limitations or disadvantages

### ⚠️ Limitations of AWS Fargate (with examples)

- **Limited support for some Kubernetes functionalities**: some advanced features may require additional configuration or are not available.  
  **Example**: DaemonSets, which run a copy of a pod on every node, are not supported in Fargate. Advanced CNI configurations or certain persistent storage plugins may also not work out of the box.

- **Higher costs for constant workloads**: in some cases, EC2 instances may be more cost-effective than Fargate for predictable, always-on tasks.  
  **Example**: If you're running a web server 24/7 with stable traffic, using a reserved EC2 instance can be significantly cheaper than using Fargate, which charges per vCPU and memory per second. Over time, this cost can exceed EC2’s.

- **Less control over the infrastructure**: compared to self-managed Kubernetes clusters or EC2 setups.  
  **Example**: You cannot select the underlying EC2 instance type, install system-level monitoring agents, or tune kernel parameters — since you don’t have access to the host.

- **Compatibility adjustments**: some legacy applications may require modifications to run properly on Fargate.  
  **Example**: Applications that write to the local file system or depend on background daemons (like cron jobs or OS-level services) might not run correctly without refactoring.

- **No support for GPUs**: currently, Fargate does not offer GPU capabilities for workloads needing heavy computational resources.  
  **Example**: Machine learning model training or real-time video processing should run on EC2 GPU instances (like `p3` or `g5`), which Fargate does not support.


# 2. Collect Community Feedback

## Overview

AWS Fargate has garnered diverse opinions within the developer community. While many appreciate its serverless approach to container management, others highlight certain limitations and challenges. Below is a synthesis of real-world user feedback from platforms like Reddit, Stack Overflow, and expert blogs.

## Positive Feedback

- **Simplified Operations**: Users commend Fargate for eliminating the need to manage EC2 instances, allowing developers to focus solely on application development.
  > "We had a really good experience with Fargate. It's like ECS with EC2 but easier."  
  — [Reddit user](https://www.reddit.com/r/aws/comments/1e54bl0/whats_yalls_experience_with_ecs_fargate/)

- **Enhanced Scalability**: Fargate's ability to automatically scale applications based on demand is frequently praised.
  > "Auto scaling is much, much easier on Fargate."  
  — [Reddit user](https://www.reddit.com/r/aws/comments/h09m21/anyone_switched_from_ecs_with_ec2_to_fargate_for/)

- **Improved Security**: The isolation provided by Fargate for each task enhances security, reducing the risk of cross-container vulnerabilities.

## Criticisms and Challenges
<!-- aws ecs run-task \
  --cluster your-cluster-name \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxxxxx],securityGroups=[sg-xxxxxxxx],assignPublicIp=ENABLED}" \
  --task-definition sample-fargateaws ecs run-task \
  --cluster your-cluster-name \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxxxxx],securityGroups=[sg-xxxxxxxx],assignPublicIp=ENABLED}" \
  --task-definition sample-fargateaws ecs run-task \
  --cluster your-cluster-name \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxxxxx],securityGroups=[sg-xxxxxxxx],assignPublicIp=ENABLED}" \
  --task-definition sample-fargate -->
- **Higher Costs**: Several users point out that Fargate can be more expensive than other solutions, especially for consistent, long-running workloads.
  > "AWS Fargate is costlier when compared with other services."  
  — [Iron.io Blog](https://blog.iron.io/aws-fargate-reviews/)

- **Limited Customization**: The abstraction that Fargate provides can sometimes limit the ability to fine-tune configurations, which some advanced users find restrictive.

- **Startup Latency**: Some developers have observed that container startup times in Fargate are longer compared to EC2, potentially impacting applications sensitive to latency.

## Community Consensus

While AWS Fargate offers significant advantages in terms of ease of use and scalability, it's essential to assess its fit based on specific application needs, workload patterns, and budget constraints. For stateless applications and microservices requiring rapid deployment without infrastructure management, Fargate is often an excellent choice. However, for applications demanding extensive customization or those with predictable, steady workloads, alternative solutions might be more cost-effective.

## Sources

- Reddit Discussion: [What's Y'alls Experience with ECS Fargate](https://www.reddit.com/r/aws/comments/1e54bl0/whats_yalls_experience_with_ecs_fargate/)
- Reddit Discussion: [Anyone switched from ECS with EC2 to Fargate for 24/7 workloads?](https://www.reddit.com/r/aws/comments/h09m21/anyone_switched_from_ecs_with_ec2_to_fargate_for/)
- Iron.io Blog: [AWS Fargate Reviews](https://blog.iron.io/aws-fargate-reviews/)

---

# Sources
- [AWS Fargate Official Overview](https://aws.amazon.com/fargate/?nc2=type_a)
- [AWS EKS and Fargate Documentation](https://docs.aws.amazon.com/it_it/eks/latest/userguide/fargate.html)

---

# 3.LAB - Part 1: Introduction to AWS Fargate.

## Table of Contents

0. [Prerequisites](#prerequisites)
1. [Step 1 – Create an ECS Cluster](#step-1--create-an-ecs-cluster)
2. [Step 2 – Create a Task Definition](#step-2--create-a-task-definition)
3. [Step 3 – Launch the Task and Link It to the Cluster](#step-3--launch-the-task-and-link-it-to-the-cluster)
4. [Step 4 – Access the Application](#step-4--access-the-application)
5. [Step 5 – Stop the Task](#step-5--stop-the-task)
6. [Step 6 – Run a Scalable ECS Service with 2 Tasks](#step-6--run-a-scalable-ecs-service-with-2-tasks)
7. [Step 7 – Clean Up Resources](#step-7--clean-up-resources)

## Prerequisites

This tutorial is designed for use within the **Machine Academy Learner Lab** environment. Most of the required infrastructure is already pre-provisioned for you.

Before starting, please make sure you:

- ✅ Have launched the **Learner Lab environment**
- ✅ Have access to the **provided AWS Console and CLI credentials**
- ✅ **A VPC with at least one public subnet**
- ✅ **A Security Group that allows inbound HTTP traffic** (port 80)
- ✅ Are working in the **us-east-1** region (unless instructed otherwise)
- ✅ Have verified that **AWS CLI is configured** (you can run `aws sts get-caller-identity` to confirm)


## Step 1 – Create an ECS Cluster

First of all we will create a AWS Elastic Container Service cluster. A cluster is the infrastructure an application runs on.

```bash
└─$ aws ecs create-cluster --cluster-name CCBDA-CLUSTER
```

 Sample output:

 ```
{
    "cluster": {
        "clusterArn": "arn:aws:ecs:us-east-1:<your_id>:cluster/CCBDA-CLUSTER",
        "clusterName": "CCBDA-CLUSTER",
        "status": "ACTIVE",
        "registeredContainerInstancesCount": 0,
        "runningTasksCount": 0,
        "pendingTasksCount": 0,
        "activeServicesCount": 0,
        "statistics": [],
        "tags": [],
        "settings": [
            {
                "name": "containerInsights",
                "value": "disabled"
            }
        ],
        "capacityProviders": [],
        "defaultCapacityProviderStrategy": []
    }
}
     
```

![](../screenshots/1-creation_cluster.png)

## Step 2 – Create a Task Definition

Once we create our cluster, we need to define the task that ECS will run.
We do this using a JSON file that describes a basic Apache web server container.

Create a file named task-definition.json with the following content:

Some important parts of the json are "image" that points to the image used for  the task definition, "cpu" and "memory" that indicate the power of the task and  "requiresCompatibilities" that indicate that it will be use Fargate.

```json

{
        "family": "sample-fargate",
        "networkMode": "awsvpc",
        "containerDefinitions": [
            {
                "name": "CCBDA-CLUSTER",
                "image": "public.ecr.aws/docker/library/httpd:latest",
                "portMappings": [
                    {
                        "containerPort": 80,
                        "hostPort": 80,
                        "protocol": "tcp"
                    }
                ],
                "essential": true,
                "entryPoint": [
                    "sh",
                    "-c"
                ],
                "command": [
               "echo '<!DOCTYPE html><html><head><title>CCBDA AWS FARGATE</title><style>body{font-family:sans-serif;background:#1e1e2f;color:#fff;text-align:center;padding-top:50px;}h1{font-size:2.5em;}p{color:#aaa;}</style></head><body><h1>CCBDA is Live on AWS Fargate!</h1><p>Served from Apache in a Docker container</p></body></html>' > /usr/local/apache2/htdocs/index.html && httpd-foreground"
            ]
            }
        ],
        "requiresCompatibilities": [
            "FARGATE"
        ],
        "cpu": "256",
        "memory": "512"
}

```

Once we put our json in a file we can create a task definition with its information:

```bash
└─$ aws ecs register-task-definition --cli-input-json file://your_file.json
```

Sample output:

```
{
    "taskDefinition": {
        "taskDefinitionArn": "arn:aws:ecs:us-east-1:<your_id>:task-definition/sample-fargate:3",
        "containerDefinitions": [
            {
                "name": "CCBDA-CLUSTER",
                "image": "public.ecr.aws/docker/library/httpd:latest",
                "cpu": 0,
                "portMappings": [
                    {
                        "containerPort": 80,
                        "hostPort": 80,
                        "protocol": "tcp"
                    }
                ],
                "essential": true,
                "entryPoint": [
                    "sh",
                    "-c"
                ],
                "command": [
                    "echo '<!DOCTYPE html><html><head><title>CCBDA AWS FARGATE</title><style>body{font-family:sans-serif;background:#1e1e2f;color:#fff;text-align:center;padding-top:50px;}h1{font-size:2.5em;}p{color:#aaa;}</style></head><body><h1>CCBDA on AWS Fargate!</h1><p>Served from Apache in a Docker container</p></body></html>' > /usr/local/apache2/htdocs/index.html && httpd-foreground"
                ],
                "environment": [],
                "mountPoints": [],
                "volumesFrom": [],
                "systemControls": []
            }
        ],
        "family": "sample-fargate",
        "networkMode": "awsvpc",
        "revision": 3,
        "volumes": [],
        "status": "ACTIVE",
        "requiresAttributes": [
            {
                "name": "com.amazonaws.ecs.capability.docker-remote-api.1.18"
            },
            {
                "name": "ecs.capability.task-eni"
            }
        ],
        "placementConstraints": [],
        "compatibilities": [
            "EC2",
            "FARGATE"
        ],
        "requiresCompatibilities": [
            "FARGATE"
        ],
        "cpu": "256",
        "memory": "512",
        "registeredAt": "2025-05-01T17:12:14.531000+02:00",
        "registeredBy": "arn:aws:sts::<your_id>:assumed-role/voclabs/user3866762=Xavier_L__pez_Manes"
    }
}
  
```

![](../screenshots/x-screenshot-1.png)

## Step 3 – Launch the Task and Link It to the Cluster

Now that the task is defined, we can run it inside the cluster as a standalone task. Just with a single command we can run as many individual tasks as we want.

```bash
└─$ aws ecs run-task \
  --cluster CCBDA-CLUSTER \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-XXXXX],securityGroups=[sg-XXXXXX],assignPublicIp=\"ENABLED\"}" \
  --task-definition sample-fargate
```

Sample output:

```
{
    "tasks": [
        {
            "attachments": [
                {
                    "id": "30380441-5dea-4ff8-bd81-274ac429bafb",
                    "type": "ElasticNetworkInterface",
                    "status": "PRECREATED",
                    "details": [
                        {
                            "name": "subnetId",
                            "value": "subnet-0f145b175a0e46cc5"
                        }
                    ]
                }
            ],
            "attributes": [
                {
                    "name": "ecs.cpu-architecture",
                    "value": "x86_64"
                }
            ],
            "availabilityZone": "us-east-1a",
            "clusterArn": "arn:aws:ecs:us-east-1:<your_id>:cluster/CCBDA-CLUSTER",
            "containers": [
                {
                    "containerArn": "arn:aws:ecs:us-east-1:<your_id>:container/CCBDA-CLUSTER/c3c73a9ebfc34598909bb55af7921522/788c1e73-986a-4077-a8b7-b66538b6098d",
                    "taskArn": "arn:aws:ecs:us-east-1:<your_id>:task/CCBDA-CLUSTER/c3c73a9ebfc34598909bb55af7921522",
                    "name": "CCBDA-CLUSTER",
                    "image": "public.ecr.aws/docker/library/httpd:latest",
                    "lastStatus": "PENDING",
                    "networkInterfaces": [],
                    "cpu": "0"
                }
            ],
            "cpu": "256",
            "createdAt": "2025-05-01T17:14:11.342000+02:00",
            "desiredStatus": "RUNNING",
            "enableExecuteCommand": false,
            "group": "family:sample-fargate",
            "lastStatus": "PROVISIONING",
            "launchType": "FARGATE",
            "memory": "512",
            "overrides": {
                "containerOverrides": [
                    {
                        "name": "CCBDA-CLUSTER"
                    }
                ],
                "inferenceAcceleratorOverrides": []
            },
            "platformVersion": "1.4.0",
            "platformFamily": "Linux",
            "tags": [],
            "taskArn": "arn:aws:ecs:us-east-1:<your_id>:task/CCBDA-CLUSTER/c3c73a9ebfc34598909bb55af7921522",
            "taskDefinitionArn": "arn:aws:ecs:us-east-1:<your_id>:task-definition/sample-fargate:5",
            "version": 1,
            "ephemeralStorage": {            }
            }
        ],
        "failures": []
    }

```
![](../screenshots/x-screenshot-2.png)

![](../screenshots/x-screenshot-3.png)

## Step 4 – Access the Application

Once your task is running on AWS Fargate, you can access the deployed web application via the public IP address assigned to the task's network interface.

### 1. Find the Task ID

First, list your running tasks:

```bash
aws ecs list-tasks --cluster CCBDA-CLUSTER
```

Then describe the task to retrieve networking details:

```bash
aws ecs describe-tasks \
  --cluster CCBDA-CLUSTER \
  --tasks <your-task-id>
```

In the output, locate the `attachments -> details` section. Look for the value of `networkInterfaceId`.

### 2. Get the Public IP Address

Go to the **EC2 Console**, navigate to **Network Interfaces**, and search for the network interface ID retrieved earlier. The **Public IPv4 address** shown there is the one used to access your application.

Alternatively, you can use the AWS CLI to get it:

```bash
aws ec2 describe-network-interfaces \
  --network-interface-ids <eni-id> \
  --query 'NetworkInterfaces[0].Association.PublicIp' \
  --output text
```

### 3. Open the Application

Open your browser and go to:

```
http://<public-ip>
```

You should see the custom Apache welcome page served from your container.

![](../screenshots/x-screenshot-5.png)

### Security Group Configuration

If the page doesn’t load:

- Ensure the **Security Group** used by the task allows **inbound traffic on port 80 (HTTP)**.
- You can modify inbound rules in the **EC2 > Security Groups** section of the AWS Console.


## Step 5 – Stop the Task

To stop a running task, you need its Task ID.

```bash
└─$ aws ecs stop-task \
  --cluster CCBDA-CLUSTER \
  --task <your-task-id>
```

![](../screenshots/3-stop_task.png)

```bash
└─$ aws ecs list-task-definitions
{
    "taskDefinitionArns": [
        "arn:aws:ecs:us-east-1:079438882329:task-definition/sample-fargate:1"
    ]
}

```

## Step 6 – Run a Scalable ECS Service with 2 Tasks

In a real-world application, we want the web server to run multiple instances, this can be done with ECS services, that run multiple tasks and has many benefits such as automatically restarted if they crash.

```bash
└─$ aws ecs create-service --cluster CCBDA-CLUSTER  \
  --service-name fargate-service \
  --task-definition sample-fargate:1 \
  --desired-count 2 \
  --launch-type "FARGATE" \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-XXXX],securityGroups=[sg-XXXX],assignPublicIp=ENABLED}"
```

![](../screenshots/4-double_running.png)

![](../screenshots/5-double_tasks.png)

## Step 7 – Clean Up Resources

Finally, we can delete the service, cluster and task definition with the following commands:

```bash
# Delete the ECS service
└─$ aws ecs delete-service --cluster CCBDA-CLUSTER --service fargate-service --force

# Delete the ECS cluster
└─$ aws ecs delete-cluster --cluster CCBDA-CLUSTER

# Deregister the task definition
aws ecs deregister-task-definition --task-definition sample-fargate:1

```

---

# 4.LAB - Part 2: Deploying on AWS Fargate with ECS, ALB & Auto Scaling

This lab guides you through the process of deploying a containerized web application using **AWS Fargate**, a serverless compute engine for containers that eliminates the need to manage EC2 instances.

### What this lab covers:

1. **Creating an ECS cluster** using Fargate to run an Apache HTTP server container.
2. **Configuring an Application Load Balancer (ALB)** to distribute incoming HTTP traffic to the Fargate tasks.
3. Setting up a **target group** that receives requests from the ALB listener.
4. **Verifying the deployment** by accessing the web app through the public DNS name of the ALB.
5. **Enabling Auto Scaling** for the ECS service based on average CPU usage.
6. Performing a full **clean-up of all AWS resources** (service, cluster, task definition, ALB, target group, and security group) to avoid unnecessary costs.

## Objective

Deploy a containerized web application using AWS Fargate and ECS, expose it via an Application Load Balancer (ALB), configure automatic scaling based on CPU usage, and safely clean up all resources.

---

## Preconfigured Resources

| Resource           | Value                                                            |
|-------------------|------------------------------------------------------------------|
| **VPC ID**         | `<vpc-id>`                                                      |
| **Subnets**        | `<subnet-id-1>`, `<subnet-id-2>`                                |
| **Security Group** | `<security-group-id>` (inbound rule: TCP port 80 open allowed)  |

---

## Step 1 – Create a Target Group

```bash
aws elbv2 create-target-group \
  --name fargate-targets \
  --protocol HTTP \
  --port 80 \
  --vpc-id <vpc-id> \
  --target-type ip
```

---

## Step 2 – Create an Application Load Balancer (ALB)

```bash
aws elbv2 create-load-balancer \
  --name fargate-alb \
  --subnets <subnet-id-1> <subnet-id-2> \
  --security-groups <security-group-id> \
  --type application \
  --scheme internet-facing
```

![ALB created and active](../screenshots/4-EC2_load_balancer.png)

This confirms that the ALB `fargate-alb` is active and associated with the correct VPC.

---

## Step 3 – Create a Listener for Port 80

```bash
aws elbv2 create-listener \
  --load-balancer-arn <load-balancer-arn> \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=<target-group-arn>
```

---

## Step 4 – Create ECS Fargate Service

```bash
aws ecs create-service \
  --cluster <cluster-name> \
  --service-name <service-name> \
  --task-definition <task-definition-name>:<revision> \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<subnet-id-1>,<subnet-id-2>],securityGroups=[<security-group-id>],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=<target-group-arn>,containerName=<container-name>,containerPort=80"
```

---

## Step 5 – Test the Application

1. Go to ECS Console → Cluster `<cluster-name>` → Services
2. Ensure tasks are in `RUNNING` state
3. Go to EC2 Console → Load Balancers → select `fargate-alb`
4. Copy the **DNS name** and visit in your browser:
   ```
   http://<alb-dns-name>
   ```

![ALB listener details](../screenshots/6-load_balancer_success.png)

Here you can see the ALB listener forwarding traffic on port 80 to the `fargate-targets` group.

---

## Step 6 – Configure Auto Scaling

#### 6.1 Register the scalable target

```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/<cluster-name>/<service-name> \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 1 \
  --max-capacity 4
```

#### 6.2 Create the `scaling-policy.json` file

```json
{
  "TargetValue": 50.0,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
  },
  "ScaleOutCooldown": 30,
  "ScaleInCooldown": 30
}
```

#### 6.3 Apply the policy

```bash
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/<cluster-name>/<service-name> \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

---

## Step 7 – Clean Up Resources

### 7.1 Delete ECS Service

```bash
aws ecs delete-service \
  --cluster <cluster-name> \
  --service <service-name> \
  --force
```

---

### 7.2 Delete ECS Cluster

```bash
aws ecs delete-cluster --cluster <cluster-name>
```

---

### 7.3 Deregister Task Definition

```bash
aws ecs deregister-task-definition --task-definition <task-definition-name>:<revision>
```

---

### 7.4 Delete Listener

```bash
aws elbv2 describe-listeners \
  --load-balancer-arn <load-balancer-arn>
```

Then:

```bash
aws elbv2 delete-listener --listener-arn <listener-arn>
```

---

### 7.5 Delete Load Balancer and Target Group

```bash
aws elbv2 delete-load-balancer --load-balancer-arn <load-balancer-arn>
aws elbv2 delete-target-group --target-group-arn <target-group-arn>
```

![No load balancers remaining](../screenshots/7-delete_load_balancer.png)

This screen confirms that the load balancer has been successfully deleted.

---

### 7.6 (Optional) Delete Security Group

```bash
aws ec2 delete-security-group --group-id <security-group-id>
```

---


## Summary:

You have successfully:
- Deployed a containerized application on AWS Fargate
- Exposed it using an Application Load Balancer
- Enabled auto scaling based on CPU
- Cleaned up all the AWS resources


## LAB - PART3: Deploying a custom application

Most of the times, we will want to deploy a custom docker and code to AWS Fargate, creating this way multiple microservices, one with its individual purpose. To learn how to run custom dockers on AWS ECS using AWS Fargate, we have provided a small HTML file and the docket to run it in the folder "webapp". This part of the tutorial can be easialy extrapolated to using multiple different docker images and runing them as services in the ECS cluster.

First of all we will build our docker image. 

```bash
└─$ docker build -t fargate-website:v1.0.0 .
```

Next, we have to authorise Docker command line client to perform actions on AWS. 

```bash
└─$ aws ecr get-login-password --region us-east-1  | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com
```
Now, we will create a elastic container registry (ECR) for or web application.

```bash
└─$ aws ecr create-repository --repository-name fargate-website --region us-east-1   
```
Once the repository is created, we want to be able to track the different versions of our web application, so, in case the one deployed does not work, we can easily roll back to a previous one.

```bash
└─$ docker tag fargate-website:v1.0.0 <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/fargate-website:v1.0.0
```

Once tagged, we can push it to the ECR.

```bash
└─$ docker push <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/fargate-website:v1.0.0
```

As we have done before, we create a json file with the information needed to define a new task. The difference is that in this case, we will link the image tag to or curtom defined one in ECR.  Furthermore, since the AWS learners lab has some limitations, to deploy a custom image, we have to specify the executionRoleArn to "arn:aws:iam::aws_account_id>:role/LabRole", since otherwise an error regarding the roles will pop up. 

```json
{
  "family": "simple-fargate-task",
  "networkMode": "awsvpc",
  "executionRoleArn": "arn:aws:iam::aws_account_id>:role/LabRole",
  "containerDefinitions": [
    {
      "name": "Fargate-website",
      "image": "aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/fargate-website:v1.0.0",
      "cpu": 256,
      "memory": 512,
      "portMappings": [
        {
          "containerPort": 80,
          "hostPort": 80,
          "protocol": "tcp"
        }
      ],
      "essential": true
    }
  ],
  "requiresCompatibilities": [
    "FARGATE"
  ],
  "cpu": "256",
  "memory": "512"
}

```

Now we can define the task with the json:

```bash
└─$ aws ecs register-task-definition --cli-input-json file://task_definition.json --region us-east-1

```

Create a cluster:

```bash
└─$ aws ecs create-cluster --cluster-name CCBDA-CLUSTER-V2 --region us-east-1
```

And run the task to ensure it works properly:

```bash
└─$ aws ecs run-task \
  --cluster CCBDA-CLUSTER-V2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-XXXXX],securityGroups=[sg-XXXXXX],assignPublicIp=\"ENABLED\"}" \
  --task-definition simple-fargate-task \
  --region us-east-1
```

Finally, we can see our custom application running on AWS Fargate.

![Custom Website](../screenshots/website-custom.PNG)




---

## Differences Between Lab1 and Lab2

| Feature                          | **Lab1**                                      | **Lab2**                                                 |
|----------------------------------|----------------------------------------------------|------------------------------------------------------------------|
| **Service Type**                 | Single Fargate task                                | Fargate ECS **Service** with managed deployment                 |
| **Load Balancer (ALB)**          | ❌ Not used                                        | ✅ Configured with HTTP listener and target group               |
| **Access Method**                | Public IP of the running task                     | Public **DNS name** of the ALB                                  |
| **Scaling**                      | ❌ No scaling, fixed task count                    | ✅ **Auto Scaling** based on average CPU usage                  |
| **Network Setup**                | Simple: one subnet, public IP                     | Complex: multiple subnets, security group, VPC routing          |
| **Deployment**                   | Manual task run via CLI                           | ECS **Service** with desired count and rolling updates          |
| **Cleanup Steps**                | Stop task manually                                | Full clean-up: service, ALB, listener, target group, etc.       |
| **Learning Focus**               | Introduction to AWS Fargate                       | End-to-end deploy of a scalable web application infrastructure  |

---

# Useful Resources: Links, Articles, and Videos for Further Learning

## Official AWS Resources

- **AWS Fargate Overview**  
  Comprehensive information about AWS Fargate, including its features, benefits, and pricing.  
  [https://aws.amazon.com/fargate/](https://aws.amazon.com/fargate/)

- **Getting Started with AWS Fargate**  
  Step-by-step guide to launching your first container using Fargate with Amazon ECS or EKS.  
  [https://aws.amazon.com/fargate/getting-started/](https://aws.amazon.com/fargate/getting-started/)

- **AWS Fargate Documentation for Amazon ECS**  
  Detailed documentation on using AWS Fargate with Amazon ECS, including task definitions and service configurations.  
  [https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)

- **AWS Fargate Documentation for Amazon EKS**  
  Guidance on running Kubernetes pods on AWS Fargate using Amazon EKS.  
  [https://docs.aws.amazon.com/eks/latest/userguide/fargate.html](https://docs.aws.amazon.com/eks/latest/userguide/fargate.html)

## Video Tutorials

- **AWS Fargate Tutorial - AWS Container Tutorial**  
  A comprehensive video tutorial covering AWS Fargate, ECS, EKS, and Docker deployment.  
  [https://www.youtube.com/watch?v=C6v1GVHfOow](https://www.youtube.com/watch?v=C6v1GVHfOow)

- **Create an AWS Fargate Cluster**  
  Tutorial on setting up an AWS Fargate cluster using Amazon ECS.  
  [https://www.youtube.com/watch?v=WsvuIxaCQGg](https://www.youtube.com/watch?v=WsvuIxaCQGg)

- **AWS Fargate Tutorial Playlist**  
  A series of videos providing in-depth tutorials on AWS Fargate.  
  [https://www.youtube.com/playlist?list=PLwpoxH5mFQS39P_DLOZZNM5XPREWWDwE1](https://www.youtube.com/playlist?list=PLwpoxH5mFQS39P_DLOZZNM5XPREWWDwE1)

## Hands-On Tutorials & Blogs

- **Launch Docker Container on AWS Fargate**  
  A practical guide to deploying Docker containers using AWS Fargate.  
  [https://www.youtube.com/watch?v=1n46Nudo6Yo](https://www.youtube.com/watch?v=1n46Nudo6Yo)

- **A Tutorial on AWS Fargate**  
  An introductory tutorial on AWS Fargate, explaining its benefits and use cases.  
  [https://medium.com/@chasdevs/a-tutorial-on-aws-fargate-bd63828b6d6c](https://medium.com/@chasdevs/a-tutorial-on-aws-fargate-bd63828b6d6c)

- **What is AWS Fargate?**  
  An in-depth article discussing AWS Fargate's features, pricing, and comparisons with other services.  
  [https://spacelift.io/blog/what-is-aws-fargate](https://spacelift.io/blog/what-is-aws-fargate)

## Additional Reading

- **Introduction to AWS Fargate**  
  An article providing a comprehensive overview of AWS Fargate, including its architecture and advantages.  
  [https://www.geeksforgeeks.org/introduction-to-aws-fargate/](https://www.geeksforgeeks.org/introduction-to-aws-fargate/)

- **AWS Fargate: A Beginner's Guide**  
  A beginner-friendly guide to understanding and using AWS Fargate.  
  [https://medium.com/edureka/aws-fargate-85a0e256cb03](https://medium.com/edureka/aws-fargate-85a0e256cb03)
