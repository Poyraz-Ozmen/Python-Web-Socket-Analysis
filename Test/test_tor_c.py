import asyncio
import tornado.websocket
import json
import psutil
import time

class WebSocketClient(tornado.websocket.WebSocketClientConnection):
    async def on_message(self, message):
        data = json.loads(message)
        symbol = data['s'].upper()
        current_price = float(data['k']['c'])
        open_price = float(data['k']['o'])
        price_change_percent = ((current_price - open_price) / open_price) * 100

        if abs(price_change_percent) >= 1.5:
            print(f"Symbol: {symbol}, Current Price: {current_price}, Open Price (1 Hour Ago): {open_price}, Price Change (%): {price_change_percent:.2f}")

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
        start_time = time.time()
        cpu_percent_list = []
        memory_usage_mb_list = []
        latency_sum = 0
        messages_received = 0

        while True:
            message = await client.read_message()
            if message is not None:
                data = json.loads(message)
                symbol = data['s'].upper()
                current_price = float(data['k']['c'])
                open_price = float(data['k']['o'])
                price_change_percent = ((current_price - open_price) / open_price) * 100
                if price_change_percent >= 0:
                    print(f"Symbol: {symbol}, Current Price: {current_price}, Open Price (1 Hour Ago): {open_price}, Price Change (%): {price_change_percent:.2f}")
                    messages_received += 1
            else:
                print("Connection closed by the server.")
                break

            # Measure latency
            latency = time.time() - start_time
            latency_sum += latency

            # Measure CPU usage and memory usage
            cpu_percent = psutil.cpu_percent()
            memory_usage_mb = psutil.virtual_memory().used / (1024 * 1024)
            cpu_percent_list.append(cpu_percent)
            memory_usage_mb_list.append(memory_usage_mb)

            elapsed_time = time.time() - start_time
            if elapsed_time >= 60:
                print("Test duration:", elapsed_time, "seconds")
                print("Average CPU usage:", sum(cpu_percent_list) / len(cpu_percent_list))
                print("Average Memory usage (MB):", sum(memory_usage_mb_list) / len(memory_usage_mb_list))
                print("Average Latency:", latency_sum / messages_received)
                print("Throughput:", messages_received / elapsed_time, "messages/second")
                break


if __name__ == "__main__":
    asyncio.run(main())
