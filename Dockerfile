# Pull official base python image
FROM python:3.10

# Set the working directory
WORKDIR /usr/src/NLPeace

# Copy the Pipfile and Pipfile.lock 
COPY ./Pipfile .
COPY ./Pipfile.lock .

# Install pipenv
RUN pip install pipenv

# Install all dependencies
RUN pipenv install --system --deploy --ignore-pipfile

# Copy project
COPY . .