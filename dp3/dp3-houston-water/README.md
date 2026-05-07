# DP3 Houston Water Monitoring Project

## Overview

This project tracks the water level of the Houston Buffalo Bayou over time using the USGS Water Services API. This project builds a serverless data pipeline that continuously collects real-world environmental data, stores it in the cloud, and exposes it through a REST API. It also generates a time-series visualization that allows users to observe trends in water level changes over time.

## Data Source

The data for this project is collected from the USGS Water Services API, which provides real-time stream gauge measurements across the United States. The endpoint used in this project returns water level (gage height) readings for the Buffalo Bayou river in Houston, Texas. This data source was chosen because it updates frequently, is publicly available without requiring an API key, and provides meaningful environmental measurements that naturally form a time series.

## Sampling Frequency

The ingestion pipeline runs every 15 minutes using an EventBridge Scheduler. Each execution triggers an AWS Lambda function that fetches the latest water level measurement from the USGS API and stores it in DynamoDB. 

## Storage Schema

The data is stored in a DynamoDB table named dp3-houston-water-level. Each record includes a partition key identifying the data source and a timestamp representing when the measurement was taken. The table stores both a Unix timestamp and a human-readable timestamp to support sorting, querying, and visualization. Each record also contains the water level value as a numeric field.

## API Resources

The API has 3 endpoints.

/current: This endpoint returns the most recent water level measurement from the database. It queries DynamoDB for the latest record and returns a formatted string describing the current water level in feet.

/trend: This endpoint computes the change in water level between the two most recent measurements. It queries the latest two entries from DynamoDB, calculates the difference, and returns a summary of whether the water level has increased or decreased.

/plot: This endpoint returns a URL pointing to a time-series plot stored in an S3 bucket. The plot is generated from historical water level data and is updated periodically by a separate Lambda function that regenerates the visualization and uploads it to S3.