import asyncio
import websockets
import json

# List of USDT pairs to subscribe to
#list_pairs = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
def get_trading_pairs(filename):
  """
  This function reads a text file containing trading pairs in the format
  "EXCHANGE:PAIR" (e.g., "BINANCE:BTCUSDT") and returns a list of the pairs
  without the exchange prefix.

  Args:
      filename (str): The name of the text file containing trading pairs.

  Returns:
      list: A list of trading pairs (e.g., ["BTCUSDT", "ETHUSDT", ...]).
  """

  list_pairs = []
  with open(filename, 'r') as file:
    for line in file:
      # Remove leading/trailing whitespace and split by colon
      pair = line.strip().split(':')

      # Extract the trading pair (assuming it's the second element)
      if len(pair) > 1:
        list_pairs.append(pair[1])

  return list_pairs

# Example usage
filename = "binance-usdt.txt"  # Replace with your actual filename
list_pairs = get_trading_pairs(filename)

#print(list_pairs)

async def send_data_to_clients(websocket, path):
    print("Client connected")

    # Construct the WebSocket URL with the list of pairs
    pairs_string = "/".join(f"{pair.lower()}@kline_1h" for pair in list_pairs)
    ws_url = f"wss://fstream.binance.com:443/ws/{pairs_string}"

    async with websockets.connect(ws_url) as ws:
        try:
            while True:
                data_str = await ws.recv()
                await websocket.send(data_str)  # Forward data to the client
        except websockets.exceptions.ConnectionClosedOK:
            print("Client disconnected")
        except Exception as e:
            print("Error:", e)

# Start the WebSocket server
start_server = websockets.serve(send_data_to_clients, "localhost", 8765)

async def server_start():
    print("Server started")
    await start_server

asyncio.get_event_loop().run_until_complete(server_start())
asyncio.get_event_loop().run_forever()
