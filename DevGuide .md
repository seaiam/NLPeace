# NLPEACE Dev Guide

## Local Setup

1. Install Python Version 3.10

2. [Install pip](https://pip.pypa.io/en/stable/installation/)

3. Install pipenv

```
pip install pipenv --user
```

#### Clone Repository

Navigate to the directory where you want to clone the repo

Enter command

```
git clone https://github.com/seaiam/NLPeace.git
```

#### Install Virtual Environment

```
pipenv install
```

### Enter/Exit Virtual Environment

##### To Enter VE 

```
pipenv shell
```

##### To exit VE
```
exit
```

## Spawning Contianers

#### Navigate to backend directory
```
cd ./backend
```

#### Build container image 
```
make build
```

#### Run the contianers 
```
make run
```

## Useful Commands to Know

#### To tear down the containers

 ```
 docker-compose down
  ```

#### If you are getting weird behaviour

```
docker-compose down -v
 ```

#### To rebuild the image without the cache
 ```
 docker-compose build --no-cache
 ```
  
## Run tests 

 ```
 make test
 ```
