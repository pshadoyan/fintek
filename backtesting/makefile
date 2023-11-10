# Define Docker image name
IMAGE_NAME=backtest-infra

# Define Docker tag
TAG=latest

# Path to the tests directory
TESTS_PATH=src/tests

# Make build
build:
	docker build -t $(IMAGE_NAME):$(TAG) .

# Make run (depends on build)
run: build
	docker-compose up

# Make push (depends on build)
push: build
	docker push $(IMAGE_NAME):$(TAG)

# Make test (does not depend on build)
test:
	cd $(TESTS_PATH) && python -m unittest discover

# Make down (to stop and remove containers, networks, images, and volumes)
down:
	docker-compose down
