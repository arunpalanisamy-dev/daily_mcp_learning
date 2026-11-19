
import httpx
from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("Weather MCP Server")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# Convert weather codes into readable descriptions
def get_weather_description(code: int) -> str:

    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snowfall",
        73: "Moderate snowfall",
        75: "Heavy snowfall",
        80: "Rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with heavy hail"
    }

    return descriptions.get(code, "Unknown weather condition")

# Find a city using Open-Meteo Geocoding API
async def get_city_coordinates(city: str):

    async with httpx.AsyncClient(timeout=20.0) as client:

        response = await client.get(
            GEOCODING_URL,
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            }
        )

        response.raise_for_status()
        data = response.json()

    results = data.get("results", [])

    if not results:
        raise ValueError(f"City not found: {city}")

    return results[0]

# Tool 1: Get current weather
@mcp.tool()
async def get_current_weather(city: str) -> str:
    """Get current weather information for a city."""

    location = await get_city_coordinates(city)

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "is_day,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m"
        ),
        "timezone": "auto",
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh"
    }

    async with httpx.AsyncClient(timeout=20.0) as client:

        response = await client.get(
            WEATHER_URL,
            params=params
        )

        response.raise_for_status()
        data = response.json()

    current = data["current"]

    condition = get_weather_description(
        current["weather_code"]
    )

    return f"""
Weather Report: {location['name']}, {location.get('country', '')}

Temperature: {current['temperature_2m']} °C
Feels Like: {current['apparent_temperature']} °C
Humidity: {current['relative_humidity_2m']} %
Wind Speed: {current['wind_speed_10m']} km/h
Precipitation: {current['precipitation']} mm
Condition: {condition}
Local Time: {current['time']}
"""

# Tool 2: Get weather forecast
@mcp.tool()
async def get_weather_forecast(city: str, days: int = 3) -> str:
    """Get daily weather forecast for a city for up to 7 days."""

    if not 1 <= days <= 7:
        return "Please select between 1 and 7 forecast days."

    location = await get_city_coordinates(city)

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "weather_code"
        ),
        "forecast_days": days,
        "timezone": "auto",
        "temperature_unit": "celsius",
        "precipitation_unit": "mm"
    }

    async with httpx.AsyncClient(timeout=20.0) as client:

        response = await client.get(
            WEATHER_URL,
            params=params
        )

        response.raise_for_status()
        data = response.json()

    daily = data["daily"]

    report = [
        (f"Weather Forecast: {location['name']}, "
        f"{location.get('country', '')}"),
        ""
    ]

    for i in range(len(daily["time"])):

        condition = get_weather_description(
            daily["weather_code"][i]
        )

        report.append(
            f"""
Date: {daily['time'][i]}
Maximum Temperature: {daily['temperature_2m_max'][i]} °C
Minimum Temperature: {daily['temperature_2m_min'][i]} °C
Precipitation: {daily['precipitation_sum'][i]} mm
Condition: {condition}
"""
        )

    return "\n".join(report)

# Start MCP server
if __name__ == "__main__":
    mcp.run()
