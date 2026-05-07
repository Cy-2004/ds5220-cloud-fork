import json
import boto3
import requests
from datetime import datetime, timezone
import time
import logging
from decimal import Decimal

# logging setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS setup
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('dp3-houston-water-level')

def lambda_handler(event, context):
    try:
        # API call
        url = "https://waterservices.usgs.gov/nwis/iv/?format=json&sites=08075000&parameterCd=00065"

        response = requests.get(url, timeout=30)
        data = response.json()

        # Extract water level (gage height)
        value_str = data["value"]["timeSeries"][0]["values"][0]["value"][0]["value"]
        water_level = Decimal(value_str)

        unix_timestamp = int(time.time())

        readable_timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S")

        # save to DynamoDB
        table.put_item(
            Item={
                "id": "river_level",
                "timestamp": unix_timestamp,
                "readable_time": readable_timestamp,
                "water_level": water_level
            }
        )

        logger.info(f"Saved water level {water_level} at {readable_timestamp}")

        return {
            "statusCode": 200,
            "body": json.dumps("Success")
        }

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")

        return {
            "statusCode": 500,
            "body": json.dumps("Error")
        }