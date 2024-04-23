import defusedxml.ElementTree as ET
from urllib.request import urlopen


class TidesScraper:
    def __init__(self, location):
        self.rss_url = "https://www.tidetimes.org.uk/"+location.lower()+"-tide-times.rss"

    def get_tides(self):
        try:
            with urlopen(self.rss_url) as Client:
                xml_page = Client.read()
                root = ET.fromstring(xml_page)
                for item in root.iter("item"):
                    description = item.find("description").text
                    description = description.replace("&lt;br/&gt;", "\n").replace(
                        "&amp;amp;", "&"
                    )
                    lines = description.split("<br/>")
                    date = lines[0].split("on ")[1].strip()
                    tide_info = [line.split(" - ") for line in lines[2:] if line]
                    formatted_output = f"{date}\n"
                    for info in tide_info:
                        time = info[0].strip()
                        tide_type = "High" if "High" in info[1] else "Low"
                        tide_height = info[1].split("(")[-1].split("m")[0].strip()
                        formatted_output += (
                            f"{time} - {tide_type}\n"  # Tide ({tide_height}m)\n"
                        )
                    return formatted_output

        except Exception as e:
            print("An error occurred:", e)


# Example usage:
rss_url = "https://www.tidetimes.org.uk/swansea-tide-times.rss"
location="Swansea";
scraper = TidesScraper(location)
scraper.get_tides()
