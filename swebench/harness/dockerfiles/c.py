_DOCKERFILE_BASE_C = r"""
FROM --platform={platform} debian:12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NONINTERACTIVE_SEEN=true \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

ENV TZ=Etc/UTC

# Install necessary packages
RUN apt-get update \
 && apt-get install -y \
      build-essential \
      autoconf \
      libtool \
      git \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
"""

_DOCKERFILE_ENV_C = r"""FROM --platform={platform} sweb.base.c.{arch}:latest

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

COPY ./setup_env.sh /root/
RUN sed -i -e 's/\r$//' /root/setup_env.sh
RUN chmod +x /root/setup_env.sh

# Run the setup script
RUN /bin/bash -c "source ~/.bashrc && /root/setup_env.sh"

WORKDIR /testbed/
"""

_DOCKERFILE_INSTANCE_C = r"""FROM --platform={platform} {env_image_name}

COPY ./setup_repo.sh /root/
RUN sed -i -e 's/\r$//' /root/setup_repo.sh
RUN /bin/bash /root/setup_repo.sh

WORKDIR /testbed/
"""
