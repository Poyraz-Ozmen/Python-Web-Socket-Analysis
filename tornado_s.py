import tornado.ioloop
import tornado.web
import tornado.websocket
import asyncio
import websockets

# Store WebSocket connections
websocket_connections = set()

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

# Load trading pairs from file
filename = "binance-usdt.txt"  # Replace with your actual filename
list_pairs = get_trading_pairs(filename)

async def send_data_to_clients(websocket):
    print("Client connected")

    try:
        # Construct the WebSocket URL with the list of pairs
        pairs_string = "/".join(f"{pair.lower()}@kline_1h" for pair in list_pairs)
        ws_url = f"wss://fstream.binance.com:443/ws/{pairs_string}"

        async with websockets.connect(ws_url) as ws:
            print("Connected to Binance WebSocket API")
            while True:
                data_str = await ws.recv()
                #print("Received data from Binance API:", data_str)  # Print raw data received from Binance API
                await websocket.write_message(data_str)  # Forward data to the client
    except Exception as e:
        print("Error:", e)
        await websocket.close()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")
        websocket_connections.add(self)
        asyncio.create_task(send_data_to_clients(self))

    def on_close(self):
        print("WebSocket closed")
        websocket_connections.remove(self)

def make_app():
    return tornado.web.Application([
        (r"/", WebSocketHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8889)  # Change port if necessary
    print("WebSocket server is running on port 8889")
    tornado.ioloop.IOLoop.current().start()
