
from boto3.dynamodb.conditions import Key, Attr
import boto3
import time

TRANSACTIONS_TABLE = None


def create_example():
    TRANSACTIONS_TABLE.put_item(Item={
        'group_id': 123,
        'id': 1,
        'from': "chesnutcase",
        'to': "lcrft_sx",
        'amnt': "1",
        'timestamp': round(time.time())
    })


def query_example():
    response = TRANSACTIONS_TABLE.query(
        KeyConditionExpression=Key('group_id').eq(123),
        FilterExpression=Attr('from').eq('chesnutcase') & Attr('to').eq('lcrft_sx')
    )
    return response["Items"]
