# start by pulling the python image
FROM python:3.8-alpine

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# copy every content from the local file to the image
COPY . /app

# Set the environment variable for TLS
ENV SSL_PROTOCOL=TLSv1.2

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["app.py"]
