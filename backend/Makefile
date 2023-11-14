lint:
	flake8 ./api

run:
	docker-compose down && docker-compose up

build: 
	docker-compose build

test:
	docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py makemigrations && python manage.py migrate && python manage.py test"