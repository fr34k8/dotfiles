#!/usr/bin/env python
# coding=utf-8
# Run this if you have issues with `s3up.py` -- this will remove partially
# uploaded file chunks and reset S3 state back to normal.
from __future__ import print_function
import os
import sys
from boto.s3.connection import S3Connection

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')

AWS_DEFAULT_BUCKET = os.environ.get('AWS_DEFAULT_BUCKET', '')

S3_ENDPOINT = 's3.amazonaws.com'

# Load/override options from optional `dotfiles_config.py` file.
OPTIONS = set(['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
    'AWS_DEFAULT_BUCKET', 'S3_ENDPOINT'])
for option in OPTIONS:
    try:
        _cfg = __import__('dotfiles_config', globals(), locals(), [option,], -1)
        if _cfg and hasattr(_cfg, option):
            globals()[option] = getattr(_cfg, option)
        del _cfg
    except:
        pass

if not (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY):
    configfile = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'dotfiles_config.py'
    )
    print("`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` must be set,",
        file=sys.stderr)
    print("either as environment varibles or in:", file=sys.stderr)
    print("    %s" % configfile, file=sys.stderr)
    sys.exit(1)

s3 = S3Connection(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    host=S3_ENDPOINT
)
bucket = s3.get_bucket(AWS_DEFAULT_BUCKET)
for mp in bucket.list_multipart_uploads():
    print(mp.key_name)
    mp.cancel_upload()
