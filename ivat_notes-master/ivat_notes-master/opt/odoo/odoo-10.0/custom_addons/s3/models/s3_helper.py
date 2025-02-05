# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
    s3_helper.py
    ~~~~~~~~~~~~~~~~~
    Helper functions for models.py
    :copyright: (c) 2017 by Marc Lijour, brolycjw.
    :license: MIT License, see LICENSE for more details.
"""

import boto3
# uncomment for debug mode:
#boto3.set_stream_logger('')
import botocore
from boto3.session import Session
from boto3.s3.transfer import S3Transfer

def parse_bucket_url(bucket_url):
    scheme = bucket_url[:5]
    print(scheme)
    assert scheme == 's3://', \
        "Expecting an s3:// scheme, got {} instead.".format(scheme)

    # scheme:
    # s3://<Your-AWS-Access-Key-ID>:<Your-AWS-Secret-Key>@<Your-S3-Bucket-name>+SSE
    # where +SSE is optional (meaning server-side encryption enabled)

    try:
        encryption_enabled = True
        remain = bucket_url.lstrip(scheme)
        access_key_id = remain.split(':')[0]
        remain = remain.lstrip(access_key_id).lstrip(':')
        secret_key = remain.split('@')[0]
        remain = remain.lstrip(secret_key).lstrip('@').split('+')
        bucket_name = remain[0]
        encryption_enabled = len(remain) > 1

        if not access_key_id or not secret_key:
            raise Exception(
                "No AWS access and secret keys were provided."
                " Unable to establish a connexion to S3."
            )
    except Exception:
        raise Exception("Unable to parse the S3 bucket url.")

    return (access_key_id, secret_key, bucket_name, encryption_enabled)


def bucket_exists(s3, bucket_name):
    print("+++++++++++++++++++++++++++++++++++++++++++++++++",bucket_name)
    exists = True
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            exists = False
    return exists


def object_exists(s3, bucket_name, key):
    print("+++++++++++++++++++++++++++++++++++++++++++++++++",bucket_name,key)
    exists = True
    try:
        s3.meta.client.head_object(Bucket=bucket_name, Key=key)


    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            exists = False
    return exists


def get_resource(access_key_id, secret_key):
    session = Session(access_key_id, secret_key)
    s3 = session.resource('s3')
    return s3

# extra: works for files stored in the file system
# (not called by models.py which only deal with in-memory)
def upload(value, storage):
    access_key_id, secret_key, bucket_name, encryption_enabled = parse_bucket_url(storage)
    s3 = get_resource(access_key_id, secret_key)
    ### S3Transfer allows multi-part, call backs etc
    # http://boto3.readthedocs.io/en/latest/_modules/boto3/s3/transfer.html
    transfer = S3Transfer(s3.meta.client)
    if encryption_enabled:
        transfer.upload_file(value, bucket_name, value, extra_args={'ServerSideEncryption': 'AES256'})
    else:
        transfer.upload_file(value, bucket_name, value)
