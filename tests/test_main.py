#!/usr/bin/env python3

import os
import pytest
import shutil
import time
from click.testing import CliRunner
from ROOTFS.usr.bin.waggle_node_hostname import main
from pathlib import Path


def test_default_nodeid():
    """Test default (from disk) nodeid work"""
    Path("/etc/waggle").mkdir(parents=True, exist_ok=True)
    shutil.copy("/workdir/tests/node-id.default", "/etc/waggle/node-id")

    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0

    # assert the log file exists, sleep to give time to flush log to disk
    time.sleep(2)
    assert Path("/var/log/waggle/waggle.log").exists()

    # assert the /etc/hostname file exists
    assert Path("/etc/hostname").exists()

    # assert it is 16 characters long
    with open("/etc/hostname", "r") as file:
        content = file.readline()
    assert len(content) == 16
    assert content == "0000ABCDEF123456"

    # clean-up the default node-id file for future tests
    os.remove("/etc/waggle/node-id")


def test_input_nodeid():
    """Test provided nodeid works"""
    runner = CliRunner()
    result = runner.invoke(main, ["-n", "/workdir/tests/node-id.input"])
    assert result.exit_code == 0

    # assert the /etc/hostname file exists
    assert Path("/etc/hostname").exists()

    # assert it is 16 characters long and matches test file
    with open("/etc/hostname", "r") as file:
        content = file.readline()
    assert len(content) == 16
    assert content == "0000123456789ABC"


def test_empty_nodeid():
    """Test that a bad node-id file results in execution failure"""
    # seed the hostname with a test value
    with open("/etc/hostname", "w") as fp:
        fp.write("emptynodeid")
    # create empty node file
    with open("/tmp/node-id.empty", "w") as fp:
        pass

    runner = CliRunner()
    result = runner.invoke(main, ["-n", "/tmp/node-id.empty"])
    assert result.exit_code != 0

    # assert the /etc/hostname file exists
    assert Path("/etc/hostname").exists()

    # assert matches the before test value
    with open("/etc/hostname", "r") as file:
        content = file.readline()
    assert content == "emptynodeid"


def test_missing_nodeid():
    """Test invalid node-id file path"""
    # seed the hostname with a test value
    with open("/etc/hostname", "w") as fp:
        fp.write("missingnodeid")

    runner = CliRunner()
    result = runner.invoke(main, ["-n", "/tmp/node-id.missing"])
    assert result.exit_code != 0

    # assert the /etc/hostname file exists
    assert Path("/etc/hostname").exists()

    # assert matches the before test value
    with open("/etc/hostname", "r") as file:
        content = file.readline()
    assert content == "missingnodeid"
