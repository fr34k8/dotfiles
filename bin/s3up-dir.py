#!/usr/bin/python
# coding=utf-8
"""
s3up-dir.py

Same as `s3up`, but recursively uploads an entire directory into S3.
See `s3up.py`

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
  s3up-dir local_directory remote_directory

Before using, please configure at least the following options in `s3up.py`:
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    DEFAULT_BUCKET
    BUCKET_CNAME
(Note, you can also set these in `dotfiles_config.py` -- see example file.)
"""
import sys
import traceback
import os
import s3up
from socket import setdefaulttimeout
setdefaulttimeout(100.0)

def upload_dir(local_dir, remote_dir, bucket=None, bucket_url=None):
    if not bucket:
        bucket = s3up.DEFAULT_BUCKET
    for root, dirs, files in os.walk(local_dir):
        for f in files:
            fullfile = os.path.join(root, f).strip()
            remotefile = fullfile.replace(local_dir,'').strip()
            if remote_dir:
                remotefile = remote_dir+"/"+remotefile
            if remotefile[0] == "/":
                remotefile = remotefile[1:]
            if (remotefile.find('.svn') == -1) and \
                (remotefile.find('.svn-base') == -1) and \
                (remotefile.find('.DS_Store') == -1) and \
                (remotefile.find('.pyo') == -1) and \
                (remotefile.find('.pyc') == -1):
                    s3up.upload_file(fullfile,bucket,remotefile)
                    if not bucket_url:
                        print "https://s3.amazonaws.com/%s/%s" % (bucket,remotefile)
                    else:
                        print "%s%s" % (bucket_url,remotefile)

def main(args):
    if len(args) == 2:
        local_dir = os.path.abspath(args[0])
        if not os.path.isdir(local_dir):
            print "First argument is not a valid local directory."
            sys.exit(1)
        upload_dir(local_dir,"files/"+args[1], s3up.DEFAULT_BUCKET, s3up.BUCKET_CNAME)
    else:
        print "Usage:"
        print "s3up-dir local_directory remote_directory"
        sys.exit(1)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except Exception, e:
        sys.stderr.write('\n')
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write('\n')
        print sys.argv[1:]
        sys.exit(1)
