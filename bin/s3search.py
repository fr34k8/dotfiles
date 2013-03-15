#!/usr/bin/env python
# coding=utf-8
"""
s3search.py

Crappy shell program to search a given S3 bucket for a filename or
path name.

Copyright 2011-2013, Mike Tigas
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
Relies on `s3up.py` in this directory.

Usage:
  s3search [bucket]

You will then be prompted for the filename to search for. If `bucket` is
not given, `AWS_DEFAULT_BUCKET` is used.

Before using, please configure at least the following options in `s3up.py`:
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_DEFAULT_BUCKET
    S3_ENDPOINT
    BUCKET_CNAME
(Note, you can also set these in `dotfiles_config.py` -- see example file.)
"""
import sys
import traceback
from boto.s3.connection import S3Connection
from socket import setdefaulttimeout
setdefaulttimeout(100.0)

import s3up

def main(args):
    if len(args) == 1:
        bucket_name = args[0]
    #elif len(args) == 0:
    else:
        bucket_name = s3up.AWS_DEFAULT_BUCKET

    if s3up.BUCKET_CNAME:
        host_path = s3up.BUCKET_CNAME
    else:
        host_path = "https://s3.amazonaws.com/%s" % bucket_name

    searchstr = raw_input("Look for files containing:\n")
    print

    print "Searching '%s' for '%s'..." % (bucket_name, searchstr)
    print

    s3 = S3Connection(
        aws_access_key_id=s3up.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=s3up.AWS_SECRET_ACCESS_KEY,
        host=s3up.S3_ENDPOINT
    )
    bucket = s3.get_bucket(bucket_name)
    for k in bucket.list():
        if unicode(searchstr) in k.name:
            print "%s/%s" % (host_path, k.name)
    print
    raw_input("Press enter to continue...")

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except Exception as e:
        sys.stderr.write('\n')
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write('\n')
        print sys.argv[1:]
        raw_input("Press enter to continue...")
        sys.exit(1)
