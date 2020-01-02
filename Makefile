# Builds the required docker images for the docker environment
compose_build:
	docker-compose build

# Spins up all of the required docker containers for this project
compose_up:
	docker-compose up

# Tears down all of the running docker containers for this project
compose_down:
	docker-compose down

# Drops you into the currently running application container's shell
shell:
	docker-compose exec server /bin/bash

# Runs the application inside the docker container
run:
	python -m kitkatch 

# Run the unit tests
unittest:
	py.test --disable-warnings -vv -s tests

.PHONY: compose_build compose_up compose_down shell run unittest
