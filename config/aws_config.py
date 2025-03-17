import os
from dotenv import load_dotenv

load_dotenv()

AWS_CONFIG = {
    'region_name': os.getenv('AWS_REGION', 'us-east-1'),
    'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
    'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY')
}

# Cognito Configuration
COGNITO_CONFIG = {
    'user_pool_id': os.getenv('COGNITO_USER_POOL_ID'),
    'client_id': os.getenv('COGNITO_CLIENT_ID')
}

# DynamoDB Configuration
DYNAMODB_CONFIG = {
    'table_name': os.getenv('DYNAMODB_TABLE_NAME', 'Inventory')
}

# S3 Configuration
S3_CONFIG = {
    'bucket_name': os.getenv('S3_BUCKET_NAME'),
    'allowed_extensions': ['jpg', 'jpeg', 'png']
}

# SNS Configuration
SNS_CONFIG = {
    'topic_arn': os.getenv('SNS_TOPIC_ARN'),
    'low_stock_threshold': int(os.getenv('LOW_STOCK_THRESHOLD', 10))
} 