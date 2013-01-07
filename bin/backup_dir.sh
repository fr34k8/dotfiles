#!/bin/bash
# Script that creates a tarball backup of a directory,
# compressed with xz (LZMA2) and encrypted with GPG.
# Resulting backup is then uploaded onto my Amazon S3
# storage space.
#
# Requires:
# * GNU Tar 1.22
# * XZ Utils 4.999.9beta
# * GNU Privacy Guard
# * Python 2.5+
# * python-boto
#
# See below for the gpgxz.sh and s3up.py helper scripts.

export BACKUPDATE=`date +"%Y%m%d-%H%M"`
export BACKUP_FILE=/tmp/$1-$BACKUPDATE.tar.xz.gpg
export BACKUP_FILE_BASENAME=$1-$BACKUPDATE.tar.xz.gpg

echo
echo "Removing existing backup file (if applicable)"
rm $BACKUP_FILE

echo
echo
tar -cf $BACKUP_FILE -Igpgxz.sh $1 --exclude-caches-all --exclude="*.pyo" --exclude="*.pyc"

echo
echo "Uploading backup to S3 store"
s3up.py $BACKUP_FILE miketigas-backup `date -u +"%Y%m%d-%H"`-UTC/$BACKUP_FILE_BASENAME 0 "private"

echo
echo "Removing archive from temp dir"
rm $BACKUP_FILE
