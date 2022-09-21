import logging

import boto3
import pandas as pd

log = logging.getLogger(__name__)


def get_region_names():
    ec2 = boto3.client("ec2")

    response = ec2.describe_regions()
    regions = response["Regions"]

    return sorted([region["RegionName"] for region in regions])


def write_df(df: pd.DataFrame, filename: str) -> None:
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        df.to_excel(filename, index=False)
        log.info("Wrote Excel %s", filename)
    elif filename.endswith(".csv"):
        df.to_csv(filename, index=False)
        log.info("Wrote CSV %s", filename)
    elif filename.endswith(".json"):
        df.to_json(filename, orient="records")
        log.info("Wrote JSON %s", filename)
    else:
        raise ValueError(f"Unsupported format: {filename}")
