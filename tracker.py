import os
from datetime import datetime, timedelta
from amadeus import Client, ResponseError
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import track

load_dotenv()
console = Console()

class FlightTracker:
    def __init__(self):
        self.api_key = os.getenv('AMADEUS_API_KEY')
        self.api_secret = os.getenv('AMADEUS_API_SECRET')
        
        if not self.api_key or not self.api_secret:
            raise ValueError("API keys not found. Please check your .env file.")

        try:
            self.amadeus = Client(
                client_id=self.api_key,
                client_secret=self.api_secret
            )
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Amadeus client: {e}")

    def find_cheapest_flights(self, origin, destination, days=60):
        """
        Searches for flights from origin to destination for the next 'days' days.
        Returns a list of cheapest flights found.
        """
        cheapest_flights = []
        start_date = datetime.today() + timedelta(days=1) # Start tomorrow

        # Generate list of dates to check
        dates_to_check = [start_date + timedelta(days=i) for i in range(days)]

        for date in track(dates_to_check, description="Scanning dates..."):
            date_str = date.strftime('%Y-%m-%d')
            try:
                response = self.amadeus.shopping.flight_offers_search.get(
                    originLocationCode=origin,
                    destinationLocationCode=destination,
                    departureDate=date_str,
                    adults=1,
                    max=1  # We only need the cheapest one per day
                )
                
                if response.data:
                    offer = response.data[0]
                    price = float(offer['price']['total'])
                    currency = offer['price']['currency']
                    cheapest_flights.append({
                        'date': date_str,
                        'price': price,
                        'currency': currency,
                        'airline': offer['validatingAirlineCodes'][0],
                        'id': offer['id']
                    })
            except ResponseError as error:
                # Handle rate limits or no flights found gracefully
                # console.print(f"[yellow]Warning:[/yellow] Could not fetch data for {date_str}: {error}")
                pass
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")

        # Sort by price
        cheapest_flights.sort(key=lambda x: x['price'])
        return cheapest_flights
