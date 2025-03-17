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

    def sign_up(self, username, password, email):
        """Registers a new user in the Cognito User Pool."""
        try:
            response = self.client.sign_up(
                ClientId=self.client_id,
                Username=username,
                Password=password,
                UserAttributes=[{'Name': 'email', 'Value': email}]
            )
            logger.info(f"User {username} registered successfully.")
            return True, "User registration successful"

        except self.client.exceptions.UsernameExistsException:
            return False, "Username already exists."
        except self.client.exceptions.InvalidParameterException as e:
            return False, f"Invalid parameters: {str(e)}"
        except self.client.exceptions.ResourceNotFoundException as e:
            return False, f"Configuration error: {str(e)}. Please verify your Cognito settings."
        except ClientError as e:
            return False, f"AWS Error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def sign_in(self, username, password):
        """Authenticates a user and returns the authentication result."""
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={'USERNAME': username, 'PASSWORD': password}
            )
            logger.info(f"User {username} logged in successfully.")
            return True, response['AuthenticationResult']

        except self.client.exceptions.NotAuthorizedException:
            return False, "Incorrect username or password."
        except self.client.exceptions.UserNotFoundException:
            return False, "User does not exist."
        except self.client.exceptions.ResourceNotFoundException:
            return False, "Cognito client configuration is invalid."
        except ClientError as e:
            return False, f"AWS Error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

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
