help:                ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

build:               ## Build docker image for the application
build: stop
	docker-compose build

one-run:             ## Executes main.py to test the script locally
one-run: stop start-bg
	docker-compose exec app python src/main.py
	docker-compose down

run-tests:           ## Start a container and run test suite for the app
run-tests: start-bg
	docker-compose exec app pytest --cov=src/ --cov-report term-missing
	docker-compose down

shell:               ## Run container to load shell
	docker-compose run app /bin/sh

start-bg:            ## Starts container in detached mode
	docker-compose up -d

start:               ## Starts the application running all the services
	docker-compose up

stop:                ## Stop and remove containers
	docker-compose down
