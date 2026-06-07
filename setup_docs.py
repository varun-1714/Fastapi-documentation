import os
import shutil

# 1. Define target directories
directories = [
    "docs/getting-started",
    "docs/fundamentals",
    "docs/pydantic",
    "docs/authentication",
    "docs/databases",
    "docs/redis",
    "docs/websocket",
    "docs/graphql",
    "docs/testing",
    "docs/docker",
    "docs/kubernetes",
    "docs/aws",
    "docs/ai",
    "docs/microservices",
    "docs/projects",
    "docs/interview-preparation"
]

print("Creating directories...")
for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created/Verified directory: {directory}")

# 2. Define source-to-destination mappings
mappings = {
    "book/part_01_python_foundations.md": "docs/getting-started/python_foundations.md",
    "book/part_02_fastapi_fundamentals.md": "docs/fundamentals/fastapi_fundamentals.md",
    "book/part_03_core_fastapi.md": "docs/fundamentals/core_fastapi.md",
    "book/part_04_pydantic_v2.md": "docs/pydantic/pydantic_v2.md",
    "book/part_05_dependency_injection.md": "docs/pydantic/dependency_injection.md",
    "book/part_06_auth_and_security.md": "docs/authentication/security.md",
    "book/part_07_databases.md": "docs/databases/sqlalchemy_databases.md",
    "book/part_08_mongodb.md": "docs/databases/mongodb_motor.md",
    "book/part_09_redis.md": "docs/redis/redis_integration.md",
    "book/part_10_background_tasks.md": "docs/fundamentals/background_tasks.md",
    "book/part_11_websockets.md": "docs/websocket/websockets.md",
    "book/part_12_graphql.md": "docs/graphql/graphql.md",
    "book/part_13_testing.md": "docs/testing/testing.md",
    "book/part_14_logging_and_monitoring.md": "docs/fundamentals/logging_and_monitoring.md",
    "book/part_15_middleware.md": "docs/fundamentals/middleware.md",
    "book/part_16_production_architecture.md": "docs/fundamentals/production_architecture.md",
    "book/part_17_docker.md": "docs/docker/docker.md",
    "book/part_18_kubernetes.md": "docs/kubernetes/kubernetes.md",
    "book/part_19_aws.md": "docs/aws/aws.md",
    "book/part_20_ai_and_ml.md": "docs/ai/ai_and_ml.md",
    "book/part_21_llm_applications.md": "docs/ai/llm_applications.md",
    "book/part_22_microservices.md": "docs/microservices/microservices.md",
    "book/part_23_end_to_end_projects.md": "docs/projects/end_to_end_projects.md",
    "book/part_24_interview_prep.md": "docs/interview-preparation/interview_prep.md",
    "book/appendices.md": "docs/interview-preparation/appendices.md"
}

print("\nCopying files...")
for src, dst in mappings.items():
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied {src} -> {dst}")
    else:
        print(f"Warning: Source file {src} not found! Skipping.")

print("\nDocumentation directory population complete.")
