#!/usr/bin/env python
# coding=utf-8
"""
s3up-private.py

Uploads files into S3 with a "private" ACL and with "encrypt_key" enabled.
Generates a time-limited URL that can access the given uploaded file.
(See also `s3-genlink.py`.)

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
s3up-private filename [expiration_time]
    Uploads the given file to DEFAULT_BUCKET (media.miketigas.com)
    at the following path:

        files/YYYYMMDD/(filename)

    ...where (filename) is a hashed representation of the original filename.

    [expiration_time] sets the time that the generated link is valid,
    in seconds. (Defaults to 3600 seconds). If set to 0, does not generate
    an access URL.

Please set the following options below before using:
    AWS_ACCESS_KEY_ID (also accepted as an env var)
    AWS_SECRET_ACCESS_KEY (also accepted as an env var)
    AWS_DEFAULT_BUCKET (also accepted as an env var)
    S3_ENDPOINT
    DEFAULT_EXPIRES
    FILENAME_HASHER
(Note, you can also set these in `dotfiles_config.py` -- see example file.
That file overrides identical AWS_* environment variables.)
"""
from __future__ import print_function
import hashlib
import os
import sys
import traceback
from boto.s3.connection import S3Connection, OrdinaryCallingFormat
from datetime import datetime
from mimetypes import guess_type

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

def key_to_secure_url(key, bucket, link_expires):
    s3 = S3Connection(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        calling_format=OrdinaryCallingFormat(),
        host=S3_ENDPOINT
    )
    bucket = s3.get_bucket(bucket)
    k = bucket.get_key(key)
    return k.generate_url(expires_in=link_expires)

def hashed_filename(remote_path):
    filebase, fileext = os.path.splitext(os.path.basename(remote_path))
    return "%s/%s" % (
        os.path.dirname(remote_path),
        FILENAME_HASHER(filebase+datetime.now().isoformat()).hexdigest() + fileext
    )

def easy_up(local_file, link_expires=DEFAULT_EXPIRES):
    if os.path.isfile(local_file):
        rpath = "files/"+datetime.now().strftime("%Y%m%d")
        remote_path = rpath+"/"+os.path.basename(local_file)
        remote_path = hashed_filename(remote_path)

        upload_file(os.path.abspath(local_file), AWS_DEFAULT_BUCKET, remote_path)

        if not link_expires:
            # Expiration time is set to zero.
            print("Upload successful. Expiration time is 0, so not generating a public link. To generate an access link:")
            print("s3-genlink.py %s [expiration_time]" % remote_path)
        else:
            # Have a time
            print(key_to_secure_url(remote_path, AWS_DEFAULT_BUCKET, link_expires))
            print(file=sys.stderr)
            print("To generate a new link:", file=sys.stderr)
            print("s3-genlink.py %s [expiration_time]" % remote_path, file=sys.stderr)
    else:
        print("Path given is not a file.", file=sys.stderr)

def upload_file(local_file, bucket, remote_path):
    s3 = S3Connection(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        calling_format=OrdinaryCallingFormat(),
        host=S3_ENDPOINT
    )
    bucket = s3.get_bucket(bucket)
    key = bucket.new_key(remote_path)
    key.content_type = guess_type(local_file, False)[0] or "application/octet-stream"
    key.set_contents_from_filename(local_file, policy="private", encrypt_key=True)

    # ===== / chunked upload =====

    key.set_metadata('Cache-Control','no-cache, no-store')
    key.set_canned_acl("private")


def main(args):
    if len(args) == 2:
        easy_up(args[0], int(args[1]))
    elif len(args) == 1:
        easy_up(args[0])
    else:
        print("s3up-private filename [expiration_time]")
        print("    Uploads the given file to AWS_DEFAULT_BUCKET (%s)" % AWS_DEFAULT_BUCKET)
        print("    at the following path:" )
        print()
        print("        files/YYYYMMDD/(filename)")
        print()
        print("    ...where (filename) is a hashed representation of the original filename.")
        print()
        print("    [expiration_time] sets the time that the generated link is valid,")
        print("    in seconds. (Defaults to %s seconds)." % DEFAULT_EXPIRES)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except Exception, e:
        sys.stderr.write('\n')
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write('\n')
        sys.exit(1)
