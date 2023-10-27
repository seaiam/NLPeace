# NLPEACE

## Local Setup

1. Install Python Version 3.10

2. [Install pip](https://pip.pypa.io/en/stable/installation/)

3. Install pipenv

*  ```pip install pipenv --user```

4. Clone Repository

* Navigate to the directory where you want to clone the repo

* Enter ```git clone https://github.com/seaiam/NLPeace.git```

5. Install Virtual Environment

*  ```pipenv install```

6. Enter/Exit Virtual Environment

* To enter ```pipenv shell```

* To exit ```exit```

## Spawning Contianers

1. cd ./backend

2. docker-compose build

3. docker-compose up

## Useful Commands to Know

To tear down the containers

* docker-compose down 

If you are getting weird behaviour

* docker-compose down -v 

To rebuild the image without the cache
* docker-compose build --no-cache
  
  
  
## Run tests from container

* run this command after building the container:

```docker-compose exec app python manage.py test core.tests```
