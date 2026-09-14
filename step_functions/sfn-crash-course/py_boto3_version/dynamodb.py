import boto3
import time

# Initialize the DynamoDB client
dynamodb_client = boto3.client('dynamodb')

def create_dynamodb_table(table_name, key_schema, attribute_definitions, read_capacity_units=5, write_capacity_units=5):
    """
    Create a DynamoDB table.
    
    :param table_name: Name of the table to create
    :param key_schema: Schema for the table's primary key
    :param attribute_definitions: Attribute definitions for the key schema
    :param read_capacity_units: Provisioned read capacity units
    :param write_capacity_units: Provisioned write capacity units
    """
    try:
        response = dynamodb_client.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput={
                'ReadCapacityUnits': read_capacity_units,
                'WriteCapacityUnits': write_capacity_units
            }
        )
        print(f"{table_name} creation initiated: {response['TableDescription']['TableStatus']}")
    except dynamodb_client.exceptions.ResourceInUseException:
        print(f"Table {table_name} already exists.")

def wait_for_table_active(table_name):
    """
    Wait until the DynamoDB table is active.
    
    :param table_name: Name of the table to wait for
    """
    print(f"Waiting for {table_name} to become active...")
    waiter = dynamodb_client.get_waiter('table_exists')
    waiter.wait(TableName=table_name)
    print(f"{table_name} is now active.")

def delete_dynamodb_table(table_name):
    """
    Delete a DynamoDB table.
    
    :param table_name: Name of the table to delete
    """
    try:
        response = dynamodb_client.delete_table(TableName=table_name)
        print(f"{table_name} deletion initiated.")
    except dynamodb_client.exceptions.ResourceNotFoundException:
        print(f"Table {table_name} does not exist.")

def put_item_into_table(table_name, item):
    """
    Put an item into a DynamoDB table.
    
    :param table_name: Name of the table
    :param item: Item to put into the table
    """
    try:
        dynamodb_client.put_item(
            TableName=table_name,
            Item=item
        )
        print(f"Item {item} inserted into {table_name}.")
    except Exception as e:
        print(f"Error putting item into table {table_name}: {e}")

def create_all_dynamodbs():
    # Example usage
    user_table_name = 'userTable'
    book_table_name = 'bookTable'

    user_key_schema = [
        {
            'AttributeName': 'userId',
            'KeyType': 'HASH'  # Partition key
        }
    ]

    user_attribute_definitions = [
        {
            'AttributeName': 'userId',
            'AttributeType': 'S'  # String
        }
    ]

    book_key_schema = [
        {
            'AttributeName': 'bookId',
            'KeyType': 'HASH'  # Partition key
        }
    ]

    book_attribute_definitions = [
        {
            'AttributeName': 'bookId',
            'AttributeType': 'S'  # String
        }
    ]

    # # Create tables
    create_dynamodb_table(user_table_name, user_key_schema, user_attribute_definitions)
    create_dynamodb_table(book_table_name, book_key_schema, book_attribute_definitions)

    # # Wait for tables to become active
    wait_for_table_active(user_table_name)
    wait_for_table_active(book_table_name)

    # Put items into tables
    user_item = {
        'userId': {'S': '1'},
        'name': {'S': 'James'},
        'points': {'N': '300'}
    }

    # Put items into table
    book_item = {
        'bookId': {'S': '1'},
        'title': {'S': 'Algorithm and Data Structures'},
        'price': {'N': '19.99'},
        'quantity': {'N': '100'}
    }

    put_item_into_table(user_table_name, user_item)
    put_item_into_table(book_table_name, book_item)


if __name__ == "__main__":
    create_all_dynamodbs()

    # user_table_name = 'userTable'
    # book_table_name = 'bookTable'
    # delete_dynamodb_table(user_table_name)
    # delete_dynamodb_table(book_table_name)