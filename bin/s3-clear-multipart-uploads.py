#!/usr/bin/env python
# coding=utf-8
# Run this if you have issues with `s3up.py` -- this will remove partially
# uploaded file chunks and reset S3 state back to normal.
from boto.s3.connection import S3Connection

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
DEFAULT_BUCKET = ''

# Load/override options from optional `dotfiles_config.py` file.
OPTIONS = set(['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
    'DEFAULT_BUCKET'])
for option in OPTIONS:
    try:
        _cfg = __import__('dotfiles_config', globals(), locals(), [option,], -1)
        if _cfg and hasattr(_cfg, option):
            globals()[option] = getattr(_cfg, option)
        del _cfg
    except:
        pass

s3 = S3Connection(aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
bucket = s3.get_bucket(DEFAULT_BUCKET)
for mp in bucket.list_multipart_uploads():
    print mp.key_name
    mp.cancel_upload()
