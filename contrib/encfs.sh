#!/bin/bash

DIR=`pwd`
RAW_DIR=${DIR}/data-raw
ENC_DIR=${DIR}/data
action=$1

if [ "create" == "$action" ]; then
    mkdir -p ${RAW_DIR} && \
        mkdir -p ${ENC_DIR} && \
        encfs ${RAW_DIR} ${ENC_DIR}
elif [ "mount" == "$action" ]; then
    encfs ${RAW_DIR} ${ENC_DIR}
elif [ "unmount" == "$action" ]; then
    fusermount -u ${ENC_DIR}
fi