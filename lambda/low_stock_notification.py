import boto3
import json
import os
from datetime import datetime
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def lambda_handler(event, context):
    # Initialize AWS clients
    dynamodb = boto3.resource('dynamodb')
    ses = boto3.client('ses')  # Amazon SES for sending emails
    
    # Get environment variables
    table_name = os.environ['DYNAMODB_TABLE_NAME']
    sender_email = os.environ['SENDER_EMAIL']  # Verified SES email
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
            # Group items by owner email
            items_by_owner = {}
            for item in low_stock_items:
                user_email = item.get('UserEmail', '')
                if user_email:
                    if user_email not in items_by_owner:
                        items_by_owner[user_email] = []
                    items_by_owner[user_email].append(item)
            
            # Send emails to each owner
            emails_sent = 0
            for owner_email, items in items_by_owner.items():
                # Prepare email message
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                subject = f"Low Stock Alert - {current_time}"
                
                # Create HTML message
                html_message = f"""
                <html>
                <head></head>
                <body>
                    <h2>⚠️ Low Stock Alert</h2>
                    <p>The following items you own are running low and need attention:</p>
                    <table border="1" cellpadding="5" style="border-collapse: collapse;">
                        <tr style="background-color: #f2f2f2;">
                            <th>Item Name</th>
                            <th>Category</th>
                            <th>Current Stock</th>
                            <th>Price (₹)</th>
                            <th>Item ID</th>
                        </tr>
                """
                
                # Add each item to the table
                for item in items:
                    html_message += f"""
                        <tr>
                            <td>{item['Name']}</td>
                            <td>{item['Category']}</td>
                            <td style="color: red; font-weight: bold;">{item['Quantity']}</td>
                            <td>{item['Price']:.2f}</td>
                            <td>{item['ItemID']}</td>
                        </tr>
                    """
                
                html_message += """
                    </table>
                    <p>Please restock these items soon to avoid stockouts.</p>
                    <p>Thank you!</p>
                </body>
                </html>
                """
                
                # Create plain text version as well
                text_message = f"Low Stock Alert - {current_time}\n\n"
                text_message += "The following items you own are running low:\n\n"
                
                for item in items:
                    text_message += (
                        f"• {item['Name']} ({item['Category']})\n"
                        f"  Current Stock: {item['Quantity']}\n"
                        f"  Price: ₹{item['Price']:.2f}\n"
                        f"  Item ID: {item['ItemID']}\n\n"
                    )
                
                # Create multipart message
                message = MIMEMultipart('alternative')
                message['Subject'] = subject
                message['From'] = sender_email
                message['To'] = owner_email
                
                # Attach parts
                part1 = MIMEText(text_message, 'plain')
                part2 = MIMEText(html_message, 'html')
                message.attach(part1)
                message.attach(part2)
                
                # Send email using Amazon SES
                response = ses.send_raw_email(
                    Source=sender_email,
                    Destinations=[owner_email],
                    RawMessage={
                        'Data': message.as_string()
                    }
                )
                emails_sent += 1
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Low stock notifications sent successfully',
                    'emailsSent': emails_sent,
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