import tornado.ioloop
import tornado.web
import tornado.websocket
import asyncio
import websockets
import psutil
import time

websocket_connections = set()

def get_trading_pairs(filename):
    list_pairs = []
    with open(filename, 'r') as file:
        for line in file:
            pair = line.strip().split(':')
            if len(pair) > 1:
                list_pairs.append(pair[1])
    return list_pairs

filename = "binance-usdt.txt"  # Replace with your actual filename
list_pairs = get_trading_pairs(filename)

async def send_data_to_clients(websocket):
    print("Client connected")

    try:
        pairs_string = "/".join(f"{pair.lower()}@kline_1h" for pair in list_pairs)
        ws_url = f"wss://fstream.binance.com:443/ws/{pairs_string}"

        async with websockets.connect(ws_url) as ws:
            print("Connected to Binance WebSocket API")
            while True:
                data_str = await ws.recv()
                await websocket.write_message(data_str)
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

async def measure_performance():
    cpu_percent_list = []
    memory_usage_mb_list = []
    start_time = time.time()
    while True:
        await asyncio.sleep(1)
        cpu_percent = psutil.cpu_percent()
        memory_usage_mb = psutil.virtual_memory().used / (1024 * 1024)
        cpu_percent_list.append(cpu_percent)
        memory_usage_mb_list.append(memory_usage_mb)
        elapsed_time = time.time() - start_time
        if elapsed_time >= 60:
            print("Test duration:", elapsed_time, "seconds")
            print("Average CPU usage:", sum(cpu_percent_list) / len(cpu_percent_list))
            print("Average Memory usage (MB):", sum(memory_usage_mb_list) / len(memory_usage_mb_list))
            tornado.ioloop.IOLoop.current().stop()  # Stop the event loop after the test duration
            break

if __name__ == "__main__":
    app = make_app()
    app.listen(8889)
    print("WebSocket server is running on port 8889")
    tornado.ioloop.IOLoop.current().add_callback(measure_performance)
    tornado.ioloop.IOLoop.current().start()
