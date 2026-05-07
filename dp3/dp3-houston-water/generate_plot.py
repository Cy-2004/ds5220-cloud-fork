import boto3
import pandas as pd
import matplotlib.pyplot as plt
import io
import logging
from boto3.dynamodb.conditions import Key

# config
TABLE_NAME = "dp3-houston-water-level"
BUCKET_NAME = "dp3-houston-water-plots"
REGION = "us-east-1"

# logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)

# aws clients
dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

s3 = boto3.client("s3", region_name=REGION)

# query data
def get_data():
    logger.info("Querying DynamoDB table")

    try:
        response = table.query(
            KeyConditionExpression=Key('id').eq('river_level')
        )
        items = response.get("Items", [])
        logger.info(f"Retrieved {len(items)} items")
        return items

    except Exception as e:
        logger.error(f"DynamoDB query failed: {str(e)}")
        return []

# generate plot
def create_plot(items):
    logger.info("Creating dataframe")

    try:
        df = pd.DataFrame(items)

        # remove rows missing readable_time
        df = df.dropna(subset=["readable_time"])

        if len(df) < 2:
            logger.warning("Not enough data for plot")
            return None

        logger.info("Converting data types")

        df["water_level"] = df["water_level"].astype(float)
        df["readable_time"] = df["readable_time"].astype(str)
        df = df.sort_values("timestamp")

        logger.info("Generating matplotlib plot")

        plt.figure(figsize=(12,6))
        plt.plot(
            df["readable_time"],
            df["water_level"],
            marker='o'
        )
        plt.title("Houston Buffalo Bayou Water Level Over Time")
        plt.xlabel("Timestamp")
        plt.ylabel("Water Level (ft)")
        plt.xticks(rotation=45)
        plt.tight_layout()

        logger.info("Saving plot to memory buffer")

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        plt.close()
        return buffer

    except Exception as e:
        logger.error(f"Plot generation failed: {str(e)}")
        return None

# upload to s3
def upload_plot(buffer):
    logger.info("Uploading plot to S3")

    try:
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key="latest.png",
            Body=buffer.getvalue(),
            ContentType="image/png"
        )
        logger.info("Upload successful")

    except Exception as e:
        logger.error(f"S3 upload failed: {str(e)}")

def main():
    logger.info("Starting plot generation job")

    items = get_data()

    if not items:
        logger.warning("No data found")
        return

    plot_buffer = create_plot(items)

    if plot_buffer is None:
        logger.warning("Plot buffer is empty")
        return

    upload_plot(plot_buffer)

    logger.info("Job completed successfully")

if __name__ == "__main__":
    main()