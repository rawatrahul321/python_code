"""
    s3-storage.models
    ~~~~~~~~~~~~~~~~~
    Use s3 as file storage mechanism
    :copyright: (c) 2017 by Marc Lijour, brolycjw.
    :license: MIT License, see LICENSE for more details.
"""

import hashlib
import base64

from odoo import models

from . import s3_helper
from odoo import api


class S3Attachment(models.Model):
    """Extends ir.attachment to implement the S3 storage engine
    """
    _inherit = "ir.attachment"

    def _connect_to_S3_bucket(self, s3, bucket_name):
        s3_bucket = s3.Bucket(bucket_name)
        exists = s3_helper.bucket_exists(s3, bucket_name)

        if not exists:
            s3_bucket = s3.create_bucket(Bucket=bucket_name)
        return s3_bucket

    def _file_read(self, fname, bin_size=False):
        storage = self._storage()
        if storage[:5] == 's3://':
            access_key_id, secret_key, bucket_name, encryption_enabled = s3_helper.parse_bucket_url(storage)

            s3 = s3_helper.get_resource(access_key_id, secret_key)
            s3_bucket = self._connect_to_S3_bucket(s3, bucket_name)
            file_exists = s3_helper.object_exists(s3, s3_bucket.name, fname)
            if not file_exists:
                # Some old files (prior to the installation of odoo-s3) may
                # still be stored in the file system even though
                # ir_attachment.location is configured to use S3
                try:
                    read = super(S3Attachment, self)._file_read(fname, bin_size=False)
                except Exception:
                    # Could not find the file in the file system either.
                    return False
            else:
                s3_key = s3.Object(s3_bucket.name, fname)
                read = base64.b64encode(s3_key.get()['Body'].read())
        else:
            read = super(S3Attachment, self)._file_read(fname, bin_size=False)
            print("_________________________read",read)
        return read

    # @api.model
    # def create(self, values):
    #     storage = self._storage()
    #     print("------------------------------storage------------",storage)
    #     if storage[:5] == 's3://':
    #         fname = self.s3_file_write(values.get("datas"))
    #         values["datas"]=fname
    #         self.browse().check('write', values=values)
    #
    #         return super(S3Attachment, self).create(values)
    #     else:
    #         for field in ('file_size', 'checksum'):
    #             values.pop(field, False)
    #         values = self._check_contents(values)
    #         self.browse().check('write', values=values)
    #         return super(S3Attachment, self).create(values)


    def s3_file_write(self, value):
        storage = self._storage()
        if storage[:5] == 's3://':
            access_key_id, secret_key, bucket_name, encryption_enabled = s3_helper.parse_bucket_url(storage)

            print("--------access_key_id----------%r",access_key_id)
            print("--------secret_key----------%r",secret_key)
            print("--------bucket_name----------%r",bucket_name)
            print("--------encryption_enabled----------%r",encryption_enabled)
            s3 = s3_helper.get_resource(access_key_id, secret_key)
            s3_bucket = self._connect_to_S3_bucket(s3, bucket_name)
            bin_value = base64.b64decode(value)
            fname = hashlib.sha1(bin_value).hexdigest()
            print("-------------fname---------%r",dir(s3_bucket))
            if encryption_enabled:
                t = s3.Object(s3_bucket.name, fname).put(Body=bin_value, ServerSideEncryption='AES256')

            else:
                t = s3.Object(s3_bucket.name, fname).put(Body=bin_value)
                print("=====================================t========================",dir(t),"-------------------------------",t.values()[0])
            url = 'https://%s.s3.amazonaws.com/%s' % (bucket_name,t.values()[0][1:-1])
            print("----------------url-------------------------------",url)


        return fname
