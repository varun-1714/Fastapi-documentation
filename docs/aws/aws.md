# Part 19: AWS Cloud Integration

---

## Chapter 1: Production AWS Architecture (ECS Fargate, Lambda, RDS & S3)

### 1. Introduction
Deploying APIs to the cloud requires designing secure, scalable, and highly available architectures. AWS (Amazon Web Services) provides container orchestration (ECS Fargate), serverless compute (Lambda), relational database hosting (RDS), and asset storage (S3) to support enterprise workloads.

### 2. Concept Explanation
* **VPC & Subnets**: Isolate cloud resources securely across public and private subnets.
* **AWS ECS Fargate**: Serverless container orchestration that runs Docker containers without requiring you to manage EC2 instances.
* **AWS Lambda & API Gateway**: A serverless execution model where code runs in response to HTTP requests, scaling automatically without server overhead.
* **AWS RDS (Relational Database Service)**: Managed relational databases (PostgreSQL/MySQL) supporting automatic backups, replication, and Multi-AZ failovers.
* **AWS S3 (Simple Storage Service)**: Object storage for static media, documents, and backups.

### 3. Architecture Explanation
For high availability, we deploy containers in an ECS Fargate cluster across private subnets in multiple Availability Zones (AZs). An Application Load Balancer (ALB) routes public traffic from Route53 to the containers, which connect to a Multi-AZ RDS instance.
```
Public Internet ---> Route 53 ---> Application Load Balancer (ALB)
                                           |
                    +----------------------+----------------------+
                    | (AZ 1 - Private)                            | (AZ 2 - Private)
             [ ECS Fargate Pod ]                           [ ECS Fargate Pod ]
                    |                                             |
                    +----------------------+----------------------+
                                           |
                                  [ Multi-AZ RDS ]
```

### 4. Visual Workflow
```
Client Request ---> API Gateway ---> AWS Lambda (fastapi-handler) ---> Reads S3 / RDS ---> Return
```

### 5. Real-World Scenario
An enterprise API needs to serve traffic across two geographic regions, store user documents securely, and scale horizontally without manual server administration.

### 6. Step-by-Step Implementation
1. Package the FastAPI application using the optimized Docker container.
2. Push the Docker image to AWS Elastic Container Registry (ECR).
3. Define the cloud infrastructure using AWS CloudFormation or Terraform.
4. Set up an ECS Fargate task definition running the container.

### 7. Terraform Infrastructure Configuration Example
```hcl
# main.tf - AWS ECS Fargate & ALB infrastructure setup
provider "aws" {
  region = "us-east-1"
}

# 1. VPC Configuration
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
}

# 2. Private Subnet for ECS Task
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
}

# 3. ECS Fargate Cluster
resource "aws_ecs_cluster" "app_cluster" {
  name = "fastapi-production-cluster"
}

# 4. ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "fastapi-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([{
    name      = "fastapi-container"
    image     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/fastapi-app:latest"
    essential = true
    portMappings = [{
      containerPort = 8000
      hostPort      = 8000
    }]
  }])
}
```

### 8. CLI Deployment Examples
Build, tag, and push the image to AWS ECR:
```bash
# Login to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Tag the local build image
docker tag fastapi-app:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/fastapi-app:latest

# Push image
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/fastapi-app:latest
```

### 9. Common Mistakes
Deploying database instances (RDS) in public subnets, making them accessible to the public internet and vulnerable to attacks.

### 10. Best Practices
Always deploy databases (RDS) and application servers (ECS/Fargate) in private subnets, allowing access only from the Application Load Balancer. Use AWS Secrets Manager to store database credentials securely.

### 11. Interview Questions
* **Q: How does AWS ECS Fargate handle container scaling compared to EC2?**
  * *A*: Under the EC2 model, you must manage and scale the underlying virtual machines yourself. Under the Fargate serverless model, AWS manages the host servers; you simply define container CPU and memory requirements, and AWS provisions the resources dynamically.

### 12. Chapter Summary
Production cloud architectures isolate resources in private subnets. ECS Fargate scales container workloads, RDS hosts databases in multiple availability zones, and ALB load balances traffic.

### 13. Practice Exercises
Write an IAM policy that grants a FastAPI task running on ECS access to read and write files to a specific S3 bucket.
