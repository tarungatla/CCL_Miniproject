import boto3
from config.aws_config import AWS_CONFIG, S3_CONFIG

class S3Operations:
    def __init__(self):
        self.s3 = boto3.client('s3', **AWS_CONFIG)
        self.bucket_name = S3_CONFIG['bucket_name']
    
    def upload_file(self, file_obj, file_name):
        try:
            # Upload without ACL parameter
            self.s3.upload_fileobj(
                file_obj,
                self.bucket_name,
                f"inventory/{file_name}"
            )
            return f"https://{self.bucket_name}.s3.amazonaws.com/inventory/{file_name}"
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def delete_file(self, file_name):
        try:
            self.s3.delete_object(
                Bucket=self.bucket_name,
                Key=f"inventory/{file_name}"
            )
        except Exception as e:
            raise Exception(f"Failed to delete file: {str(e)}")