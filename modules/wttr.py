import requests


class WeatherFetcher:
    def __init__(self, location):
        self.location = location

    def get_weather(self):
        url = f"https://wttr.in/{self.location}?format=%C+%t+%w+%S+%s"
        response = requests.get(url)
        if response.status_code == 200:
            response_text = response.text.replace("Partly ", "")
            response_text = response_text.replace("Light", "")
            response_text = response_text.replace("shower", "")
            weather_info = response_text.split()
            condition = weather_info[0].strip()
            temperature = weather_info[1].strip()
            wind = weather_info[2].strip()
            dawn = weather_info[-2].strip()
            sunset = weather_info[-1].strip()

            emojis = {
                "☁️": ["Cloudy", "Overcast", "cloudy"],
                "🌤️": ["Partly", "Partly cloudy"],
                "": ["Sunny", "Clear"],
                "🌧️": ["Rain", "Lightrain", "Drizzle"],
                "🌦️": ["Light shower rain", "Rain shower"],
                "🌩️": ["Thunderstorm"],
                "❄": ["Snow", "Light snow", "Light shower snow"],
                "🌨️": ["Snow shower", "Shower snow"],
                "🌬️": ["Windy"],
                "🌫️": ["Mist", "Fog"],
            }

            selected_emoji = next(
                (
                    emoji
                    for emoji, conditions in emojis.items()
                    if condition in conditions
                ),
                None,
            )

            output = f"{selected_emoji} {condition}\n"
            output += f"🌡️ {temperature}\n"
            output += f"💨 {wind}\n"
            output += f"🌞 {dawn}\n"
            output += f"🌛 {sunset}\n"
            return output
        else:
            return "Failed to fetch weather data."


# Example usage:
#location = "Swansea"
#weather_fetcher = WeatherFetcher(location)
#weather_data = weather_fetcher.get_weather()
#print(weather_data)
