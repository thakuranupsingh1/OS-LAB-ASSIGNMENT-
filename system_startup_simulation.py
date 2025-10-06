# system_startup_simulation.py
# This script simulates a basic OS startup, process creation, and shutdown.

import multiprocessing
import time
import logging
import random

# Sub-Task 1: Initialize the logging configuration.
# We configure the logger to write to 'process_log.txt'.
# The format includes the timestamp, the process name, and the message,
# which is crucial for tracking concurrent operations.
logging.basicConfig(
    filename='process_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(processName)s - %(message)s',
    # Clear the log file on each run by setting filemode to 'w'
    filemode='w' 
)

# Sub-Task 2: Define a function that simulates a process task.
# This function acts as a dummy system service (e.g., networking, database).
# It logs its start and end times and sleeps for a random duration
# to simulate performing some work.
def system_service(service_name):
    """
    Simulates a system service that runs for a short, random duration.
    Args:
        service_name (str): The name of the service to simulate.
    """
    # Log the start of the task.
    logging.info(f"Service '{service_name}' started.")
    
    # Simulate work with a random delay between 2 and 4 seconds.
    work_duration = random.uniform(2, 4)
    time.sleep(work_duration)
    
    # Log the completion of the task.
    logging.info(f"Service '{service_name}' finished in {work_duration:.2f} seconds.")

# The main execution block.
# This ensures the code inside only runs when the script is executed directly.
if __name__ == '__main__':
    # Log the beginning of the system startup from the main process.
    logging.info("System boot sequence initiated.")
    print("🚀 System Starting...")

    # Define the services to be run as separate processes.
    services = ['NetworkService', 'DatabaseService', 'LoggingService']
    processes = []

    # Sub-Task 3: Create and start processes concurrently.
    for service in services:
        # We create a Process object, giving it a target function to execute
        # and a name for easy identification in logs.
        process = multiprocessing.Process(target=system_service, name=service, args=(service,))
        processes.append(process)
        # The start() method spawns a new process and executes the target function.
        process.start()
        logging.info(f"Launched {process.name}.")

    logging.info("All services launched. Main process is now waiting for them to complete.")
    print("⚙️  All services are running concurrently...")

    # Sub-Task 4: Ensure proper termination and joining of processes.
    # The join() method makes the main process wait until the child process
    # has finished its execution. This is crucial for a graceful shutdown.
    for process in processes:
        process.join()

    # Log the final shutdown message.
    logging.info("All services have completed. System is shutting down.")
    print("✅ System Shutdown Gracefully.")
