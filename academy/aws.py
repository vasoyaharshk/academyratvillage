from academy import time_utils
from academy import settings
import boto3


def send_timing():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(settings.OPERATION_TABLE)

    time = str(time_utils.now_seconds())

    table.put_item(
        Item={
            'time': time
        }
    )


def send_timing2():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(settings.TASK_TABLE)

    time = str(time_utils.now_seconds())

    table.put_item(
        Item={
            'time': time
        }
    )
