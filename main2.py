import os
from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Sample hotel data for 5 locations
HOTEL_DATA = {
    "new_york": [
        {
            "name": "The Plaza Hotel",
            "rating": 4.5,
            "price_per_night": 450,
            "amenities": ["WiFi", "Pool", "Spa", "Gym", "Restaurant"],
            "availability": True
        },
        {
            "name": "The Standard High Line",
            "rating": 4.2,
            "price_per_night": 320,
            "amenities": ["WiFi", "Bar", "Gym", "Pet-friendly"],
            "availability": True
        },
        {
            "name": "Pod Hotel Brooklyn",
            "rating": 4.0,
            "price_per_night": 180,
            "amenities": ["WiFi", "Restaurant", "Rooftop Bar"],
            "availability": False
        }
    ],
    "paris": [
        {
            "name": "Hotel Plaza Athenee",
            "rating": 4.8,
            "price_per_night": 680,
            "amenities": ["WiFi", "Spa", "Restaurant", "Concierge", "Bar"],
            "availability": True
        },
        {
            "name": "Le Marais Hotel",
            "rating": 4.1,
            "price_per_night": 280,
            "amenities": ["WiFi", "Restaurant", "Historic Building"],
            "availability": True
        },
        {
            "name": "Hotel des Grands Boulevards",
            "rating": 4.3,
            "price_per_night": 350,
            "amenities": ["WiFi", "Restaurant", "Bar", "Garden"],
            "availability": True
        }
    ],
    "tokyo": [
        {
            "name": "The Ritz-Carlton Tokyo",
            "rating": 4.7,
            "price_per_night": 520,
            "amenities": ["WiFi", "Spa", "Pool", "Multiple Restaurants", "City View"],
            "availability": True
        },
        {
            "name": "Shibuya Excel Hotel Tokyu",
            "rating": 4.2,
            "price_per_night": 290,
            "amenities": ["WiFi", "Restaurant", "City Center", "Shopping Access"],
            "availability": True
        },
        {
            "name": "Capsule Hotel Shinjuku 510",
            "rating": 3.8,
            "price_per_night": 80,
            "amenities": ["WiFi", "Shared Bath", "Lockers"],
            "availability": False
        }
    ],
    "london": [
        {
            "name": "The Savoy",
            "rating": 4.6,
            "price_per_night": 590,
            "amenities": ["WiFi", "Spa", "Multiple Restaurants", "Theatre District", "River View"],
            "availability": True
        },
        {
            "name": "Premier Inn London City",
            "rating": 4.0,
            "price_per_night": 120,
            "amenities": ["WiFi", "Restaurant", "24/7 Reception"],
            "availability": True
        },
        {
            "name": "The Zetter Townhouse",
            "rating": 4.4,
            "price_per_night": 380,
            "amenities": ["WiFi", "Bar", "Boutique Style", "Historic"],
            "availability": True
        }
    ],
    "dubai": [
        {
            "name": "Burj Al Arab Jumeirah",
            "rating": 4.9,
            "price_per_night": 1200,
            "amenities": ["WiFi", "Multiple Pools", "Spa", "Private Beach", "Butler Service"],
            "availability": True
        },
        {
            "name": "Atlantis The Palm",
            "rating": 4.5,
            "price_per_night": 480,
            "amenities": ["WiFi", "Water Park", "Aquarium", "Multiple Restaurants", "Beach"],
            "availability": True
        },
        {
            "name": "Rove Downtown Dubai",
            "rating": 4.1,
            "price_per_night": 150,
            "amenities": ["WiFi", "Pool", "Gym", "Restaurant", "City Center"],
            "availability": False
        }
    ]
}


def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set.")
    return init_chat_model("openai:gpt-4.1")


@tool
def search_hotels(location: str, max_price: int = None) -> List[Dict[str, Any]]:
    """
    Search for available hotels in a specific location.

    Args:
        location: The city/location to search for hotels (e.g., 'new_york', 'paris', 'tokyo', 'london', 'dubai')
        max_price: Optional maximum price per night filter

    Returns:
        List of available hotels with details
    """
    location_key = location.lower().replace(" ", "_")

    if location_key not in HOTEL_DATA:
        return {
            "error": f"No hotels found for location: {location}. Available locations: {', '.join(HOTEL_DATA.keys())}"
        }

    hotels = HOTEL_DATA[location_key]
    available_hotels = [hotel for hotel in hotels if hotel["availability"]]

    if max_price is not None:
        available_hotels = [hotel for hotel in available_hotels if hotel["price_per_night"] <= max_price]

    return {
        "location": location,
        "total_available": len(available_hotels),
        "hotels": available_hotels
    }


@tool
def get_hotel_details(location: str, hotel_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific hotel.

    Args:
        location: The city/location of the hotel
        hotel_name: The name of the hotel

    Returns:
        Detailed hotel information
    """
    location_key = location.lower().replace(" ", "_")

    if location_key not in HOTEL_DATA:
        return {"error": f"Location '{location}' not found"}

    hotels = HOTEL_DATA[location_key]
    for hotel in hotels:
        if hotel["name"].lower() == hotel_name.lower():
            return {
                "location": location,
                "hotel_details": hotel,
                "estimated_weekly_cost": hotel["price_per_night"] * 7,
                "estimated_monthly_cost": hotel["price_per_night"] * 30
            }

    return {"error": f"Hotel '{hotel_name}' not found in {location}"}


@tool
def calculate_booking_cost(price_per_night: int, nights: int, tax_rate: float = 0.12) -> Dict[str, float]:
    """
    Calculate the total cost of a hotel booking including taxes.

    Args:
        price_per_night: Price per night in USD
        nights: Number of nights
        tax_rate: Tax rate (default 12%)

    Returns:
        Breakdown of booking costs
    """
    subtotal = price_per_night * nights
    tax = subtotal * tax_rate
    total = subtotal + tax

    return {
        "price_per_night": price_per_night,
        "nights": nights,
        "subtotal": subtotal,
        "tax": round(tax, 2),
        "total_cost": round(total, 2)
    }


@tool
def get_available_locations() -> List[str]:
    """
    Get all available booking locations.

    Returns:
        List of available cities/locations
    """
    return {
        "available_locations": list(HOTEL_DATA.keys()),
        "total_locations": len(HOTEL_DATA)
    }


# Define tools list
tools = [search_hotels, get_hotel_details, calculate_booking_cost, get_available_locations]


def process_hotel_query(query: str) -> str:
    """
    Process a hotel-related query and return a string response.

    Args:
        query: The hotel-related question or request

    Returns:
        String response with hotel information
    """
    try:
        llm = get_llm()
        llm_with_tools = llm.bind_tools(tools)

        messages = [HumanMessage(query)]
        ai_msg = llm_with_tools.invoke(messages)

        # Process tool calls if any
        if hasattr(ai_msg, 'tool_calls') and ai_msg.tool_calls:
            results = []

            for tool_call in ai_msg.tool_calls:
                # Find the corresponding tool function
                tool_map = {
                    "search_hotels": search_hotels,
                    "get_hotel_details": get_hotel_details,
                    "calculate_booking_cost": calculate_booking_cost,
                    "get_available_locations": get_available_locations
                }

                selected_tool = tool_map.get(tool_call["name"].lower())
                if selected_tool:
                    tool_output = selected_tool.invoke(tool_call["args"])
                    results.append(f"Tool: {tool_call['name']}\nResult: {tool_output}")
                    messages.append(ToolMessage(str(tool_output), tool_call_id=tool_call["id"]))

            # Get final AI response after tool execution
            final_response = llm_with_tools.invoke(messages)

            # Combine tool results with AI response
            response_parts = []
            if results:
                response_parts.extend(results)
            if hasattr(final_response, 'content') and final_response.content:
                response_parts.append(f"AI Response: {final_response.content}")

            return "\n\n".join(response_parts)
        else:
            # Return direct AI response if no tools were called
            return ai_msg.content if hasattr(ai_msg, 'content') else str(ai_msg)

    except Exception as e:
        return f"Error processing query: {str(e)}"


def main():
    try:
        print("Hotel Booking LLM System")
        print("=" * 50)

        # Test the new process_hotel_query function
        test_queries = [
            "What hotels are available in Tokyo under $300 per night?",
            "Show me details for The Savoy hotel in London and calculate the cost for 5 nights",
            "What are all the available booking locations?",
            "Find me a luxury hotel in Dubai with spa facilities"
        ]

        print("Testing process_hotel_query function:")
        print("=" * 50)

        for i, query in enumerate(test_queries, 1):
            print(f"\nQuery {i}: {query}")
            print("-" * 40)

            # Use the new function
            response = process_hotel_query(query)
            print(response)
            print("=" * 50)

        # Example of how to use the function programmatically
        print("\nProgrammatic Usage Example:")
        print("-" * 30)
        user_query = "What's the cheapest hotel in Paris?"
        result = process_hotel_query(user_query)
        print(f"Query: {user_query}")
        print(f"Response: {result}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nTo run this program, make sure to:")
        print("1. Set your OPENAI_API_KEY environment variable")
        print("2. Install required packages: pip install langchain langchain-openai")


if __name__ == "__main__":
    main()