import asyncio
import tornado.websocket
import json

class WebSocketClient(tornado.websocket.WebSocketClientConnection):
    async def on_message(self, message):
        # Calculate price change percentage and print if necessary
        data = json.loads(message)
        symbol = data['s'].upper()
        current_price = float(data['k']['c'])
        open_price = float(data['k']['o'])
        price_change_percent = ((current_price - open_price) / open_price) * 100

        if abs(price_change_percent) >= 1.5:
            print(f"Symbol: {symbol}, Current Price: {current_price}, Open Price (1 Hour Ago): {open_price}, Price Change (%): {price_change_percent:.2f}")

        # Call the parent method to handle message reception
        await super().on_message(message)

async def connect_to_server():
    url = "ws://localhost:8889/"
    try:
        print("Connecting to server...")
        client = await tornado.websocket.websocket_connect(url, connect_timeout=10)
        print("Connected to server")
        return client
    except Exception as e:
        print("Error connecting to server:", e)
        return None
    
async def main():
    client = await connect_to_server()
    if client:
        while True:
            message = await client.read_message()
            if message is not None:
                data = json.loads(message)
                symbol = data['s'].upper()
                current_price = float(data['k']['c'])
                open_price = float(data['k']['o'])
                price_change_percent = ((current_price - open_price) / open_price) * 100
                #print(f"Symbol: {symbol}, Current Price: {current_price}, Open Price (1 Hour Ago): {open_price}, Price Change (%): {price_change_percent:.2f}")
                # Print data if the price change percentage is greater than 2%
                if price_change_percent >= 0:
                    print(f"Symbol: {symbol}, Current Price: {current_price}, Open Price (1 Hour Ago): {open_price}, Price Change (%): {price_change_percent:.2f}")
            else:
                print("Connection closed by the server.")
                break


if __name__ == "__main__":
    asyncio.run(main())
