import asyncio
import websockets
import json
import time
import psutil

async def receive_data():
    # Performance measurement variables
    cpu_percent_list = []
    memory_usage_mb_list = []
    latency_list = []
    start_time = time.time()
    message_count = 0
    throughput_list = []

    async with websockets.connect('ws://localhost:8765') as websocket:
        print("Connected to server")
        while True:
            # Receive data from the server
            start_receive_time = time.time()  # Start measuring latency
            data_str = await websocket.recv()
            end_receive_time = time.time()  # End measuring latency
            latency = end_receive_time - start_receive_time  # Calculate latency
            latency_list.append(latency)  # Store latency

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

            # Print data if the price change percentage is greater than 1.5%
            if price_change_percent >= 1.5:
                print(f"Symbol: {symbol}, Current Price: {current_price}, Open Price (1 Hour Ago): {open_price}, Price Change (%): {price_change_percent:.2f}, Latency: {latency:.6f} seconds")

            # Performance measurement
            cpu_percent = psutil.cpu_percent()
            memory_usage_mb = psutil.virtual_memory().used / (1024 * 1024)
            cpu_percent_list.append(cpu_percent)
            memory_usage_mb_list.append(memory_usage_mb)

            # Increment message count
            message_count += 1

            # Check test duration
            elapsed_time = time.time() - start_time
            if elapsed_time >= 60:  # End test after 60 seconds
                print("Test duration:", elapsed_time, "seconds")
                print("Average CPU usage:", sum(cpu_percent_list) / len(cpu_percent_list))
                print("Average Memory usage (MB):", sum(memory_usage_mb_list) / len(memory_usage_mb_list))
                print("Average Latency:", sum(latency_list) / len(latency_list))
                throughput = message_count / elapsed_time
                print("Throughput:", throughput, "messages/second")
                break

asyncio.run(receive_data())
