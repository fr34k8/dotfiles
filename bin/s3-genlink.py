#!/usr/bin/env python
# coding=utf-8
"""
s3-genlink.py

Companion to `s3up-private.py` (or any other utility uploading to S3
with "private" ACL). Generates a time-limited URL that can access the
given key.

Copyright 2012-2013, Mike Tigas
https://mike.tig.as/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

-----

Requires boto: http://boto.cloudhackers.com/

Usage:
s3-genlink.py remote_path [expiration_time]
    Given a key already in S3, generates a URL that is
    valid for `expiration_time` seconds. (Defaults to one hour.)


Please set the following options below before using:
    AWS_ACCESS_KEY_ID (also accepted as an env var)
    AWS_SECRET_ACCESS_KEY (also accepted as an env var)
    AWS_DEFAULT_BUCKET (also accepted as an env var)
    S3_ENDPOINT
    DEFAULT_EXPIRES
    FILENAME_HASHER
(Note, you can also set these in `dotfiles_config.py` -- see example file.)
"""
from __future__ import print_function
import hashlib
import os
import sys
import traceback
from boto.s3.connection import S3Connection
from boto.s3.connection import OrdinaryCallingFormat

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')

AWS_DEFAULT_BUCKET = os.environ.get('AWS_DEFAULT_BUCKET', '')

S3_ENDPOINT = "s3.amazonaws.com"

DEFAULT_EXPIRES = 3600

FILENAME_HASHER = hashlib.sha224

# Load/override options from optional `dotfiles_config.py` file.
OPTIONS = set(['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
    'AWS_DEFAULT_BUCKET', 'S3_ENDPOINT', 'DEFAULT_EXPIRES', 'FILENAME_HASHER'])
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

# ========== Uploader methods ==========

def key_to_secure_url(key, bucket=None, link_expires=DEFAULT_EXPIRES):
    if not bucket:
        bucket = AWS_DEFAULT_BUCKET

    s3 = S3Connection(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        host=S3_ENDPOINT,
        calling_format=OrdinaryCallingFormat()
    )
    bucket = s3.get_bucket(bucket)
    k = bucket.get_key(key)
    print(k.generate_url(expires_in=link_expires))

def main(args):
    if len(args) == 2:
        key_to_secure_url(args[0], AWS_DEFAULT_BUCKET, int(args[1]))
    elif len(args) == 1:
        key_to_secure_url(args[0])
    else:
        print("s3-genlink.py remote_path [expiration_time]")
        print("    Given a remote path already in S3, generates a URL that is")
        print("    valid for `expiration_time` seconds. (Defaults to %s seconds.)" % DEFAULT_EXPIRES)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except Exception, e:
        sys.stderr.write('\n')
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write('\n')
        sys.exit(1)
