import json
import logging
import sys
from collections import defaultdict

import click
import pandas as pd

from aws_inventor.utils import write_df

log = logging.getLogger(__name__)


def format_principal(principal: dict) -> list[str]:
    if not isinstance(principal, dict):
        return [str(principal)]
    if "AWS" not in principal:
        return [str(principal)]
    aws_principal = principal["AWS"]
    if isinstance(aws_principal, str):
        aws_principal = [aws_principal]
    return aws_principal


def format_key_for_df(key: dict) -> dict:
    key = key.copy()
    sid_to_principals = defaultdict(list)

    policies = key.pop("Policies", [])
    for pol_name, pol in sorted(policies.items()):
        if pol["Id"].startswith("auto-"):  # Skip auto-generated policies
            continue
        for stmt in pol["Statement"]:
            sid_to_principals[format_sid(pol_name, stmt)].extend(
                format_principal(stmt["Principal"])
            )
    key.update(
        {
            f"SID: {sid}": ", ".join(sorted(principals))
            for sid, principals in sid_to_principals.items()
        }
    )
    key["EncryptionAlgorithms"] = ", ".join(sorted(key["EncryptionAlgorithms"]))
    key.update(
        {f'Tag: {tag["TagKey"]}': tag["TagValue"] for tag in key.pop("Tags", [])}
    )
    return key


def format_sid(pol_name: str, stmt: dict) -> str:
    name = stmt["Sid"]
    if pol_name != "default":
        name = f"{pol_name}::{name}"
    return name


@click.command(help="Format list_keys output")
@click.option("--input-file", "-i", type=click.File("r"), default=sys.stdin)
@click.option(
    "--output-file", "-o", "output_files", multiple=True, default=["key-report.xlsx"]
)
def format_keys(input_file, output_files):
    key_data = [json.loads(line) for line in input_file]
    df = pd.DataFrame([format_key_for_df(key) for key in key_data])
    df.drop(df[df["Enabled"] == False].index, inplace=True)
    df.drop(columns=["AWSAccountId", "KeyId", "Enabled"], inplace=True)
    df.sort_values(by=["KeyManager", "KeyState", "KeyUsage"], inplace=True)
    for output_file in output_files:
        write_df(df, output_file)
