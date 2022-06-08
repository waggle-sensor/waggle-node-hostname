# Waggle Node Hostname Service

A service that sets the Debian OS hostname to the system name
(gathered from config, `/etc/waggle/config.ini`) combined with the unique
Node ID found in the `/etc/waggle/node-id` file.

```
<system name>-<node ID>
```

To be executed on system shutdown to ensure the hostname is correct for
the next boot.

## Build Instructions

Builds are created using the `./build.sh` script. For help execute `./build.sh -?`.

Build generates a Debian package that can be installed into a Debian OS via
the `dpkg -i` command.
