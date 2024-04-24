#!python3
# -*- coding: utf-8 -*-

"""
MeshBot
=======================

meshbot.py: A message bot designed for Meshtastic, providing information from modules upon request:
* weather and 
* tides information 

Author:
- Andy
- April 2024

MIT License

Copyright (c) 2024 Andy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import argparse
import logging
import threading
import time
from pathlib import Path

import requests

try:
    import meshtastic.serial_interface
    from pubsub import pub
except ImportError:
    print(
        "ERROR: Missing meshtastic library!\nYou can install it via pip:\npip install meshtastic"
    )

import serial.tools.list_ports

from modules.tides import TidesScraper
from modules.whois import Whois
from modules.wttr import WeatherFetcher


def find_serial_ports():
    # Use the list_ports module to get a list of available serial ports
    ports = [port.device for port in serial.tools.list_ports.comports()]
    filtered_ports = [
        port for port in ports if "COM" in port.upper() or "USB" in port.upper()
    ]
    return filtered_ports


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# GLOBALS
try:
    LOCATION = requests.get("https://ipinfo.io/city").text
    logger.info(f"Setting location to {LOCATION}")
except:
    logger.warning("Could not calculate location.  Using defaults")
    LOCATION = "Swansea"

# CHANGE TO YOUR LOCAL COASTAL TOWN
TIDE_LOCATION = "Swansea"

# CHANGE ME TO YOUR NODE ID
MYNODE = "3663493700"

# Global variables for weather and tides data
weather_fetcher = WeatherFetcher(LOCATION)
tides_scraper = TidesScraper(TIDE_LOCATION)

transmission_count = 0
cooldown = False
kill_all_robots = 0  # Assuming you missed defining kill_all_robots
dbfilename = ""


# Function to periodically refresh weather and tides data
def refresh_data():
    while True:
        global weather_info
        global tides_info
        weather_info = weather_fetcher.get_weather()
        tides_info = tides_scraper.get_tides()
        time.sleep(3 * 60 * 60)  # Sleep for 3 hours


def reset_transmission_count():
    global transmission_count
    transmission_count -= 1
    if transmission_count < 0:
        transmission_count = 0
    logger.info(f"Reducing transmission count {transmission_count}")
    threading.Timer(180.0, reset_transmission_count).start()


def reset_cooldown():
    global cooldown
    cooldown = False
    logger.info("Cooldown Disabled.")
    threading.Timer(240.0, reset_cooldown).start()


def reset_killallrobots():
    global kill_all_robots
    kill_all_robots = 0
    logger.info("Killbot Disabled.")
    threading.Timer(120.0, reset_killallrobots).start()


# Function to handle incoming messages
def message_listener(packet, interface):
    global transmission_count
    global cooldown
    global kill_all_robots
    global weather_info
    global tides_info
    global dbfilename

    if packet is not None and packet["decoded"].get("portnum") == "TEXT_MESSAGE_APP":
        message = packet["decoded"]["text"].lower()
        sender_id = packet["from"]
        logger.info(f"Message {packet['decoded']['text']} from {packet['from']}")
        logger.info(f"transmission count {transmission_count}")
        if transmission_count < 11:
            if "weather" in message:
                transmission_count += 1
                interface.sendText(weather_info, wantAck=True, destinationId=sender_id)
            elif "tides" in message:
                transmission_count += 1
                interface.sendText(tides_info, wantAck=True, destinationId=sender_id)
            elif "#test" in message:
                transmission_count += 1
                interface.sendText("🟢 ACK", wantAck=True, destinationId=sender_id)
            elif "#whois #" in message:
                message_parts = message.split("#")
                transmission_count += 1
                if len(message_parts) > 1:
                    whois_search = Whois(dbfilename)
                    logger.info(
                        f"Querying whois DB {dbfilename} for: {message_parts[2].strip()}"
                    )
                    try:
                        if (
                            type(int(message_parts[2].strip(), 16)) == int
                            or type(int(message_parts[2].strip().upper(), 16)) == int
                        ):
                            result = whois_search.search_nodes(message_parts[2].strip())

                            if result:
                                node_id, long_name, short_name = result
                                whois_data = f"ID:{node_id}\n"
                                whois_data += f"Long Name: {long_name}\n"
                                whois_data += f"Short Name: {short_name}"
                                logger.info(f"Data: {whois_data}")
                                interface.sendText(
                                    f"{whois_data}",
                                    wantAck=False,
                                    destinationId=sender_id,
                                )
                            else:
                                interface.sendText(
                                    "No matching record found.",
                                    wantAck=False,
                                    destinationId=sender_id,
                                )
                    except:
                        logger.error("Not a hex string aborting!")
                        pass
                    if type(message_parts[2].strip()) == str:
                        result = whois_search.search_nodes_sn(message_parts[2].strip())

                        if result:
                            node_id, long_name, short_name = result
                            whois_data = f"ID:{node_id}\n"
                            whois_data += f"Long Name: {long_name}\n"
                            whois_data += f"Short Name: {short_name}"
                            logger.info(f"Data: {whois_data}")
                            interface.sendText(
                                f"{whois_data}", wantAck=False, destinationId=sender_id
                            )
                        else:
                            interface.sendText(
                                "No matching record found.",
                                wantAck=False,
                                destinationId=sender_id,
                            )

                    else:
                        interface.sendText(
                            "No matching record found.",
                            wantAck=False,
                            destinationId=sender_id,
                        )

                    whois_search.close_connection()
                else:
                    pass
            elif "#kill_all_robots" in message:
                transmission_count += 1
                if kill_all_robots == 0:
                    interface.sendText(
                        "Confirm", wantAck=False, destinationId=sender_id
                    )
                    kill_all_robots += 1
                if kill_all_robots > 0:
                    interface.sendText(
                        "💣 Deactivating all reachable bots... SECRET_SHUTDOWN_STRING",
                        wantAck=False,
                    )
                    transmission_count += 1
                    kill_all_robots = 0
        if transmission_count >= 11:
            if not cooldown:
                interface.sendText(
                    "❌ Bot has reached duty cycle, entering cool down... ❄",
                    wantAck=False,
                )
                logger.info("Cooldown enabled.")
                cooldown = True
            logger.info(
                "Duty cycle limit reached. Please wait before transmitting again."
            )
        else:
            # do nothing as not a keyword and message destination was the node
            pass


# Main function
def main():
    logger.info("Starting program.")
    reset_transmission_count()
    reset_cooldown()
    reset_killallrobots()
    cwd = Path.cwd()
    global dbfilename

    parser = argparse.ArgumentParser(description="Meshbot a bot for Meshtastic devices")
    parser.add_argument("--port", type=str, help="Specify the serial port to probe")
    parser.add_argument("--db", type=str, help="Specify DB: mpowered or liam")

    args = parser.parse_args()

    if args.port:
        serial_ports = [args.port]
    else:
        serial_ports = find_serial_ports()
        if serial_ports:
            logger.info("Available serial ports:")
            for port in serial_ports:
                logger.info(port)
            logger.info(
                "Im not smart enough to work out the correct port, please use the --port argument with a relevent meshtastic port"
            )
        else:
            logger.info("No serial ports found.")

    if args.db:
        if args.db.lower() == "mpowered":
            dbfilename = str(cwd) + "/db/nodes.db"
            logger.info(f"Setting DB to mpowered data: {dbfilename}")
        if args.db.lower() == "liam":
            dbfilename = str(cwd) + "/db/nodes2.db"
            logger.info(f"Setting DB to Liam Cottle data: {dbfilename}")
    else:
        dbfilename = str(cwd) + "/db/nodes.db"
        logger.info("Default DB: {dbfilename}")

    logger.info(f"Press CTRL-C x2 to terminate the program")
    interface = meshtastic.serial_interface.SerialInterface()
    pub.subscribe(message_listener, "meshtastic.receive")

    # Start a separate thread for refreshing data periodically
    refresh_thread = threading.Thread(target=refresh_data)
    refresh_thread.daemon = True
    refresh_thread.start()

    # Keep the main thread alive
    while True:
        # time.sleep(1)
        continue


if __name__ == "__main__":
    main()
