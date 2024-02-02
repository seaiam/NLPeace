# Dockerizing your app

This guide has the steps to containerize your app.

# Steps
1. Install Docker to create and manage containers: [Docker](https://docs.docker.com/get-docker/)
2. Install the docker extension in VS Code
3. Open the terminal in VS code, and make sure that the path is at the root of the project (where the Dockerfile is located)
4. run the following command to create an image in development: docker-compose -f docker-compose.dev.yml up --build

5. run the following command to create an image in production: docker-compose -f docker-compose.prod.yml up --build
   
The container should now be up and running. 

To view the container, open your browser and search: http://localhost:8000/ in dev and https://nlpeace-0c427559664a.herokuapp.com in production

In Docker, you can view your current deployed container as well as previous images that you have created.

To remove the current container, you can run the command: docker-compose down
