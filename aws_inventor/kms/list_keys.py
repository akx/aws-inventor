import json
import logging

import boto3
import click
import tqdm

from aws_inventor.utils import get_region_names

log = logging.getLogger(__name__)


def get_key_info(kms_client, key_id: str):
    key_info = kms_client.describe_key(KeyId=key_id)["KeyMetadata"]
    try:
        policy_names = kms_client.list_key_policies(KeyId=key_id)["PolicyNames"]
    except Exception:
        log.warning("Could not list policies for key %s, using `default` only", key_id)
        policy_names = ["default"]
    policies = {}
    for policy_name in policy_names:
        policy_resp = kms_client.get_key_policy(KeyId=key_id, PolicyName=policy_name)
        policies[policy_name] = json.loads(policy_resp["Policy"])
    try:
        tags = kms_client.list_resource_tags(KeyId=key_id)["Tags"]
    except Exception:
        tags = []
    return {**key_info, "Policies": policies, "Tags": tags}


@click.command(help="List KMS keys to JSONL")
@click.option("--output", "-o", type=click.File("w"), default="-")
def list_keys(output):
    for region_name in tqdm.tqdm(get_region_names()):
        kms_client = boto3.client("kms", region_name=region_name)
        for key in kms_client.list_keys()["Keys"]:
            formatted_key = get_key_info(kms_client, key_id=key["KeyId"])
            print(json.dumps(formatted_key, default=str), file=output)
