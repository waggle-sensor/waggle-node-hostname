#!/usr/bin/env python3

import os
import pytest
import shutil
from click.testing import CliRunner
from ROOTFS.usr.bin.waggle_node_hostname import main
from pathlib import Path


@pytest.fixture()
def helper():
    print("****SETUP*****")
    # load default files
    Path("/etc/waggle").mkdir(parents=True, exist_ok=True)
    shutil.copy("/workdir/tests/node-id.default", "/etc/waggle/node-id")
    shutil.copy("/workdir/tests/config.ini.default", "/etc/waggle/config.ini")
    shutil.copy("/workdir/tests/bk_key.pem.default", "/etc/waggle/bk_key.pem")
    # seed the hostname with a test value
    with open("/etc/hostname", "w") as fp:
        fp.write("pre-test-hostname")

    yield

    print("****TEARDOWN*****")
    shutil.rmtree("/etc/waggle")


def test_default_nodeid_sysname(helper):
    """Test default (from disk) nodeid and sysname (from config) works"""
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0

    # assert the /etc/hostname file exists
    assert Path("/etc/hostname").exists()

    # assert hostname is correct
    with open("/etc/hostname", "r") as file:
        content = file.readline()
    assert len(content) == 26
    assert content == "ws-nxcore-0000ABCDEF123456"


def test_input_nodeid(helper):
    """Test provided nodeid and default sysname (from config) works"""
    runner = CliRunner()
    result = runner.invoke(main, ["-n", "/workdir/tests/node-id.input"])
    assert result.exit_code == 0

    # assert the /etc/hostname file exists
    assert Path("/etc/hostname").exists()

    # assert hostname is correct
    with open("/etc/hostname", "r") as file:
        content = file.readline()
    assert len(content) == 26
    assert content == "ws-nxcore-0000123456789ABC"


def test_empty_nodeid(helper):
    """Test that an empty node-id file results in hostname failure"""
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
    assert content == "pre-test-hostname"


def test_missing_nodeid(helper):
    """Test invalid node-id file path"""
    runner = CliRunner()
    result = runner.invoke(main, ["-n", "/tmp/node-id.missing"])
    assert result.exit_code != 0

    # assert the /etc/hostname file exists
    assert Path("/etc/hostname").exists()

    # assert matches the before test value
    with open("/etc/hostname", "r") as file:
        content = file.readline()
    assert content == "pre-test-hostname"


def test_badformat_config(helper):
    """Test bad formatted config.ini"""
    shutil.copy("/workdir/tests/config.ini.badformat", "/etc/waggle/config.ini")

    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code != 0

    # assert the /etc/hostname file exists
    assert Path("/etc/hostname").exists()

    # assert matches the before test value
    with open("/etc/hostname", "r") as file:
        content = file.readline()
    assert content == "pre-test-hostname"


def test_missing_revtunnel_section(helper):
    """Test for missing reverse-tunnel section in config.ini"""
    shutil.copy("/workdir/tests/config.ini.badrevtun1", "/etc/waggle/config.ini")

    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code != 0

    # assert the /etc/hostname file exists
    assert Path("/etc/hostname").exists()

    # assert matches the before test value
    with open("/etc/hostname", "r") as file:
        content = file.readline()
    assert content == "pre-test-hostname"


def test_missing_revtunnel_key(helper):
    """Test for missing reverse-tunnel[key] key in config.ini"""
    shutil.copy("/workdir/tests/config.ini.badrevtun2", "/etc/waggle/config.ini")

    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code != 0

    # assert the /etc/hostname file exists
    assert Path("/etc/hostname").exists()

    # assert matches the before test value
    with open("/etc/hostname", "r") as file:
        content = file.readline()
    assert content == "pre-test-hostname"


def test_revtun_key_file_missing(helper):
    """Test for missing reverse-tunnel key file"""
    os.remove("/etc/waggle/bk_key.pem")

    # test returns non-failure, but does not make any changes to the hostname
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0

    # assert the /etc/hostname file exists
    assert Path("/etc/hostname").exists()

    # assert matches the before test value
    with open("/etc/hostname", "r") as file:
        content = file.readline()
    assert content == "pre-test-hostname"


def test_missing_sysname_unknown(helper):
    """Test for missing or bad system["name"] key in config.ini"""
    shutil.copy("/workdir/tests/config.ini.badsysname", "/etc/waggle/config.ini")

    # test returns non-failure, and sets a "unknown" hostname
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0

    # assert the /etc/hostname file exists
    assert Path("/etc/hostname").exists()

    # assert hostname is correct
    with open("/etc/hostname", "r") as file:
        content = file.readline()
    assert len(content) == 24
    assert content == "unknown-0000ABCDEF123456"
