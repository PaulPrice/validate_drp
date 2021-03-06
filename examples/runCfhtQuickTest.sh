#!/bin/bash

PRODUCT_DIR=${VALIDATE_DRP_DIR}

CAMERA=CfhtQuick
CONFIG_FILE="${PRODUCT_DIR}"/config/cfhtConfig.py
MAPPER=lsst.obs.cfht.MegacamMapper

"${PRODUCT_DIR}"/examples/runExample.sh $CAMERA $MAPPER \
    ${VALIDATION_DATA_CFHT_DIR}/raw "${CONFIG_FILE}"
