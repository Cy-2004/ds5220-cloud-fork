from chalice import Chalice
import boto3
from decimal import Decimal
import logging
from boto3.dynamodb.conditions import Key
import time

# chalice setup
app = Chalice(app_name='dp3-houston-water')

# logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# aws setup
logger.info("Initializing DynamoDB resource")

try:
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('dp3-houston-water-level')
    logger.info("Connected to DynamoDB table successfully")

except Exception as e:
    logger.error(f"Failed to initialize DynamoDB: {str(e)}")

@app.route('/')
def index():
    logger.info("Root endpoint '/' called")

    try:
        logger.info("Returning API metadata")
        return {
            "about": "Tracks Houston Buffalo Bayou water level over time using USGS data.",
            "resources": ["current", "trend", "plot"]
        }

    except Exception as e:
        logger.error(f"Root endpoint failed: {str(e)}")
        return {
            "about": "Error loading API",
            "resources": []
        }

@app.route('/current')
def current():
    logger.info("'/current' endpoint called")

    try:
        logger.info("Querying DynamoDB for latest water level")

        response = table.query(
            KeyConditionExpression=Key('id').eq('river_level'),
            ScanIndexForward=False,
            Limit=1
        )

        logger.info("DynamoDB query completed")

        items = response.get("Items", [])

        logger.info(f"Retrieved {len(items)} items")

        if len(items) == 0:
            logger.warning("No water level data found")
            return {
                "response": "No water level data available yet"
            }

        logger.info("Extracting latest item")

        item = items[0]

        logger.info(f"Latest item: {item}")

        logger.info("Converting Decimal water level to float")

        level = float(item['water_level'])

        readable_time = item.get(
            "readable_time",
            "unknown time"
        )

        logger.info(
            f"Current water level = {level} ft at {readable_time}"
        )

        return {
            "response": f"Current water level is {level:.2f} ft at {readable_time} UTC"
        }

    except KeyError as e:
        logger.error(f"Missing expected field in DynamoDB item: {str(e)}")
        return {
            "response": "Data format error in current endpoint"
        }

    except Exception as e:
        logger.error(f"Current endpoint failed: {str(e)}")
        return {
            "response": "Error fetching current water level"
        }

@app.route('/trend')
def trend():
    logger.info("'/trend' endpoint called")

    try:
        logger.info("Querying DynamoDB for latest two readings")

        response = table.query(
            KeyConditionExpression=Key('id').eq('river_level'),
            ScanIndexForward=False,
            Limit=2
        )

        logger.info("DynamoDB query completed")

        items = response.get("Items", [])

        logger.info(f"Retrieved {len(items)} items")

        if len(items) < 2:
            logger.warning("Not enough data points to calculate trend")
            return {
                "response": "Not enough data yet to calculate trend"
            }

        logger.info("Extracting latest readings")

        latest_item = items[0]
        previous_item = items[1]

        logger.info(f"Latest item: {latest_item}")
        logger.info(f"Previous item: {previous_item}")

        logger.info("Converting water levels to float")

        latest_level = float(latest_item['water_level'])
        previous_level = float(previous_item['water_level'])

        logger.info(
            f"Latest level = {latest_level}, Previous level = {previous_level}"
        )

        diff = latest_level - previous_level

        logger.info(f"Calculated difference = {diff}")

        latest_time = latest_item.get(
            "readable_time",
            "unknown time"
        )

        if diff > 0:
            trend_message = (
                f"Water level increased by {diff:.2f} ft "
                f"since the previous reading"
            )

        elif diff < 0:
            trend_message = (
                f"Water level decreased by {abs(diff):.2f} ft "
                f"since the previous reading"
            )

        else:
            trend_message = (
                "Water level has not changed since the previous reading."
            )

        logger.info(f"Trend response: {trend_message}")

        return {
            "response": f"{trend_message} (latest reading at {latest_time} UTC)"
        }

    except KeyError as e:
        logger.error(f"Missing expected field in DynamoDB item: {str(e)}")
        return {
            "response": "Data format error in trend endpoint"
        }

    except Exception as e:
        logger.error(f"Trend endpoint failed: {str(e)}")
        return {
            "response": "Error calculating water level trend"
        }

@app.route('/plot')
def plot():
    logger.info("'/plot' endpoint called")

    timestamp = int(time.time())

    try:
        logger.info("Preparing plot URL")

        plot_url = (
            f"https://dp3-houston-water-plots.s3.amazonaws.com/latest.png?v={timestamp}"
        )

        logger.info(f"Returning plot URL: {plot_url}")

        return {
            "response": plot_url
        }

    except Exception as e:
        logger.error(f"Plot endpoint failed: {str(e)}")
        return {
            "response": "Error retrieving plot"
        }