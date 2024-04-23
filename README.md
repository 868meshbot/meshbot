# MeshBot

MeshBot is a Python program designed to run on Meshtastic devices, allowing users to send and receive messages efficiently over a mesh network.

## Features

- Broadcast messages: Send text broadcasts to all devices on the mesh network.
- Weather updates: Get real-time weather updates for a specified location.
- Tides information: Receive tidal information for coastal areas.
- Whois: Query one of two User databases mpowered or liam

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

## Usage

1. Run the MeshBot program:

```
python meshbot.py --help
```

2. Follow the on-screen instructions to interact with the program.

## Contributors

- [868meshbot](https://github.com/868meshbot)

## Acknowledgements

This project utilizes the Meshtastic Python library, which provides communication capabilities for Meshtastic devices. For more information about Meshtastic, visit [meshtastic.org](https://meshtastic.org/).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## References

Database of IDs, long_name and short_names obtained from the node list from the following URLs: -[https://map.mpowered247.com/](https://map.mpowered247.com/) -[https://meshtastic.liamcottle.net/](https://meshtastic.liamcottle.net/)
