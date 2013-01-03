# coding=utf-8
# Shared config options for Python scripts in this directory.
# Copy this file to 'dotfiles_config.py' and set the options below to use this.

# s3up, s3up-private, s3up-dir, s3-genlink, s3-clear-multipart-uploads.py
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_DEFAULT_BUCKET = ''
S3_ENDPOINT = 's3.amazonaws.com'

# s3up, s3up-private, s3up-dir, s3-genlink
BUCKET_CNAME = ''

# Options for s3up & s3up-dir, for files larger than 5MB:
UPLOAD_PARALLELIZATION = 4
CHUNK_SIZE = 5242880 # (Note: must be >= 5242880 (5MB))
CHUNK_RETRIES = 10

# s3up-private, s3-genlink
import hashlib
DEFAULT_EXPIRES = 3600
FILENAME_HASHER = hashlib.sha224
