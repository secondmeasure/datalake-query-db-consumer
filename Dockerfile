FROM python:3.9

# Necessary to install BBSM packages on the VPN locally. Uncomment ENV and add back trusted-host/index-url flag to pip
#ENV PIP_INDEX_URL="https://artprod.dev.bloomberg.com/artifactory/api/pypi/bloomberg-pypi/simple"

ARG SQLALCHEMY_DEPENDENCIES=""

WORKDIR /datalakequerydbconsumer

COPY . .

COPY ./log_config.yaml /opt/config/datalakequerydbconsumer/log_config.yaml

RUN python3.9 -m pip install ${SQLALCHEMY_DEPENDENCIES} tox .
#--trusted-host artprod.dev.bloomberg.com --index-url=$PIP_INDEX_URL

ENTRYPOINT [ "python3.9", "-m", "bloomberg.datalake.datalakequerydbconsumer" ]
