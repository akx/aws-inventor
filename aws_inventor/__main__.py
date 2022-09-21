import logging

import click

from aws_inventor.kms.format_keys import format_keys
from aws_inventor.kms.list_keys import list_keys


@click.group()
def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )


main.add_command(list_keys)
main.add_command(format_keys)

if __name__ == "__main__":
    main()
