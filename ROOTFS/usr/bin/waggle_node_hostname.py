#!/usr/bin/env python3

import configparser
import logging
import socket
import sys
from pathlib import Path

import click

logging.basicConfig(level=logging.INFO, format="%(message)s")

def_nodeid = "/etc/waggle/node-id"
config_file = "/etc/waggle/config.ini"


def set_hostname(sysname=None, nodeid=None, defer=False):
    """Set the system hostname to '<sysname>-<nodeid>'

    Arguments:
        sysname (str): the system name to prepend to the hostname
        nodeid (str): the Node ID name to postpend to the hostname
        defer (bool): cache hostname change only (if True); else set now also

    Returns:
        none, exception on error
    """
    logging.info(
        f"Set the system hostname [sysname: {sysname} | nodeid: {nodeid} | defer: {defer}]"
    )

    if not sysname:
        raise Exception("Unable to set hostname, `sysname` must not be empty")
    if not isinstance(sysname, str):
        raise TypeError(f"Unable to set hostname, `sysname` [{sysname}] must be a string")

    if not nodeid:
        raise Exception("Unable to set hostname, `nodeid` must not be empty")
    if not isinstance(nodeid, str):
        raise TypeError(f"Unable to set hostname, `nodeid` [{nodeid}] must be a string")

    hostname = f"{sysname}-{nodeid}"

    if not defer:
        # set the hostname now
        try:
            socket.sethostname(hostname)
            logging.info(f"Successfuly set the run-time hostname [{hostname}]")
        except:
            logging.warning(f"Unable to set the run-time hostname [{hostname}]")
            pass

    # set the hostname for future system boots
    with open("/etc/hostname", "w") as file:
        file.write(hostname)


@click.command()
@click.option("-n", "--nodeid", "nodeid_file", default=def_nodeid, help="node ID file to use")
@click.option(
    "-d",
    "--defer",
    is_flag=True,
    default=False,
    show_default=True,
    help="cache hostname for next boot only",
)
def main(nodeid_file, defer):
    logging.info(f"Waggle set hostname [node ID file: {nodeid_file} | defer: {defer}]")

    config = configparser.ConfigParser()
    try:
        config.read(config_file)
    except:
        logging.error(f"config error: unable to read config file {config_file}")
        sys.exit(1)

    # only proceed with setting a custom hostname after registration is complete
    try:
        regkey = str(config["reverse-tunnel"]["key"])
    except:
        logging.error(f"config error: unable to load 'reverse-tunnel[key]'")
        sys.exit(1)
    if not Path(f"{regkey}").exists():
        logging.warning(f"Registration key [{regkey}] missing, will NOT set hostname")
        sys.exit(0)

    # the registration key exists, so set the hostname
    try:
        sysname = config["system"]["name"]
    except:
        sysname = "unknown"
        logging.warning(
            f"System name config entry 'system[name]' not found, using default '{sysname}'"
        )

    nodeid = None
    try:
        with open(nodeid_file, "r") as f:
            nodeid = f.readline().strip()
    except Exception as e:
        logging.error(f"Unable to read node ID from file [{nodeid_file}]")
        sys.exit(1)

    set_hostname(sysname, nodeid, defer)


if __name__ == "__main__":
    main()  # pragma: no cover
