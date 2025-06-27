FROM python:3.12
# here i pick python:3.xx instead of our base on ACR
# becuase the base on ACR is amd64
# then arm machines will have issues
ENV PYTHONUNBUFFERED 1
# to prevent run as root
ARG DOCKER_HOME="/opt/python-user"
ARG DOCKER_CODE="/opt/python-user/code"
ARG DOCKER_GROUP="python-user"
ARG DOCKER_USER="python-user"
ARG DOCKER_UID=5000

ENV ZSH="/opt/python-user/.oh-my-zsh"

WORKDIR ${DOCKER_CODE}

RUN groupadd -g ${DOCKER_UID} ${DOCKER_GROUP} \
    && useradd -r -u ${DOCKER_UID} -g ${DOCKER_GROUP} -d ${DOCKER_HOME} ${DOCKER_USER} \
    && chown -R ${DOCKER_USER}:${DOCKER_GROUP} ${DOCKER_HOME}

RUN apt-get update && \
    apt-get install -y curl git zsh openssh-client && \
    pip install --upgrade pip

# 安装oh-my-zsh
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# 为SSH和git创建目录并设置权限
RUN mkdir -p ${DOCKER_HOME}/.ssh && \
    chown -R ${DOCKER_USER}:${DOCKER_GROUP} ${DOCKER_HOME}/.ssh && \
    chmod 700 ${DOCKER_HOME}/.ssh

ENV PATH "$PATH:/opt/python-user/.local/bin"
ENV PYTHONPATH=.

USER ${DOCKER_USER}
ENTRYPOINT [ "/bin/sh", "-c" ]