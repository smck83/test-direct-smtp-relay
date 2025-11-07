FROM python:3-slim
LABEL maintainer="s@mck.la"
ENV MY_APP_PATH=/opt/checkSMTP



RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    && mkdir -p $MY_APP_PATH/data
COPY run.py main.py $MY_APP_PATH/
RUN pip install fastapi uvicorn["standard"] cachetools aiocache dnspython
WORKDIR $MY_APP_PATH/

ENTRYPOINT ["python3", "-u", "/opt/checkSMTP/run.py"]

EXPOSE 8000/tcp
