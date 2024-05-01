#!python3
# -*- coding: utf-8 -*-

"""
MeshBot
=======================

meshbot.py: A message bot designed for Meshtastic, providing information from modules upon request:
* weather information 
* tides information 
* whois search
* simple bbs

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
import secrets
import threading
import time
from pathlib import Path

import requests
import yaml

try:
    import meshtastic.serial_interface
    from pubsub import pub
except ImportError:
    print(
        "ERROR: Missing meshtastic library!\nYou can install it via pip:\npip install meshtastic\n"
    )

import serial.tools.list_ports

from modules.bbs import BBS
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
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# GLOBALS
LOCATION = ""
TIDE_LOCATION = ""
MYNODE = ""
MYNODES = ""
DBFILENAME = ""
DM_MODE = ""
FIREWALL = ""

with open("settings.yaml", "r") as file:
    settings = yaml.safe_load(file)

LOCATION = settings.get("LOCATION")
TIDE_LOCATION = settings.get("TIDE_LOCATION")
MYNODE = settings.get("MYNODE")
MYNODES = settings.get("MYNODES")
DBFILENAME = settings.get("DBFILENAME")
DM_MODE = settings.get("DM_MODE")
FIREWALL = settings.get("FIREWALL")

logger.info(f"DM_MODE: {DM_MODE}")
logger.info(f"FIREWALL: {FIREWALL}")
# try:
#    LOCATION = requests.get("https://ipinfo.io/city").text
#    logger.info(f"Setting location to {LOCATION}")
# except:
#    logger.warning("Could not calculate location.  Using defaults")

weather_fetcher = WeatherFetcher(LOCATION)
tides_scraper = TidesScraper(TIDE_LOCATION)
bbs = BBS()
transmission_count = 0
cooldown = False
kill_all_robots = 0  # Assuming you missed defining kill_all_robots


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
    global DBFILENAME
    global DM_MODE
    global FIREWALL

    if packet is not None and packet["decoded"].get("portnum") == "TEXT_MESSAGE_APP":
        message = packet["decoded"]["text"].lower()
        sender_id = packet["from"]
        logger.info(f"Message {packet['decoded']['text']} from {packet['from']}")
        logger.info(f"transmission count {transmission_count}")
        if (
            transmission_count < 16
            and (DM_MODE == 0 or str(packet["to"]) == MYNODE)
            and (FIREWALL == 0 or any(node in str(packet["from"]) for node in MYNODES))
        ):
            if "#fw" in message:
                message_parts = message.split(" ")
                if len(message_parts) > 1:
                    if message_parts[1].lower() == "off":
                        FIREWALL = False
                        logger.info("FIREWALL=False")
                    else:
                        FIREWALL = True
                        logger.info("FIREWALL=True")
                else:
                    FIREWALL = True
                    logger.info("FIREWALL=True")
            elif "#dm" in message:
                message_parts = message.split(" ")
                if len(message_parts) > 1:
                    if message_parts[1].lower() == "off":
                        DM_MODE = False
                        logger.info("DM_MODE=False")
                    else:
                        DM_MODE = True
                        logger.info("DM_MODE=True")
                else:
                    DM_MODE = True
                    logger.info("DM_MODE=True")

            elif "#flipcoin" in message:
                transmission_count += 1
                interface.sendText(
                    secrets.choice(["Heads", "Tails"]),
                    wantAck=True,
                    destinationId=sender_id,
                )
            elif "#random" in message:
                transmission_count += 1
                interface.sendText(
                    str(secrets.randbelow(10) + 1),
                    wantAck=True,
                    destinationId=sender_id,
                )
            elif "#weather" in message:
                transmission_count += 1
                interface.sendText(weather_info, wantAck=True, destinationId=sender_id)
            elif "#tides" in message:
                transmission_count += 1
                interface.sendText(tides_info, wantAck=True, destinationId=sender_id)
            elif "#test" in message:
                transmission_count += 1
                interface.sendText("🟢 ACK", wantAck=True, destinationId=sender_id)
            elif "#whois #" in message:
                message_parts = message.split("#")
                transmission_count += 1
                lookup_complete = False
                if len(message_parts) > 1:
                    whois_search = Whois(DBFILENAME)
                    logger.info(
                        f"Querying whois DB {DBFILENAME} for: {message_parts[2].strip()}"
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
                                lookup_complete = True
                    except:
                        logger.error("Not a hex string aborting!")
                        pass
                    if (
                        type(message_parts[2].strip()) == str
                        and lookup_complete == False
                    ):
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
            elif "#bbs" in message:
                transmission_count += 1
                count = 0
                message_parts = message.split()
                addy = hex(packet["from"]).replace("0x", "!")
                if message_parts[1].lower() == "any":
                    try:
                        count = bbs.count_messages(addy)
                        logger.info(f"{count} messages found")
                    except ValueError as e:
                        message = "No new messages."
                        logger.error(f"bbs count messages error: {e}")
                    if count:
                        message = "You have " + str(count) + " messages."
                        interface.sendText(
                            message, wantAck=True, destinationId=sender_id
                        )
                if message_parts[1].lower() == "get":
                    try:
                        message = bbs.get_message(addy)
                        bbs.delete_message(addy)
                    except:
                        message = "No new messages."
                    logger.info(message)
                    interface.sendText(
                        message,
                        wantAck=False,
                        destinationId=sender_id,
                    )

                if message_parts[1].lower() == "post":
                    content = " ".join(
                        message_parts[3:]
                    )  # Join the remaining parts as the message content
                    whois_search = Whois(DBFILENAME)
                    result = whois_search.search_nodes(
                        hex(packet["from"]).replace("0x", "")
                    )
                    if result:
                        node_id, long_name, short_name = result
                    else:
                        short_name = hex(packet["from"])
                    content = content + " from: " + short_name
                    bbs.post_message(message_parts[2], content)
            elif "#kill_all_robots" in message:
                transmission_count += 1
                if kill_all_robots == 0:
                    interface.sendText(
                        "Confirm", wantAck=False, destinationId=sender_id
                    )
                    kill_all_robots += 1
                if kill_all_robots > 1:
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
    global DBFILENAME

    parser = argparse.ArgumentParser(description="Meshbot a bot for Meshtastic devices")
    parser.add_argument("--port", type=str, help="Specify the serial port to probe")
    parser.add_argument("--db", type=str, help="Specify DB: mpowered or liam")

    args = parser.parse_args()

    if args.port:
        serial_ports = [args.port]
        logger.info(f"Serial port {serial_ports}\n")
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
        exit(0)

    if args.db:
        if args.db.lower() == "mpowered":
            DBFILENAME = str(cwd) + "/db/nodes.db"
            logger.info(f"Setting DB to mpowered data: {DBFILENAME}")
        if args.db.lower() == "liam":
            DBFILENAME = str(cwd) + "/db/nodes2.db"
            logger.info(f"Setting DB to Liam Cottle data: {DBFILENAME}")
    else:
        logger.info(f"Default DB: {DBFILENAME}")

    logger.info(f"Press CTRL-C x2 to terminate the program")
    interface = meshtastic.serial_interface.SerialInterface(serial_ports[0])
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
