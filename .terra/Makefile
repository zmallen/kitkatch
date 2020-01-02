AWS_REGION:=$(if $(AWS_REGION),$(AWS_REGION),us-west-2)
ENVIRONMENT:=qa
GIT_SHA:=$(shell git rev-parse --short=7 HEAD)
S3_BUCKET_PREFIX:=$(if $(S3_BUCKET_PREFIX),$(S3_BUCKET_PREFIX),zf-terraform)
TERRAFORM:=terraform

tf_files := $(shell find . -name "*.tf")

all: plan

check-fmt:
	$(TERRAFORM) fmt -check=true -diff

fmt:
	$(TERRAFORM) fmt

init: clobber
	$(TERRAFORM) init -backend-config="bucket=$(S3_BUCKET_PREFIX)-$(ENVIRONMENT)" \
	                  -backend-config="region=$(AWS_REGION)"

validate: ${tf_files}
	$(TERRAFORM) validate \
		-var-file="$(AWS_REGION).tfvar"

plan: init ${tf_files}
	$(TERRAFORM) plan \
		-var "env=$(ENVIRONMENT)" \
		-var "git_sha=\"$(GIT_SHA)\"" \
		-var-file="$(AWS_REGION).tfvar" \
		-out terra.plan

download-model:
	aws s3 cp s3://zf-threatops-ml/object-detection/releases/20190614_zerofox_yolov3.weights ../zerofox_yolov3.weights

apply: plan download-model ../zerofox_yolov3.weights
	$(TERRAFORM) apply terra.plan

clean:
	rm -f *.backup *.plan
	rm -f .terraform/terraform.tfstate

clobber: clean
	rm -rf .terraform

.PHONY: all clean check-fmt clobber fmt validate plan apply
