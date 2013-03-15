#!/usr/bin/env python
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
    AWS_DEFAULT_BUCKET
    S3_ENDPOINT
    BUCKET_CNAME
(Note, you can also set these in `dotfiles_config.py` -- see example file.)
"""
import sys
import traceback
import os
import s3up
from boto.s3.connection import S3Connection
from socket import setdefaulttimeout
setdefaulttimeout(100.0)

# TODO
# note: not compatible with multipart (parallelized) upload due to
# different etag calculation.
# see https://forums.aws.amazon.com/thread.jspa?messageID=203436
USE_DELTA_UPLOAD = False

def should_upload_file(local_file_path, bucket, remote_file_path):
    """
    Logic to handle skipping file uploads.

    * Skip temporary / cache-like files.
    """
    if not (
        (remote_file_path.find('.svn') == -1) and
        (remote_file_path.find('.svn-base') == -1) and
        (remote_file_path.find('.DS_Store') == -1) and
        (remote_file_path.find('.pyo') == -1) and
        (remote_file_path.find('.pyc') == -1)
    ):
        return False

    # TODO
    if USE_DELTA_UPLOAD:
        s3 = S3Connection(
            aws_access_key_id=s3up.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=s3up.AWS_SECRET_ACCESS_KEY,
            host=s3up.S3_ENDPOINT
        )
        bucket_obj = s3.get_bucket(bucket)
        key = bucket_obj.get_key(remote_file_path) or None
        if key and getattr(key, 'etag', None):
            local_hash = None
            try:
                with open(local_file_path, 'rb') as f_obj:
                    local_hash = key.compute_md5(f_obj)
            except:
                pass
            etag = key.etag.strip('"').strip("'")
            print "local file: ", local_file_path
            print "local hash: ", local_hash[0]
            print "remote file: ", remote_file_path
            print "remote etag: ", etag
            if local_hash and (etag == local_hash[0]):
                return False
        else:
            return True

    return True

def upload_dir(local_dir, remote_dir, bucket=None, bucket_url=None):
    if not bucket:
        bucket = s3up.AWS_DEFAULT_BUCKET

    for root, dirs, files in os.walk(local_dir):
        for f in files:
            fullfile = os.path.join(root, f).strip()
            remotefile = fullfile.replace(local_dir,'').strip()
            if remote_dir:
                remotefile = remote_dir+"/"+remotefile
            if remotefile[0] == "/":
                remotefile = remotefile[1:]
            if should_upload_file(fullfile, bucket, remotefile):
                if not USE_DELTA_UPLOAD:
                    # cannot use multipart with deltas
                    s3up.upload_file(fullfile, bucket, remotefile)
                else:
                    # TODO
                    s3 = S3Connection(
                        aws_access_key_id=s3up.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=s3up.AWS_SECRET_ACCESS_KEY,
                        host=s3up.S3_ENDPOINT
                    )
                    bucket_obj = s3.get_bucket(bucket)
                    key = bucket_obj.get_key(remotefile) or bucket_obj.new_key(remotefile)
                    key.set_contents_from_filename(fullfile,
                        policy="public-read")
                    key.make_public()
                if not bucket_url:
                    print "https://s3.amazonaws.com/%s/%s" % (bucket,remotefile)
                else:
                    print "%s%s" % (bucket_url,remotefile)
            else:
                print "Skipped %s" % remotefile


def main(args):
    if len(args) == 2:
        local_dir = os.path.abspath(args[0])
        if not os.path.isdir(local_dir):
            print "First argument is not a valid local directory."
            sys.exit(1)
        upload_dir(local_dir,"files/"+args[1], s3up.AWS_DEFAULT_BUCKET, s3up.BUCKET_CNAME)
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
