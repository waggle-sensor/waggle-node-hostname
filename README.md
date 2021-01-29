# Waggle Node Hostname Service

An early boot service that sets the Debian OS hostname to the unique Node ID
found in the `/etc/waggle/node-id` file. If the file is not found the service
fails and exists with an error.

## Build Instructions

Builds are created using the `./build.sh` script. For help execute `./build.sh -?`.

Build generates a Debian package that can be installed into a Debian OS via
the `dpkg -i` command.
