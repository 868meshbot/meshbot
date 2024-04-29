# MeshBot

![Meshbot](./img/meshbot.png)

MeshBot is an OpenSource Python program designed to run on computers with a connected Meshtastic device, allowing users to send and receive messages efficiently over a mesh network.

## Features

- Broadcast messages: Send text broadcasts to all devices on the mesh network.
- Weather updates: Get real-time weather updates for a specified location.
- Tides information: Receive tidal information for coastal areas.
- Whois: Query one of two User databases mpowered247 or liamcottle
- Simple BBS: IN PROGRESS, store and retrieve messages via the bot

## Requirements

- Python 3.x
- Meshtastic Python library
- Access to a Meshtastic device [Meshtastic](https://meshtastic.org)
- Serial drivers for your meshtastic device, See [Installing Serial Drivers](https://meshtastic.org/docs/getting-started/serial-drivers/)

## Installation

1. Clone this repository to your local machine:

```
git clone https://github.com/868meshbot/meshbot.git
```

2. Navigate into the folder and setup a virtual environment

```
cd meshbot
python3 -m venv .venv
. .venv/bin/activate

```

3. Install the required dependencies:

```
pip install -r requirements.txt
```

4. Connect your Meshtastic device to your computer via USB and run the program

```
python ./mesbot.py

```

## Configuration (NEW)

We have revamped the configuration, there is now a ''settings.yaml'' file, which we believe makes the program easier to manage

Example Content:

```
---
LOCATION: "Swansea"
TIDE_LOCATION: "Swansea"
MYNODE: "3663493700"
MYNODES:
  - "3663493700"
DBFILENAME: "./db/nodes.db"
```

Description

- LOCATION and TIDE_LOCATION = These should be obvious
- MYNODE = The hw address of the node connected in int/number form. This is so the bot only responds to DMs
- MYNODES = A list of nodes (in int/number form) that are permitted to interact with the bot
- DBFILENAME = Configure which user database file to use by default

## Usage

Run the MeshBot program:

```
python meshbot.py --help
```

Example on Linux:

```
python meshbot.py --port /dev/ttyUSB0
```

Example on OSX:

```
python meshbot.py --port /dev/cu.usbserial-0001
```

Example on Windows:

```
python meshbot.py --port COM7
```

## Bot interaction

You bot will be accessible through the meshtastic mesh network through the node name. DM the bot/node and issue any of the following commands:

- #test : receive a test message
- #weather : local weather report
- #tides : tide info (dont forget to change the default town in the source)
- #whois #xxxx : retrieve name and node info for a node based on last 4 chars of address
- #bbs #post !address message : post a messgae on the bbs for a given user at !address
- #bbs #get : retrieve your message(s) left by another user(s)

## Contributors

- [868meshbot](https://github.com/868meshbot)

## Acknowledgements

This project utilizes the Meshtastic Python library, which provides communication capabilities for Meshtastic devices. For more information about Meshtastic, visit [meshtastic.org](https://meshtastic.org/).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## References

Database of IDs, long_name and short_names obtained from the node list from the following URLs:

- [https://map.mpowered247.com/](https://map.mpowered247.com/)
- [https://meshtastic.liamcottle.net/](https://meshtastic.liamcottle.net/)
