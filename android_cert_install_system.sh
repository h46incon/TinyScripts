#!/bin/sh
#su

WORK_PATH=$(dirname $(readlink -f $0))
TEMP_SYS_CERT=${WORK_PATH}/system_cert
SYS_CERT=/system/etc/security/cacerts

umount ${SYS_CERT}
rm -r $TEMP_SYS_CERT

mkdir $TEMP_SYS_CERT
cp ${SYS_CERT}/*  ${TEMP_SYS_CERT}/
mount -t tmpfs tmpfs $SYS_CERT
cp ${TEMP_SYS_CERT}/* ${SYS_CERT}/
cp ${WORK_PATH}/my_cert/* ${SYS_CERT}/
chown root:root ${SYS_CERT}/*
chmod 644 ${SYS_CERT}/*
chcon u:object_r:system_file:s0 ${SYS_CERT}/*

echo "Done"

