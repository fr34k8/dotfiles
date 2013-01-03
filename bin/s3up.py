#!/usr/bin/env python
# coding=utf-8
"""
s3up.py
An Amazon S3 uploader that uses MultiPart (chunked) uploads and parallelization
to improve upload speed for files >= 5 MB.

Copyright 2010-2013, Mike Tigas
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
  s3up filename
    Uploads the given file to the AWS_DEFAULT_BUCKET (see below)
    with the following key:
        files/YYYYMMDD/(filename)

  s3up filename [remote_directory]
    As above, except to the given directory:
        (remote_directory)/(filename)

  s3up filename [bucket] [remote_filename] [cache_time]
  s3up filename [bucket] [remote_filename] [cache_time] [policy]


Please double-check and set the following options below before using:
  AWS_ACCESS_KEY_ID (also accepted as an env var)
  AWS_SECRET_ACCESS_KEY (also accepted as an env var)
  AWS_DEFAULT_BUCKET (also accepted as an env var)
  S3_ENDPOINT
  UPLOAD_PARALLELIZATION
  CHUNK_SIZE
  CHUNK_RETRIES
(Note, you can also set these in `dotfiles_config.py` -- see example file.
That file overrides identical AWS_* environment variables.)
"""
from __future__ import print_function
import os
import sys
import traceback
from boto.s3.connection import S3Connection
from cStringIO import StringIO
from datetime import datetime
from math import ceil, floor
from mimetypes import guess_type
from threading import Thread
from time import sleep

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')

# When only giving one or two args, the following bucket is used:
AWS_DEFAULT_BUCKET = os.environ.get('AWS_DEFAULT_BUCKET', '')

# Default is "s3.amazonaws.com", for US Standard (auto routing
# to N. Virginia or Pacific Northwest). See following link to ensure
# you set this properly if you are using another region or if you wish to
# manually use a specific sub-endpoint like "s3-external-1.amazonaws.com"
# (manual domain for N. Virginia):
# http://docs.amazonwebservices.com/general/latest/gr/rande.html#s3_region
S3_ENDPOINT = "s3.amazonaws.com"

# If you have a CNAME for this bucket (or, even better, a CNAME for a
# CloudFront for this bucket) you can throw that in here, with the protocol you
# want to use. This will be used to print the URI for resulting uploads.
#BUCKET_CNAME = "http://s3_media.example.com"
#BUCKET_CNAME = "https://d312sd4f87pfh0.cloudfront.net"
BUCKET_CNAME = None

# Number of simultaneous upload threads to execute.
UPLOAD_PARALLELIZATION = 4

# Default size for a file chunk (excluding final chunk). A file will need
# to be larger than this size to enable parallelized upload. (Since S3
# only supports 10,000 chunks, extremely large files will automatically
# adjust this value to end up with 10,000 chunks at most.)
# Note: must be >= 5242880 (5MB)
CHUNK_SIZE = 5242880

# For robustness, we can retry uploading any chunk up to this many times. (Set
# to 1 or less to only attempt one upload per chunk.) Because we chunk large
# uploads, an error in a single chunk doesn't necessarily mean we need to
# re-upload the entire file.
CHUNK_RETRIES = 10

# Load/override options from optional `dotfiles_config.py` file.
OPTIONS = set(['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
    'AWS_DEFAULT_BUCKET', 'S3_ENDPOINT', 'BUCKET_CNAME',
    'UPLOAD_PARALLELIZATION', 'CHUNK_SIZE', 'CHUNK_RETRIES'])
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

# ========== "MultiPart" (chunked) upload utility methods ==========

def mem_chunk_file(local_file):
    """
    Given the file at `local_file`, returns a generator of CHUNK_SIZE
    (default 5MB) StringIO file-like chunks for that file.
    """
    fstat = os.stat(local_file)
    fsize = fstat.st_size

    chunk_size = CHUNK_SIZE
    num_chunks = max(int(floor(float(fsize) / float(chunk_size))), 1)
    if num_chunks > 10000:
        # File would require too many chunks. Make each chunk larger instead.
        chunk_size = int(ceil(float(fsize) / 10000.0))
        chunk_size = int(1024.0 * ceil(chunk_size / 1024.0))  # round up to nearest 1KB
        num_chunks = int(ceil(float(fsize) / float(chunk_size)))

    fp = open(local_file, 'rb')
    for i in range(num_chunks):
        tfp = StringIO()
        if i == (num_chunks - 1):
            # remaining data
            size_hint = fsize - (chunk_size * (num_chunks - 1))
        else:
            size_hint = chunk_size

        tfp.write(fp.read(size_hint))
        tfp.seek(0)
        yield tfp
    fp.close()


def upload_worker(multipart_key, fp, index, headers=None):
    """
    Uploads a file chunk in a MultiPart S3 upload. If an error occurs uploading
    this chunk, retry up to `CHUNK_RETRIES` times.
    """
    success = False
    attempts = 0
    while not success:
        try:
            fp.seek(0)
            multipart_key.upload_part_from_file(fp, index, headers=headers)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            success = False

            attempts += 1
            if attempts >= CHUNK_RETRIES:
                break

            sleep(0.5)
        else:
            success = True

    if not success:
        raise Exception("Upload of chunk %d failed after 5 retries." % index)

    fp.close()


def upload_chunk(arg_list):
    thread = Thread(
        target=upload_worker,
        args=arg_list
    )
    thread.daemon = False
    thread.start()
    return thread


# ========== Uploader methods ==========

def easy_up(local_file, rdir=None):
    if os.path.isfile(local_file):
        #print("File:", file=sys.stderr)
        #print(os.path.abspath(local_file), file=sys.stderr)
        #print(file=sys.stderr)

        if not rdir:
            rpath = "files/" + datetime.now().strftime("%Y%m%d")
        else:
            rpath = rdir
        remote_path = rpath + "/" + os.path.basename(local_file)

        upload_file(
            os.path.abspath(local_file), AWS_DEFAULT_BUCKET, remote_path, 0
        )

        #print("File uploaded to:", file=sys.stderr)
        if BUCKET_CNAME:
            print("%s/%s" % (BUCKET_CNAME, remote_path))
        else:
            print("https://%s/%s/%s" % (
                S3_ENDPOINT, AWS_DEFAULT_BUCKET, remote_path
            ))

        #print(file=sys.stderr)
    else:
        print("Path given is not a file.", file=sys.stderr)


def upload_file(local_file, bucket, remote_path, cache_time=0, policy="public-read", force_download=False):
    # Expiration time:
    cache_time = int(cache_time)

    # Metadata that we need to pass in before attempting an upload.
    content_type = guess_type(local_file, False)[0] \
        or "application/octet-stream"
    basic_headers = {
        "Content-Type": content_type,
    }
    if force_download:
        basic_headers["Content-Disposition"] = \
            "attachment; filename=%s" % os.path.basename(local_file)

    s3 = S3Connection(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        host=S3_ENDPOINT
    )
    bucket = s3.get_bucket(bucket)

    mp_key = bucket.initiate_multipart_upload(
        remote_path,
        headers=basic_headers
    )

    active_threads = []
    try:
        # Chunk the given file into `CHUNK_SIZE` (default: 5MB) chunks
        # that can be uploaded in parallel.
        chunk_generator = mem_chunk_file(local_file)

        # Use `UPLOAD_PARALLELIZATION` (default: 4) threads at a time to
        # churn through the `chunk_generator` queue.
        for i, chunk in enumerate(chunk_generator):
            args = (mp_key, chunk, i + 1, basic_headers)

            # If we don't have enough concurrent threads yet, spawn an upload
            # thread to handle this chunk.
            if len(active_threads) < UPLOAD_PARALLELIZATION:
                # Upload this chunk in a background thread and hold on to the
                # thread for polling.
                t = upload_chunk(args)
                active_threads.append(t)

            # Poll until an upload thread finishes before allowing more upload
            # threads to spawn.
            while len(active_threads) >= UPLOAD_PARALLELIZATION:
                for thread in active_threads:
                    # Kill threads that have been completed.
                    if not thread.isAlive():
                        thread.join()
                        active_threads.remove(thread)

                # a polling delay since there's no point in constantly waiting
                # and taxing CPU
                sleep(0.1)

        # We've exhausted the queue, so join all of our threads so that we wait
        # on the last pieces to complete uploading.
        for thread in active_threads:
            thread.join()
    except:
        # Since we have threads running around and possibly partial data up on
        # the server, we need to clean up before propogating an exception.
        sys.stderr.write("Exception! Waiting for existing child threads to " \
            "stop.\n\n")
        for thread in active_threads:
            thread.join()

        # Remove any already-uploaded chunks from the server.
        mp_key.cancel_upload()
        for mp in bucket.list_multipart_uploads():
            if mp.key_name == remote_path:
                mp.cancel_upload()

        # Propogate the error.
        raise
    else:
        # We finished the upload successfully.
        mp_key.complete_upload()
        key = bucket.get_key(mp_key.key_name)

    # ===== / chunked upload =====

    if cache_time != 0:
        key.set_metadata(
            'Cache-Control',
            'max-age=%d, must-revalidate' % int(cache_time)
        )
    else:
        key.set_metadata('Cache-Control', 'no-cache, no-store')

    if policy == "public-read":
        key.make_public()
    else:
        key.set_canned_acl(policy)


def print_help():
    print("An Amazon S3 uploader that uses MultiPart (chunked) uploads " \
        "and parallelization to improve upload speed for files >= 5 MB.")
    print()
    print("Usage:")
    print("s3up filename")
    print("    Uploads the given file to AWS_DEFAULT_BUCKET (%s) at the following path:" % AWS_DEFAULT_BUCKET)
    print("      files/YYYYMMDD/(filename)")
    print()
    print("s3up filename [remote_directory]")
    print("    As above, except the file is uploaded to the given directory:")
    print("      (remote_directory)/(filename)")
    print()
    print("s3up filename [bucket] [remote_filename] [cache_time]")
    print()
    print("s3up filename [bucket] [remote_filename] [cache_time] [policy]")


def main(args):
    if len(args) == 5:
        upload_file(args[0], args[1], args[2], args[3], args[4])
    elif len(args) == 4:
        upload_file(args[0], args[1], args[2], args[3])
    elif len(args) == 3:
        upload_file(args[0], args[1], args[2])
    elif len(args) == 2:
        easy_up(args[0], args[1])
    elif len(args) == 1:
        if (args[0] == "--help") or (args[0] == "-h") or (args[0] == "-?"):
            print_help()
        else:
            easy_up(args[0], None)
    else:
        print_help()

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except Exception, e:
        sys.stderr.write('\n')
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write('\n')
        sys.exit(1)
