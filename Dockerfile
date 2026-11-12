FROM python:3.14-slim
LABEL maintainer="s@mck.la"
ENV MY_APP_PATH=/opt/checkSMTP \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Pick up Debian security fixes released since the base image was built
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p $MY_APP_PATH/data

WORKDIR $MY_APP_PATH/
COPY requirements.txt ./
# pip is only needed at build time; removing it also drops the copies of
# urllib3/msgpack/setuptools it bundles, which scanners flag.
RUN pip install --root-user-action=ignore -r requirements.txt \
    && python -m pip uninstall -y --root-user-action=ignore pip
COPY run.py main.py ./

# Run as an unprivileged user rather than root
RUN useradd --system --no-create-home --shell /usr/sbin/nologin app \
    && chown -R app:app $MY_APP_PATH/data
USER app

ENTRYPOINT ["python3", "-u", "/opt/checkSMTP/run.py"]

EXPOSE 8000/tcp
