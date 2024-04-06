#!/bin/bash

# Define the log file location
LOG_FILE="docker_startup.log"


# Make sure docker is running
check_docker() {
  # Check if Docker daemon is running
  if ! systemctl is-active --quiet docker; then
    echo "Docker is not running. Attempting to start Docker..." | tee -a $LOG_FILE
    sudo systemctl start docker >> $LOG_FILE 2>&1
  fi

  # Wait a bit for Docker to start
  sleep 30
}

# Log starting of the script
echo "Starting the Docker containers startup script at $(date)" | tee -a $LOG_FILE

# Start Docker
check_docker

# Navigate to the directory containing the docker-compose file
cd /home/azureuser/capstone/NLPeace/backend

# Run Docker Compose commands
#echo "Building Docker containers..." | /usr/bin/tee -a $LOG_FILE
#docker compose -f docker-compose.prod.yml build >> $LOG_FILE 2>&1

echo "Starting Docker containers..." | /usr/bin/tee -a $LOG_FILE
docker compose -f docker-compose.prod.yml up -d >> $LOG_FILE 2>&1

# Log completion
echo "Docker containers startup script finished at $(date)" | tee -a $LOG_FILE
