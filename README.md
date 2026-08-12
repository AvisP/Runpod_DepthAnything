## Instructions

1. Create a virtualenv with python3.10 and include the packages in `requirements.txt`
2. Download the files of Depth Anything from huggingface into a local `models` folder
3. Create a local endpoint using `handler.py` by running `python handler.py -rp-api`
4. To test the endpoint test it with `send_test_run.py` script. Repo uses a sample image `StreetView.jpg` in the repo. Successful execution would return a matrix and generate an image of the depth map
5. The `send_test_run.py` script will also create a `test_input.json` which can be used to test the endpoint by just doing `python handler.py` which will use this json file to test
6. Create a docker image using the `Dockerfile` created which includes all the packages and the model files as well `docker build --platform linux/amd64 --tag docker_username/depth-anything3:latest .`
7. Locally test if the container works by `docker run -it --gpus all docker_username/depth-anything3:latest`
8. Push the container into the docker hub by `docker push modz1/depth-anything3:latest`
9. Follow instructions on runpod severless and create an endpoint. Copy over the credentials (Key, Url) into `.env.example` and rename it to `.env`
10. Test the endpoint with `send_test_run.py` script
