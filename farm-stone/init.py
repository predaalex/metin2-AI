import multiprocessing
import time


def worker_function(event, worker_id):
    while True:
        print(f"Worker {worker_id} is waiting for the command from the master.")
        event.wait()  # Wait for the master's command
        print(f"Worker {worker_id} received the command from the master and is now executing.")

        # Simulate some work in the worker
        print(f"Worker {worker_id} is doing some work...")
        time.sleep(2)

        # Clear the event to wait for the next command
        event.clear()


if __name__ == "__main__":
    event = multiprocessing.Event()
    event.clear()  # Initially, the event is cleared

    num_workers = 3
    workers = []

    for i in range(num_workers):
        worker = multiprocessing.Process(target=worker_function, args=(event, i))
        workers.append(worker)
        worker.start()

    # Simulate the master thread sending a command to the workers
    for _ in range(3):
        print("Master is sending a command to the workers...")
        event.set()  # Signal the workers to execute

        # Simulate some work in the master
        print("Master is doing some work...")
        time.sleep(2)

    # Wait for the workers to finish
    for worker in workers:
        worker.join()
