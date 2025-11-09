from crewai import Agent, Task, Crew
from crewai.tools import tool
import requests
import pycountry
import os
import json
from serpapi import GoogleSearch
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Utility for keys ---
def get_env_key(key_name):
    value = os.getenv(key_name)
    if not value:
        raise RuntimeError(f"{key_name} not set in environment")
    return value


# ------------------ TOOLS ------------------

@tool("get_country_code")
def get_country_code(country_name: str):
    """Fetch the ISO 3166-1 alpha-2 country code for a given country name."""
    try:
        country = pycountry.countries.get(name=country_name)
        if not country:
            for c in pycountry.countries:
                if country_name.lower() in c.name.lower():
                    return c.alpha_2
        return country.alpha_2 if country else None
    except Exception as e:
        print(f"Error getting country code: {e}")
        return None


@tool("get_iata_code")
def get_iata_code(city: str, country_code: str):
    """
    Fetch the IATA code for a given city using the AviationStack API.
    Takes a country_code ('IN', 'US', etc.), not a country name.
    """
    aviation_stackKey = get_env_key("aviation_stackKey")

    url = f"http://api.aviationstack.com/v1/airports?access_key={aviation_stackKey}&country_iso2={country_code}"
    response = requests.get(url).json()
    airports = response.get("data", [])

    for airport in airports:
        if city.lower() in airport.get("airport_name", "").lower():
            return airport.get("iata_code")

    return None


@tool("get_flights")
def get_flights(outbound_date: str, dep_code: str, arr_code: str, max_price=10000, return_date=None):
    """
    Search flights between two IATA codes using the SERP API Google Flights engine.
    """
    SERP_API = get_env_key("SERP_API")
    print("Searching flights with SERP API...")

    params = {
        "api_key": SERP_API,
        "engine": "google_flights",
        "hl": "en",
        "gl": "us",
        "departure_id": dep_code,
        "arrival_id": arr_code,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "currency": "INR",
        "max_price": max_price,
        "type": 2
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    print(results)

    flights = []
    for flight in results.get("best_flights", []):
        try:
            flights.append({
                "departure_airport": flight["flights"][0].get("departure_airport"),
                "arrival_airport": flight["flights"][0].get("arrival_airport"),
                "airline": flight["flights"][0].get("airline"),
                "flight_number": flight["flights"][0].get("flight_number"),
                "travel_class": flight["flights"][0].get("travel_class"),
                "price": flight.get("price"),
            })
        except Exception:
            continue

    return flights


@tool("get_hotels")
def get_hotels(destination: str, checkin_date: str, checkout_date: str, max_price: int = 10000, adults: int = 2, children: int = 0, children_ages: list = []):
    """Search best hotels in a city using Google Hotels via SERP API."""
    SERP_API = get_env_key("SERP_API")

    params = {
        "api_key": SERP_API,
        "engine": "google_hotels",
        "q": destination,
        "hl": "en",
        "gl": "in",
        "check_in_date": checkin_date,
        "check_out_date": checkout_date,
        "currency": "INR",
        "sort_by": "13",  # best match
        "adults": adults,
        "max_price": max_price,
        "children": children,
        "children_ages": ",".join(map(str, children_ages)) if children_ages else "",
    }

    try:
        print("Searching hotels with SERP API...")
        search = GoogleSearch(params)
        results = search.get_dict()
        print(results)
    except Exception as e:
        print(f"Error fetching hotels: {e}")

    hotels = []
    for hotel in results.get("properties", []):
        rate_info = hotel.get("rate_per_night", {})
        hotels.append({
            "name": hotel.get("name"),
            "rate": rate_info.get("lowest"),
            "overall_rating": hotel.get("overall_rating"),
            "hotel_class": hotel.get("hotel_class"),
            "nearby_places": hotel.get("nearby_places")
        })
    return hotels


@tool("get_places")
def get_places(location: str):
    """Fetch top tourist places in a city using Google Local results."""
    SERP_API = get_env_key("SERP_API")

    params = {
        "api_key": SERP_API,
        "engine": "google_local",
        "google_domain": "google.co.in",
        "q": f"Best tourist places in {location}",
        "hl": "en",
        "gl": "in",
        "location": location,
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    local_results = results.get("local_results", [])
    places = [
        {
            "title": place.get("title"),
            "address": place.get("address"),
            "type": place.get("type")
        }
        for place in local_results
    ]
    return places


'''
We are Planning to go on 4 day trip from Bangalore to Goa on 20th November 2025. Plan our trip
'''