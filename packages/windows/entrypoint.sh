#! /bin/bash

set -ex

JOBS=$1
DEBUG=$2
ZIP_NAME=$3
TRUST_VERIFICATION=$4
CA_NAME=$5

# Compile the securics agent for Windows
FLAGS="-j ${JOBS} IMAGE_TRUST_CHECKS=${TRUST_VERIFICATION} CA_NAME=\"${CA_NAME}\" "

if [[ "${DEBUG}" = "yes" ]]; then
    FLAGS+="DEBUG=1 "
fi

if [ -z "${BRANCH}"]; then
    mkdir /securics-local-src
    cp -r /local-src/* /securics-local-src
else
    URL_REPO=https://github.com/wazuh/wazuh/archive/${BRANCH}.zip

    # Download the securics repository
    wget -O securics.zip ${URL_REPO} && unzip securics.zip
fi

bash -c "make -C /securics-*/src deps TARGET=winagent ${FLAGS}"
bash -c "make -C /securics-*/src TARGET=winagent ${FLAGS}"

rm -rf /securics-*/src/external

zip -r /shared/${ZIP_NAME} /securics-*
