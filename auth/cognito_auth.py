import os
import boto3
import logging
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CognitoAuth:
    def __init__(self):
        """Initialize the Cognito client and verify configuration."""
        try:
            # Load environment variables
            self.user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
            self.client_id = os.getenv("COGNITO_CLIENT_ID")
            aws_region = os.getenv("AWS_REGION", "ap-south-1")  # Default to ap-south-1 if not set

            # AWS Configuration
            self.client = boto3.client('cognito-idp', region_name=aws_region)

            if not self.user_pool_id or not self.client_id:
                raise ValueError("Cognito configuration is missing. Ensure environment variables are set.")


            print(f"User Pool ID: {self.user_pool_id}")
            print(f"Client ID: {self.client_id}")
            print(f"Region: {os.getenv('AWS_REGION')}")
            # Verify Cognito Configuration on initialization
            valid, message = self.verify_configuration()
            if not valid:
                logger.error(f"Cognito Configuration Error: {message}")

        except Exception as e:
            logger.error(f"Failed to initialize Cognito client: {str(e)}")
            raise

    def sign_up(self, email, password, email_attr):
        """Registers a new user in the Cognito User Pool using email as username."""
        try:
            response = self.client.sign_up(
                ClientId=self.client_id,
                Username=email,  # Use email as username
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email_attr}
                ]
            )
            logger.info(f"User {email} registered successfully.")
            return True, "User registration successful"
        except self.client.exceptions.UsernameExistsException:
            return False, "Email already registered"
        except Exception as e:
            return False, f"Registration error: {str(e)}"

    def sign_in(self, email, password):
        """Signs in a user using their email."""
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,  # Use email as username
                    'PASSWORD': password
                }
            )
            logger.info(f"User {email} logged in successfully.")
            return True, response['AuthenticationResult']
        except Exception as e:
            return False, str(e)

    def verify_token(self, token):
        """Validates an access token and retrieves user information."""
        try:
            response = self.client.get_user(AccessToken=token)
            return True, response

        except self.client.exceptions.NotAuthorizedException:
            return False, "Token is invalid or expired."
        except ClientError as e:
            return False, f"AWS Error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def verify_configuration(self):
        """Checks if the Cognito configuration is valid."""
        try:
            self.client.describe_user_pool_client(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id
            )
            return True, "Cognito configuration is valid."

        except self.client.exceptions.ResourceNotFoundException:
            return False, "Invalid Cognito configuration. User pool client does not exist."
        except ClientError as e:
            return False, f"AWS Error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def confirm_sign_up(self, email, confirmation_code):
        """Confirms user registration with verification code."""
        try:
            response = self.client.confirm_sign_up(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=confirmation_code
            )
            logger.info(f"User {email} verified successfully.")
            return True, "Email verified successfully"
        except self.client.exceptions.CodeMismatchException:
            return False, "Invalid verification code"
        except self.client.exceptions.ExpiredCodeException:
            return False, "Verification code has expired"
        except self.client.exceptions.UserNotFoundException:
            return False, "User not found"
        except Exception as e:
            return False, f"Verification error: {str(e)}"

    def resend_verification_code(self, email):
        """Resends verification code to user's email."""
        try:
            response = self.client.resend_confirmation_code(
                ClientId=self.client_id,
                Username=email
            )
            return True, "Verification code resent successfully"
        except Exception as e:
            return False, f"Failed to resend code: {str(e)}"
