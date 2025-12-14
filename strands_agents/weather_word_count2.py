from strands import Agent, tool
from strands.models import BedrockModel
from strands_tools import http_request

# Define a weather-focused system prompt
WEATHER_SYSTEM_PROMPT = """You are a weather assistant with HTTP capabilities. You can:

1. Make HTTP requests to the Open-Meteo API
2. Process and display weather forecast data
3. Provide weather information for locations in Germany

When retrieving weather information:
1. First get latitude and longitudethe for the city using https://geocoding-api.open-meteo.com/v1/search?name={cityname}
2. Use the latitude and longitudethe from the previous step and get the weather using https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}
2. Then use the returned forecast URL to get the actual forecast

When displaying responses:
- Format weather data in a human-readable way
- Highlight important information like temperature, precipitation, and alerts
- Handle errors appropriately
- Convert technical terms to user-friendly language

Always explain the weather conditions clearly and provide context for the forecast.
"""


@tool
def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split())


# Bedrock
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.3,
)

agent = Agent(
    system_prompt=WEATHER_SYSTEM_PROMPT,
    tools=[word_count, http_request],
    model=bedrock_model,
)
response = agent(
    "What's the weather like in Berlin? Also how many words are in the response? Дай также рекомендации что лучше одеть и надо ли брать с собой зонт. Give the answer in Russian."
)
