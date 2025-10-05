# FastAPI Task App

## Setup & Run

Clone the repository:

git clone https://github.com/imtiaz2564/fastapi_task.git

cd fastapi-task-app

## Build and Start the Containers

Start the containers:

docker-compose up --build

This will start:

FastAPI app on http://localhost:8000

MySQL on localhost:3307 (mapped from container port 3306)

The FastAPI app automatically connects to the database and creates the required tables.

Stop the containers:

docker-compose down


## Environment Variables
Set in docker-compose.yml:
environment:
  DATABASE_URL: "mysql+aiomysql://root:root@db:3306/fastapi_db"
root:root → MySQL username and password

db → MySQL container hostname inside Docker network

3306 → MySQL container port

fastapi_db → Database name

Note: The host port 3307 maps to container port 3306 for local access.