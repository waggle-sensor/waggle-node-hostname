#!/usr/bin/env python3

import click
import logging
import logging.handlers
import uuid
import socket
from pathlib import Path

logger = logging.getLogger("waggle-node-hostname")
logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address="/dev/log")
handler.setFormatter(logging.Formatter("waggle-node-hostname: %(message)s"))
logger.addHandler(handler)

def_nodeid = "/etc/waggle/node-id"


def set_hostname(nodeid=None):
    """Set the hostname using the node ID string

    Arguments:
        node ID (str): the node ID string to generate the hostname from

    Returns:
        none, exception on error
    """
    logger.info(f"Set the system hostname [node ID: {nodeid}]")

    if not nodeid:
        raise Exception("Unable to set hostname, node ID must not be empty")
    if not isinstance(nodeid, str):
        raise TypeError(f"Unable to set hostname, node ID [{nodeid}] must be a string")

    # set the hostname for this and future boots
    try:
        socket.sethostname(nodeid)
        logger.info(f"Successfuly set the run-time hostname [{nodeid}]")
    except:
        logger.warning(f"Unable to set the run-time hostname [{nodeid}]")
        pass
    with open("/etc/hostname", "w") as file:
        file.write(nodeid)


@click.command()
@click.option(
    "-n", "--nodeid", "nodeid_file", default=def_nodeid, help="node ID file to use"
)
def main(nodeid_file):

    logger.info(f"Waggle set hostname [node ID file: {nodeid_file}]")

    nodeid = None
    try:
        with open(nodeid_file, "r") as f:
            nodeid = f.readline().strip()
    except Exception as e:
        logger.error(f"Unable to read node ID from file [{nodeid_file}]")

    set_hostname(nodeid)


if __name__ == "__main__":
    main()  # pragma: no cover
