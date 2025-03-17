import boto3
from datetime import datetime
import uuid
from config.aws_config import AWS_CONFIG, DYNAMODB_CONFIG

class DynamoDBOperations:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', **AWS_CONFIG)
        self.table = self.dynamodb.Table(DYNAMODB_CONFIG['table_name'])

    def add_item(self, name, category, quantity, price, image_url):
        item = {
            'ItemID': str(uuid.uuid4()),
            'Name': name,
            'Category': category,
            'Quantity': quantity,
            'Price': price,
            'ImageURL': image_url,
            'Timestamp': datetime.utcnow().isoformat()
        }
        self.table.put_item(Item=item)
        return item['ItemID']

    def get_items(self, category=None):
        if category:
            response = self.table.scan(
                FilterExpression='Category = :cat',
                ExpressionAttributeValues={':cat': category}
            )
        else:
            response = self.table.scan()
        return response.get('Items', [])

    def update_item(self, item_id, updates):
        update_expression = "SET "
        expression_values = {}
        
        for key, value in updates.items():
            update_expression += f"#{key} = :{key}, "
            expression_values[f":{key}"] = value
        
        update_expression = update_expression[:-2]
        
        self.table.update_item(
            Key={'ItemID': item_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames={f"#{k}": k for k in updates.keys()}
        )

    def delete_item(self, item_id):
        self.table.delete_item(
            Key={'ItemID': item_id}
        ) 