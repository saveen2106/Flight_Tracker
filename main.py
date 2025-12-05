import sys
import argparse
from rich.console import Console
from rich.table import Table
from src.tracker import FlightTracker

console = Console()


def main():
    parser = argparse.ArgumentParser(description='Flight Ticket Price Tracker')
    parser.add_argument('--days', type=int, default=60, help='Number of days to search (default: 60)')
    args = parser.parse_args()

    console.print("[bold blue]Flight Ticket Price Tracker[/bold blue]")
    console.print(f"Tracks cheapest flights for the next {args.days} days.\n")

    origin = console.input("Enter [bold green]Origin[/bold green] (IATA code, e.g., JFK): ").upper()
    destination = console.input("Enter [bold green]Destination[/bold green] (IATA code, e.g., LHR): ").upper()

    if len(origin) != 3 or len(destination) != 3:
        console.print("[bold red]Error:[/bold red] Invalid IATA code format. Please use 3 letters.")
        return

    try:
        tracker = FlightTracker()
    except ValueError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        console.print("Please create a .env file with AMADEUS_API_KEY and AMADEUS_API_SECRET.")
        return
    except Exception as e:
        console.print(f"[bold red]Initialization Error:[/bold red] {e}")
        return

    console.print(f"\nSearching for flights from [bold]{origin}[/bold] to [bold]{destination}[/bold]...")
    
    flights = tracker.find_cheapest_flights(origin, destination, days=args.days)

    if not flights:
        console.print("\n[bold yellow]No flights found.[/bold yellow] Check your route or API quota.")
        return

    # Display results in a table
    table = Table(title=f"Cheapest Flights: {origin} -> {destination}")
    table.add_column("Date", style="cyan")
    table.add_column("Price", style="green")
    table.add_column("Airline", style="magenta")

    # Show top 10 cheapest
    for flight in flights[:10]:
        table.add_row(
            flight['date'],
            f"{flight['price']} {flight['currency']}",
            flight['airline']
        )

    console.print("\n")
    console.print(table)
    
    if len(flights) > 0:
        best = flights[0]
        console.print(f"\n[bold]Best Deal:[/bold] {best['date']} for {best['price']} {best['currency']}")

if __name__ == "__main__":
    main()
