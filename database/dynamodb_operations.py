import boto3
from datetime import datetime
import uuid
from config.aws_config import AWS_CONFIG, DYNAMODB_CONFIG
from decimal import Decimal

class DynamoDBOperations:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', **AWS_CONFIG)
        self.table = self.dynamodb.Table(DYNAMODB_CONFIG['table_name'])

    def add_item(self, name, category, quantity, price, image_url="", user_email=""):
        # This method should store the image_url in the item record
        item_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        item = {
            'ItemID': item_id,
            'Name': name,
            'Category': category,
            'Quantity': int(quantity),
            'Price': price,
            'ImageURL': str(image_url),  # Store the S3 URL
            'UserEmail': user_email,  # Add user email
            'Timestamp': timestamp
        }
        
        # Add to DynamoDB table
        self.table.put_item(Item=item)
        return item_id

    def get_items(self, category=None, user_email=None):
        """Get items with optional filtering by category and user email"""
        filter_expression = None
        expression_values = {}
        expression_names = {}

        # Build filter expression
        if category and user_email:
            filter_expression = '#category = :cat AND #email = :email'
            expression_values = {':cat': category, ':email': user_email}
            expression_names = {'#category': 'Category', '#email': 'UserEmail'}
        elif category:
            filter_expression = '#category = :cat'
            expression_values = {':cat': category}
            expression_names = {'#category': 'Category'}
        elif user_email:
            filter_expression = '#email = :email'
            expression_values = {':email': user_email}
            expression_names = {'#email': 'UserEmail'}

        # Execute scan with appropriate filters
        if filter_expression:
            response = self.table.scan(
                FilterExpression=filter_expression,
                ExpressionAttributeValues=expression_values,
                ExpressionAttributeNames=expression_names
            )
        else:
            response = self.table.scan()
        
        return response.get('Items', [])

    def update_item(self, item_id, updates):
        """Update an existing item in DynamoDB"""
        update_expression = "SET "
        expression_attribute_values = {}
        expression_attribute_names = {}
        
        for key, value in updates.items():
            # Add to update expression
            update_expression += f"#{key} = :{key}, "
            # Add to expression attribute names
            expression_attribute_names[f"#{key}"] = key
            # Add to expression attribute values
            # Convert numbers to Decimal for DynamoDB
            if isinstance(value, (int, float)):
                value = Decimal(str(value))
            expression_attribute_values[f":{key}"] = value
        
        # Add timestamp to update
        update_expression += "#Timestamp = :timestamp"
        expression_attribute_names["#Timestamp"] = "Timestamp"
        expression_attribute_values[":timestamp"] = datetime.now().isoformat()
        
        try:
            self.table.update_item(
                Key={'ItemID': item_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to update item: {str(e)}")

    def delete_item(self, item_id):
        self.table.delete_item(
            Key={'ItemID': item_id}
        ) 