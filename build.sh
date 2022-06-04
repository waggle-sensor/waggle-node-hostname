#!/bin/bash -e

docker run --rm \
  -e NAME="waggle-node-hostname" \
  -e DESCRIPTION="Service to set the hostname on Waggle nodes" \
  -e "DEPENDS=python3-click" \
  -v "$PWD:/repo" \
  waggle/waggle-deb-builder:latest