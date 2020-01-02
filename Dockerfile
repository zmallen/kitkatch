FROM python:3.7

WORKDIR /opt

COPY requirements.txt /opt/requirements.txt
RUN pip3 install -r requirements.txt

COPY . /opt/kitkatch

ENTRYPOINT [ "python", "-m", "apptemplate"]
