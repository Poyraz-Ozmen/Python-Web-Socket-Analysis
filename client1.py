import asyncio
import websockets
import json

# Dictionary to store the open price for each symbol
open_prices = {}

async def receive_data():
    async with websockets.connect('ws://localhost:8765') as websocket:
        print("Connected to server")
        while True:
            # Receive data from the server
            data_str = await websocket.recv()
            if not data_str:
                print("Disconnected from server")
                break
            data = json.loads(data_str)

            # Extract symbol, current price, and open price from the received data
            symbol = data['s'].upper()  # Convert symbol to uppercase
            current_price = float(data['k']['c'])
            open_price = float(data['k']['o'])

            # Calculate price change percentage
            price_change_percent = ((current_price - open_price) / open_price) * 100

            # Print data if the price change percentage is greater than 2%
            if price_change_percent >= 1.5:
                print(f"Symbol: {symbol}, Current Price: {current_price}, Open Price (1 Hour Ago): {open_price}, Price Change (%): {price_change_percent:.2f}")

asyncio.run(receive_data())
