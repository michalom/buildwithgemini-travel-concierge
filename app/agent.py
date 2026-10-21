# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo
import json
import uuid
import requests
from google.cloud import firestore
from google.cloud import storage
from google import genai

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.genai import types

MODEL = "gemini-3.1-pro-preview"

# CRITICAL: Hardcoding the project ID as requested to avoid issues with Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-67102be14323"
BUCKET_NAME = "travel-concierge-assets-vzfk1d"

def get_weather(query: str) -> str:
    """Fetches the current real weather for a destination.

    Args:
        query: A string containing the location to get weather information for (e.g. 'San Francisco').

    Returns:
        A string with the real weather information for the queried location.
    """
    try:
        url = f"https://wttr.in/{query.replace(' ', '+')}?format=3"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        return f"Error fetching weather for {query}: {str(e)}"


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"

def get_hotels(destination: str) -> str:
    """Search for hotels in a specific destination from the database.
    
    Args:
        destination: The name of the destination (e.g. 'San Francisco', 'New York').
    
    Returns:
        A JSON string containing the list of available hotels and their details.
    """
    db = firestore.Client(project=PROJECT_ID)
    hotels_ref = db.collection("hotels")
    query = hotels_ref.where(filter=firestore.FieldFilter("destination", "==", destination)).stream()
    
    results = []
    for doc in query:
        results.append(doc.to_dict())
        
    if not results:
        return f"No hotels found for {destination}."
    
    return json.dumps(results)

def add_hotel(id: str, name: str, destination: str, price_per_night: int, amenities: list[str]) -> str:
    """Add a new hotel to the catalog database.
    
    Args:
        id: Unique identifier for the hotel (e.g. 'hotel-ny-3').
        name: Name of the hotel.
        destination: City or location of the hotel.
        price_per_night: Estimated price per night in USD.
        amenities: List of amenities (e.g. ['WiFi', 'Pool']).
    
    Returns:
        A string confirming the hotel was added.
    """
    db = firestore.Client(project=PROJECT_ID)
    hotel_data = {
        "id": id,
        "name": name,
        "destination": destination,
        "price_per_night": price_per_night,
        "amenities": amenities,
        "rating": 5.0 # default rating for new hotels
    }
    db.collection("hotels").document(id).set(hotel_data)
    return f"Hotel '{name}' in {destination} added successfully."

def save_itinerary(user_name: str, destination: str, hotel_id: str, activities: list[str]) -> str:
    """Saves a user's finalized trip itinerary to the database.
    
    Args:
        user_name: The name of the user planning the trip.
        destination: The destination city.
        hotel_id: The ID of the selected hotel.
        activities: A list of planned activities.
        
    Returns:
        A string confirming the itinerary was saved with its unique ID.
    """
    db = firestore.Client(project=PROJECT_ID)
    itinerary_id = f"itin-{uuid.uuid4().hex[:8]}"
    
    itinerary_data = {
        "id": itinerary_id,
        "user_name": user_name,
        "destination": destination,
        "hotel_id": hotel_id,
        "activities": activities,
        "created_at": firestore.SERVER_TIMESTAMP
    }
    
    db.collection("itineraries").document(itinerary_id).set(itinerary_data)
    return f"Itinerary saved successfully with ID: {itinerary_id}"

def get_exchange_rate(base_currency: str = "USD", target_currency: str = "IDR") -> str:
    """Fetches the live exchange rate between two currencies.
    
    Args:
        base_currency: The 3-letter currency code to convert from (default: USD).
        target_currency: The 3-letter currency code to convert to (default: IDR).
        
    Returns:
        A string with the exchange rate information or an error message.
    """
    try:
        url = f"https://open.er-api.com/v6/latest/{base_currency.upper()}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data["result"] == "success":
            rates = data.get("rates", {})
            target = target_currency.upper()
            if target in rates:
                return f"The current exchange rate is 1 {base_currency.upper()} = {rates[target]} {target}."
            else:
                return f"Currency {target} not found in the exchange rate data."
        else:
            return "Failed to fetch exchange rates."
    except Exception as e:
        return f"Error fetching exchange rate: {str(e)}"

def get_destination_guide(place: str) -> str:
    """Fetches a destination guide, historical overview, and highlights for a city, country, or point of interest.

    Args:
        place: The name of the city, region, or attraction (e.g. 'Bali', 'Eiffel Tower', 'Kyoto').

    Returns:
        A summary description of the place.
    """
    try:
        formatted_place = place.strip().replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_place}"
        headers = {"User-Agent": "TravelConciergeAgent/1.0 (contact@example.com)"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        extract = data.get("extract", "")
        if extract:
            return f"Overview for {data.get('title', place)}:\n{extract}"
        return f"No guide found for {place}."
    except Exception as e:
        return f"Error fetching destination guide for {place}: {str(e)}"

def generate_travel_image(prompt: str, tool_context: ToolContext) -> str:
    """Generates an image for a destination, landmark, mood board, or travel item using gemini-3.1-flash-lite-image.

    Args:
        prompt: A descriptive prompt describing what image to generate (e.g. 'A scenic sunset view of Mount Fuji with cherry blossoms').
        tool_context: The ADK tool context for recording session artifacts.

    Returns:
        The public HTTPS URL of the uploaded image in Cloud Storage.
    """
    try:
        client = genai.Client(vertexai=True, location="global")
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
        )

        image_bytes = None
        mime_type = "image/jpeg"
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break

        if not image_bytes:
            return "Error: No image was generated by the model."

        filename = f"image_{uuid.uuid4().hex[:8]}.jpg"

        # 1. Save with tool_context.save_artifact so it shows up in Playground's Artifacts panel
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload the same image bytes to the public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return f"Image generated successfully. Public URL: {public_url}"
    except Exception as e:
        return f"Error generating image: {str(e)}"

from google.adk.code_executors import AgentEngineSandboxCodeExecutor

root_agent = Agent(
    name="travel_concierge",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are a helpful Travel Concierge AI assistant. 
    You help users plan their trips by finding hotels, checking weather, providing destination guides, generating destination images/mood boards, and managing itineraries.
    You have access to a database of hotels and public tools. Always check the database when users ask about accommodations.
    You also have a secure python code execution sandbox environment. Write and execute python to perform calculations, convert formats, write files, process data, or any other tasks best solved with programming.""",
    tools=[
        get_weather,
        get_current_time,
        get_hotels,
        add_hotel,
        save_itinerary,
        get_exchange_rate,
        get_destination_guide,
        generate_travel_image,
    ],
    code_executor=AgentEngineSandboxCodeExecutor(
        agent_engine_resource_name="projects/642983050889/locations/us-east1/reasoningEngines/837364965970018304"
    ),
)

app = App(
    root_agent=root_agent,
    name="app",
)
