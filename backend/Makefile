lint:
	flake8 ./api

run:
	docker-compose up

build: 
	docker-compose build

down:
	docker-compose down

test:
	docker-compose -f docker-compose.dev.yml run --rm app sh -c "python manage.py wait_for_db && python manage.py makemigrations && python manage.py migrate && python manage.py test"
users:
	docker-compose -f docker-compose.dev.yml run --rm app sh -c "python manage.py wait_for_db && python manage.py makemigrations && python manage.py migrate && python manage.py create_test_users"
coverage:
	docker-compose -f docker-compose.dev.yml run --rm app sh -c "python manage.py wait_for_db && python manage.py makemigrations && python manage.py migrate && coverage run manage.py test && coverage report"