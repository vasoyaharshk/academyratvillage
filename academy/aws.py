from academy import time_utils
from academy import settings


class FakeBoto3:
    def __init__(self):
        self.name = "fake"

    def resource(self, text):
        pass

try:
    import boto3
except:
    boto3 = FakeBoto3


def send_timing():
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(settings.OPERATION_TABLE)

        time = str(time_utils.now_seconds())

        table.put_item(
            Item={
                'time': time
            }
        )
    except:
        pass


def send_timing2():
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(settings.TASK_TABLE)

        time = str(time_utils.now_seconds())

        table.put_item(
            Item={
                'time': time
            }
        )
    except:
        pass
