help:                ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

build:               ## Build docker image for the application
build: stop
	docker-compose build

shell:               ## Run container to load shell
	docker-compose run app /bin/bash

start-bg:            ## Starts container in detached mode
	docker-compose up -d

start:               ## Starts the application running all the services
	docker-compose up

stop:                ## Stop and remove containers
	docker-compose down
