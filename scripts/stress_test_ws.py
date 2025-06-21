import asyncio
import websockets
import time
import multiprocessing

# Configuration
WEBSOCKET_URL = "ws://127.0.0.1:5000/ws/devactyl-app/2.4/DEVACTYL_759050921413312532"
CLIENTS_PER_PROCESS = 100     # Clients per process
NUM_PROCESSES = 4            # Number of CPU cores/processes to use
DURATION = 3600                # Time to keep connections open (in seconds)

async def stay_connected(client_id):
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            print(f"[Client {client_id}] Connected")
            await asyncio.sleep(DURATION)  # Just keep the connection alive
    except Exception as e:
        print(f"[Client {client_id}] Connection error: {e}")

async def run_clients(start_id, count):
    tasks = [asyncio.create_task(stay_connected(start_id + i)) for i in range(count)]
    await asyncio.gather(*tasks)

def worker(start_id, count):
    asyncio.run(run_clients(start_id, count))

def main():
    processes = []
    for i in range(NUM_PROCESSES):
        start_id = i * CLIENTS_PER_PROCESS
        p = multiprocessing.Process(target=worker, args=(start_id, CLIENTS_PER_PROCESS))
        time.sleep(0.5)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

if __name__ == "__main__":
    main()
