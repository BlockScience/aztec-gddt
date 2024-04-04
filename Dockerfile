FROM continuumio/miniconda3
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install curl -y
RUN apt-get install unzip
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
COPY aws-credentials.csv .
COPY aztec_gddt aztec_gddt
COPY data data
COPY cloud_run.py .
RUN aws configure import --csv file://aws-credentials.csv
ENTRYPOINT ["python", "cloud_run.py"]