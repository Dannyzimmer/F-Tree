FROM python:3.12.6-slim-bullseye

RUN apt update -y && \
    apt install -y pango1.0-tools tk graphviz xdg-utils evince

ADD GUI.py GUI.py
ADD run.py run.py
ADD resources resources
ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD ["python3", "/run.py"]
