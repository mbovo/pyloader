FROM python:3
WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt && pip install -e .

CMD [ "/bin/bash", "/usr/src/app/job.sh" ]
