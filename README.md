# Inventory Management System 📦

A robust inventory management system built with Streamlit and AWS services, featuring user authentication, image storage, and real-time inventory tracking.

## Features 🚀

### User Authentication
- Email-based signup and login using AWS Cognito
- Email verification for new accounts
- Secure password management

### Inventory Management
- Add, edit, and delete inventory items
- Upload and manage product images
- Track quantity and pricing
- Categorize items for better organization
- User-specific inventory views

### User Interface
- Clean, responsive design using Streamlit
- Multiple view options (List/Grid view)
- Interactive charts and statistics
- Category-based filtering
- Quantity-based filtering

### Data Visualization
- Category distribution pie charts
- Stock level bar charts
- Real-time inventory statistics

## Technology Stack 💻

- **Frontend:** Streamlit (Python-based UI framework)
- **Authentication:** AWS Cognito
- **Database:** AWS DynamoDB
- **Storage:** AWS S3 (for product images)
- **Backend:** Python with boto3 SDK

## Prerequisites 📋

- Python 3.8 or higher
- AWS Account with appropriate permissions
- Required AWS services set up:
  - Cognito User Pool
  - DynamoDB Table
  - S3 Bucket
  - IAM User with necessary permissions

## Installation 🔧

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tarungatla/CCL_Miniproject.git
   cd CCL_Miniproject
  
2. **Install required packages:**
    ```bash
    pip install -r requirements.txt

3. **Create a .env file in the root directory with your AWS credentials:**
    ```bash
    AWS_ACCESS_KEY_ID=your_access_key
    AWS_SECRET_ACCESS_KEY=your_secret_key
    AWS_REGION=your_region
    COGNITO_USER_POOL_ID=your_user_pool_id
    COGNITO_CLIENT_ID=your_client_id
    DYNAMODB_TABLE_NAME=Inventory
    S3_BUCKET_NAME=your_bucket_name
    LOW_STOCK_THRESHOLD=10


4. **Run the application:**
    ```bash
    streamlit run app.py
  