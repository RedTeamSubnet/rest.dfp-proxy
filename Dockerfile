# syntax=docker/dockerfile:1

ARG BASE_IMAGE=ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG DFG_API_SLUG="rest.device-fp-gate"


## Here is the builder image:
FROM ${BASE_IMAGE} AS builder

ARG DEBIAN_FRONTEND
ARG DFG_API_SLUG

# ARG USE_GPU=false
ARG PYTHON_VERSION=3.10

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR "/usr/src/${DFG_API_SLUG}"

RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=private \
	--mount=type=cache,target=/root/.cache,sharing=locked \
	_BUILD_TARGET_ARCH=$(uname -m) && \
	echo "BUILDING TARGET ARCHITECTURE: ${_BUILD_TARGET_ARCH}" && \
	rm -rfv /var/lib/apt/lists/* /var/cache/apt/archives/* /tmp/* && \
	apt-get clean -y && \
	# echo "Acquire::http::Pipeline-Depth 0;" >> /etc/apt/apt.conf.d/99fixbadproxy && \
	# echo "Acquire::http::No-Cache true;" >> /etc/apt/apt.conf.d/99fixbadproxy && \
	# echo "Acquire::BrokenProxy true;" >> /etc/apt/apt.conf.d/99fixbadproxy && \
	apt-get update --fix-missing -o Acquire::CompressionTypes::Order::=gz && \
	apt-get install -y --no-install-recommends \
		ca-certificates \
		build-essential \
		wget && \
	_MINICONDA_VERSION=py39_25.1.1-2 && \
	if [ "${_BUILD_TARGET_ARCH}" == "x86_64" ]; then \
		_MINICONDA_FILENAME=Miniconda3-${_MINICONDA_VERSION}-Linux-x86_64.sh && \
		export _MINICONDA_URL=https://repo.anaconda.com/miniconda/${_MINICONDA_FILENAME}; \
	elif [ "${_BUILD_TARGET_ARCH}" == "aarch64" ]; then \
		_MINICONDA_FILENAME=Miniconda3-${_MINICONDA_VERSION}-Linux-aarch64.sh && \
		export _MINICONDA_URL=https://repo.anaconda.com/miniconda/${_MINICONDA_FILENAME}; \
		# _MINIFORGE_VERSION=24.11.3-0 && \
		# _MINICONDA_FILENAME=Miniforge3-${_MINIFORGE_VERSION}-Linux-aarch64.sh && \
		# export _MINICONDA_URL=https://github.com/conda-forge/miniforge/releases/download/${_MINIFORGE_VERSION}/${_MINICONDA_FILENAME}; \
	else \
		echo "Unsupported platform: ${_BUILD_TARGET_ARCH}" && \
		exit 1; \
	fi && \
	if [ ! -f "/root/.cache/${_MINICONDA_FILENAME}" ]; then \
		wget -nv --show-progress --progress=bar:force:noscroll "${_MINICONDA_URL}" -O "/root/.cache/${_MINICONDA_FILENAME}"; \
	fi && \
	/bin/bash "/root/.cache/${_MINICONDA_FILENAME}" -b -u -p /opt/conda && \
	/opt/conda/condabin/conda update -y conda && \
	/opt/conda/condabin/conda install -y python=${PYTHON_VERSION} pip && \
	/opt/conda/bin/pip install --timeout 60 -U pip

# COPY ./requirements* ./
RUN	--mount=type=cache,target=/root/.cache,sharing=locked \
	--mount=type=bind,source=requirements.txt,target=requirements.txt \
	# _BUILD_TARGET_ARCH=$(uname -m) && \
	# if [ "${_BUILD_TARGET_ARCH}" == "x86_64" ] && [ "${USE_GPU}" == "false" ]; then \
	# 	export _REQUIRE_FILE_PATH=./requirements/requirements.amd64.txt; \
	# elif [ "${_BUILD_TARGET_ARCH}" == "x86_64" ] && [ "${USE_GPU}" == "true" ]; then \
	# 	export _REQUIRE_FILE_PATH=./requirements/requirements.gpu.txt; \
	# elif [ "${_BUILD_TARGET_ARCH}" == "aarch64" ]; then \
	# 	export _REQUIRE_FILE_PATH=./requirements/requirements.arm64.txt; \
	# fi && \
	# /opt/conda/bin/pip install --timeout 60 -r "${_REQUIRE_FILE_PATH}" && \
	/opt/conda/bin/pip install --timeout 60 -r ./requirements.txt


## Here is the base image:
FROM ${BASE_IMAGE} AS base

ARG DEBIAN_FRONTEND
ARG DFG_API_SLUG

ARG DFG_HOME_DIR="/app"
ARG DFG_API_DIR="${DFG_HOME_DIR}/${DFG_API_SLUG}"
ARG DFG_API_DATA_DIR="/var/lib/${DFG_API_SLUG}"
ARG DFG_API_LOGS_DIR="/var/log/${DFG_API_SLUG}"
ARG DFG_API_TMP_DIR="/tmp/${DFG_API_SLUG}"
# ARG DFG_API_MODELS_DIR="${DFG_API_DATA_DIR}/models"
ARG DFG_API_PORT=8000
## IMPORTANT!: Get hashed password from build-arg!
## echo "DFG_USER_PASSWORD123" | openssl passwd -5 -stdin
ARG HASH_PASSWORD="\$5\$UN1S7dZEa/qDoijJ\$hJ5o.Wpp5aP2kp.46Y7lWgcsRE8/oRLVswU6Swi13fB"
ARG UID=1000
ARG GID=11000
ARG USER=dfg-user
ARG GROUP=dfg-group

ENV DFG_HOME_DIR="${DFG_HOME_DIR}" \
	DFG_API_DIR="${DFG_API_DIR}" \
	DFG_API_DATA_DIR="${DFG_API_DATA_DIR}" \
	DFG_API_LOGS_DIR="${DFG_API_LOGS_DIR}" \
	DFG_API_TMP_DIR="${DFG_API_TMP_DIR}" \
	DFG_API_PORT=${DFG_API_PORT} \
	UID=${UID} \
	GID=${GID} \
	USER=${USER} \
	GROUP=${GROUP} \
	PYTHONIOENCODING=utf-8 \
	PYTHONUNBUFFERED=1 \
	PATH="/opt/conda/bin:${PATH}"

# ENV DFG_API_MODELS_DIR="${DFG_API_MODELS_DIR}"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN rm -rfv /var/lib/apt/lists/* /var/cache/apt/archives/* /tmp/* /root/.cache/* && \
	apt-get clean -y && \
	# echo "Acquire::http::Pipeline-Depth 0;" >> /etc/apt/apt.conf.d/99fixbadproxy && \
	# echo "Acquire::http::No-Cache true;" >> /etc/apt/apt.conf.d/99fixbadproxy && \
	# echo "Acquire::BrokenProxy true;" >> /etc/apt/apt.conf.d/99fixbadproxy && \
	apt-get update --fix-missing -o Acquire::CompressionTypes::Order::=gz && \
	apt-get install -y --no-install-recommends \
		sudo \
		locales \
		tzdata \
		procps \
		iputils-ping \
		iproute2 \
		curl \
		nano && \
	apt-get clean -y && \
	sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
	sed -i -e 's/# en_AU.UTF-8 UTF-8/en_AU.UTF-8 UTF-8/' /etc/locale.gen && \
	sed -i -e 's/# ko_KR.UTF-8 UTF-8/ko_KR.UTF-8 UTF-8/' /etc/locale.gen && \
	dpkg-reconfigure --frontend=noninteractive locales && \
	update-locale LANG=en_US.UTF-8 && \
	echo "LANGUAGE=en_US.UTF-8" >> /etc/default/locale && \
	echo "LC_ALL=en_US.UTF-8" >> /etc/default/locale && \
	addgroup --gid ${GID} ${GROUP} && \
	useradd -lmN -d "/home/${USER}" -s /bin/bash -g ${GROUP} -G sudo -u ${UID} ${USER} && \
	echo "${USER} ALL=(ALL) NOPASSWD: ALL" > "/etc/sudoers.d/${USER}" && \
	chmod 0440 "/etc/sudoers.d/${USER}" && \
	echo -e "${USER}:${HASH_PASSWORD}" | chpasswd -e && \
	echo -e "\nalias ls='ls -aF --group-directories-first --color=auto'" >> /root/.bashrc && \
	echo -e "alias ll='ls -alhF --group-directories-first --color=auto'\n" >> /root/.bashrc && \
	echo -e "\numask 0002" >> "/home/${USER}/.bashrc" && \
	echo "alias ls='ls -aF --group-directories-first --color=auto'" >> "/home/${USER}/.bashrc" && \
	echo -e "alias ll='ls -alhF --group-directories-first --color=auto'\n" >> "/home/${USER}/.bashrc" && \
	echo ". /opt/conda/etc/profile.d/conda.sh" >> "/home/${USER}/.bashrc" && \
	echo "conda activate base" >> "/home/${USER}/.bashrc" && \
	rm -rfv /var/lib/apt/lists/* /var/cache/apt/archives/* /tmp/* /root/.cache/* "/home/${USER}/.cache/*" && \
	mkdir -pv "${DFG_API_DIR}" "${DFG_API_DATA_DIR}" "${DFG_API_LOGS_DIR}" "${DFG_API_TMP_DIR}" && \
	chown -Rc "${USER}:${GROUP}" "${DFG_HOME_DIR}" "${DFG_API_DATA_DIR}" "${DFG_API_LOGS_DIR}" "${DFG_API_TMP_DIR}" && \
	find "${DFG_API_DIR}" "${DFG_API_DATA_DIR}" -type d -exec chmod -c 770 {} + && \
	find "${DFG_API_DIR}" "${DFG_API_DATA_DIR}" -type d -exec chmod -c ug+s {} + && \
	find "${DFG_API_LOGS_DIR}" "${DFG_API_TMP_DIR}" -type d -exec chmod -c 775 {} + && \
	find "${DFG_API_LOGS_DIR}" "${DFG_API_TMP_DIR}" -type d -exec chmod -c +s {} +

ENV LANG=en_US.UTF-8 \
	LANGUAGE=en_US.UTF-8 \
	LC_ALL=en_US.UTF-8

COPY --from=builder --chown=${UID}:${GID} /opt/conda /opt/conda


## Here is the final image:
FROM base AS app

WORKDIR "${DFG_API_DIR}"
COPY --chown=${UID}:${GID} ./src ${DFG_API_DIR}
COPY --chown=${UID}:${GID} --chmod=770 ./scripts/docker/*.sh /usr/local/bin/

# VOLUME ["${DFG_API_DATA_DIR}"]
# EXPOSE ${DFG_API_PORT}

USER ${UID}:${GID}
# HEALTHCHECK --start-period=30s --start-interval=1s --interval=5m --timeout=5s --retries=3 \
# 	CMD curl -f http://localhost:${DFG_API_PORT}/api/v${DFG_API_VERSION:-1}/ping || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
# CMD ["-b", "uvicorn main:app --host=0.0.0.0 --port=${DFG_API_PORT:-8000} --no-access-log --no-server-header --proxy-headers --forwarded-allow-ips='*'"]
