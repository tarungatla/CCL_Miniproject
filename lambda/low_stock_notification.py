import boto3
import json
import os
from datetime import datetime

def lambda_handler(event, context):
    # Initialize AWS clients
    dynamodb = boto3.resource('dynamodb')
    sns = boto3.client('sns')
    
    # Get environment variables
    table_name = os.environ['DYNAMODB_TABLE_NAME']
    topic_arn = os.environ['SNS_TOPIC_ARN']
    low_stock_threshold = int(os.environ.get('LOW_STOCK_THRESHOLD', 10))
    
    try:
        # Get items with low stock
        table = dynamodb.Table(table_name)
        response = table.scan(
            FilterExpression='#qty <= :threshold',
            ExpressionAttributeNames={
                '#qty': 'Quantity'
            },
            ExpressionAttributeValues={
                ':threshold': low_stock_threshold
            }
        )
        
        low_stock_items = response.get('Items', [])
        
        if low_stock_items:
            # Prepare notification message
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"⚠️ Low Stock Alert - {current_time}\n\n"
            message += "The following items are running low:\n\n"
            
            for item in low_stock_items:
                message += (
                    f"• {item['Name']} ({item['Category']})\n"
                    f"  Current Stock: {item['Quantity']}\n"
                    f"  Price: ₹{item['Price']:.2f}\n"
                    f"  Item ID: {item['ItemID']}\n\n"
                )
            
            # Send SNS notification
            sns.publish(
                TopicArn=topic_arn,
                Message=message,
                Subject='Low Inventory Alert',
                MessageAttributes={
                    'AlertType': {
                        'DataType': 'String',
                        'StringValue': 'LowStock'
                    },
                    'ItemCount': {
                        'DataType': 'Number',
                        'StringValue': str(len(low_stock_items))
                    }
                }
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Low stock notification sent successfully',
                    'itemsAffected': len(low_stock_items)
                })
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No items are currently low in stock',
                    'itemsAffected': 0
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 