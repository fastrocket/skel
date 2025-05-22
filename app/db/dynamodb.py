import boto3
from boto3.dynamodb.conditions import Key, Attr
import config
from typing import Dict, Any, Optional, List

def get_dynamodb_resource():
    """
    Create and return a DynamoDB resource
    """
    # Create DynamoDB resource with optional local endpoint for development
    return boto3.resource(
        'dynamodb',
        region_name=config.AWS_REGION,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        endpoint_url=config.DYNAMODB_ENDPOINT_URL,
    )

def get_users_table():
    """
    Get the users table from DynamoDB
    """
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(config.DYNAMODB_TABLE_USERS)

def create_tables_if_not_exist():
    """
    Create the required DynamoDB tables if they don't exist
    """
    dynamodb = get_dynamodb_resource()
    client = dynamodb.meta.client
    
    # Get existing tables
    existing_tables = client.list_tables()['TableNames']
    
    # Create users table if it doesn't exist
    if config.DYNAMODB_TABLE_USERS not in existing_tables:
        client.create_table(
            TableName=config.DYNAMODB_TABLE_USERS,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'},  # Partition key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'},
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'email-index',
                    'KeySchema': [
                        {'AttributeName': 'email', 'KeyType': 'HASH'},
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5,
                    }
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5,
            }
        )
        print(f"Created table: {config.DYNAMODB_TABLE_USERS}")

# User operations
def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by ID
    """
    table = get_users_table()
    response = table.get_item(Key={'id': user_id})
    return response.get('Item')

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by email using GSI
    """
    table = get_users_table()
    response = table.query(
        IndexName='email-index',
        KeyConditionExpression=Key('email').eq(email)
    )
    items = response.get('Items', [])
    return items[0] if items else None

def create_user(user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new user
    """
    table = get_users_table()
    table.put_item(Item=user)
    return user

def update_user(user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing user
    """
    table = get_users_table()
    
    # Create update expression, attribute names, and attribute values
    update_expression = "SET "
    expression_attribute_names = {}
    expression_attribute_values = {}
    
    # Skip id as it's the primary key
    for key, value in user.items():
        if key != 'id':
            # Use a placeholder for attribute names to avoid issues with reserved keywords
            # A simple scheme: #k0, #k1, ... for keys, and :v0, :v1, ... for values
            # Or more specific for known problematic keys like 'name'
            attr_name_placeholder = f"#{key.replace('-', '_')}_placeholder"
            attr_value_placeholder = f":{key.replace('-', '_')}_value"
            
            if key.lower() == "name": # Specifically handle 'name'
                attr_name_placeholder = "#usr_name" # Using a fixed placeholder for 'name'
                expression_attribute_names["#usr_name"] = "name"
            else:
                expression_attribute_names[attr_name_placeholder] = key

            update_expression += f"{attr_name_placeholder} = {attr_value_placeholder}, "
            expression_attribute_values[attr_value_placeholder] = value
    
    # Remove trailing comma and space
    update_expression = update_expression.rstrip(', ')
    
    # Update the item
    if expression_attribute_values: # Only update if there are attributes to update
        table.update_item(
            Key={'id': user['id']},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
    
    return user

def delete_user(user_id: str) -> bool:
    """
    Delete a user by ID
    """
    table = get_users_table()
    table.delete_item(Key={'id': user_id})
    return True
