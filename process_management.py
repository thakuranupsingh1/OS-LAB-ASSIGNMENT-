#!/usr/bin/env python3

import os
import sys
import time
import argparse
import subprocess

# A simple CPU-intensive function for Task 5
def cpu_bound_task():
    """A simple function to consume CPU time."""
    count = 0
    for _ in range(10**7):
        count += 1

## Task 1: Process Creation Utility
def task1_create_processes(n):
    """
    Creates N child processes using os.fork().
    The parent waits for all children to complete.
    """
    print(f"--- Running Task 1: Creating {n} Child Processes ---")
    child_pids = []
    parent_pid = os.getpid()
    print(f"Parent Process PID: {parent_pid}")

    for i in range(n):
        pid = os.fork()

        if pid == 0:
            # Child process
            time.sleep(i + 1) # Stagger children for clean output
            print(f"  -> Child-{i+1}: My PID is {os.getpid()}, My Parent's PID is {os.getppid()}.")
            os._exit(0) # Child exits
        else:
            # Parent process
            print(f"Parent: Created child with PID: {pid}")
            child_pids.append(pid)

    # Parent waits for all children
    for child_pid in child_pids:
        waited_pid, status = os.waitpid(child_pid, 0)
        print(f"Parent: Child {waited_pid} has finished with status {status}.")
    
    print("Parent: All children have completed.\n")


## Task 2: Command Execution Using exec()
def task2_execute_commands(commands):
    """
    Each forked child executes a Linux command.
    """
    print(f"--- Running Task 2: Executing Commands in Children ---")
    parent_pid = os.getpid()
    print(f"Parent Process PID: {parent_pid}")

    for cmd_str in commands:
        pid = os.fork()

        if pid == 0:
            # Child process
            print(f"\nChild {os.getpid()}: Executing '{cmd_str}'...")
            try:
                # Split the command string into a list for execvp
                cmd_args = cmd_str.split()
                os.execvp(cmd_args[0], cmd_args)
            except FileNotFoundError:
                print(f"Error: Command not found '{cmd_str}'")
                os._exit(1)
        else:
            # Parent process
            os.wait() # Wait for the immediate child to finish
    
    print("\nParent: All commands executed by children.\n")


## Task 3: Zombie & Orphan Processes
def task3_zombie_process():
    """
    Demonstrates a zombie process by having the parent not wait for the child.
    """
    print("--- Running Task 3: Simulating a Zombie Process ---")
    pid = os.fork()

    if pid == 0:
        # Child process
        print(f"Child ({os.getpid()}): I am alive but will exit immediately.")
        os._exit(0)
    else:
        # Parent process
        print(f"Parent ({os.getpid()}): I created a child ({pid}) but I will not wait for it.")
        print("Parent: I am going to sleep for 30 seconds.")
        print(">>> NOW, open a new terminal and run: ps -el | grep 'Z'")
        print(">>> You should see a process with PID", pid, "marked as <defunct>.")
        time.sleep(30)
        # Parent finally waits, allowing the zombie to be cleaned up
        os.wait()
        print("Parent: Woke up and reaped the child. The zombie is gone.\n")

def task3_orphan_process():
    """
    Demonstrates an orphan process by having the parent exit before the child.
    """
    print("--- Running Task 3: Simulating an Orphan Process ---")
    pid = os.fork()

    if pid == 0:
        # Child process
        print(f"Child ({os.getpid()}): My parent is {os.getppid()}.")
        print("Child: My parent is about to die. I will be an orphan.")
        time.sleep(5) # Give parent time to exit
        print(f"Child ({os.getpid()}): I am an orphan. My new parent is {os.getppid()} (usually init/systemd PID 1).")
        print("Child: I will now exit.")
        os._exit(0)
    else:
        # Parent process
        print(f"Parent ({os.getpid()}): I am exiting now, leaving my child ({pid}) as an orphan.")
        time.sleep(1) # Short sleep to ensure child's first print happens
        os._exit(0)


## Task 4: Inspecting Process Info from /proc
def task4_inspect_proc(pid):
    """
    Reads and prints process information from the /proc filesystem.
    """
    print(f"--- Running Task 4: Inspecting /proc for PID {pid} ---")
    proc_dir = f"/proc/{pid}"

    if not os.path.isdir(proc_dir):
        print(f"Error: Process with PID {pid} does not exist.")
        return

    try:
        # 1. Read /proc/[pid]/status
        print(f"\n--- Reading {proc_dir}/status ---")
        with open(f"{proc_dir}/status", 'r') as f:
            for line in f:
                if line.startswith(("Name:", "State:", "Pid:", "PPid:", "VmSize:")):
                    print(line.strip())

        # 2. Read /proc/[pid]/exe (executable path)
        print(f"\n--- Reading {proc_dir}/exe ---")
        exe_path = os.readlink(f"{proc_dir}/exe")
        print(f"Executable Path: {exe_path}")

        # 3. List /proc/[pid]/fd (open file descriptors)
        print(f"\n--- Listing {proc_dir}/fd ---")
        fd_dir = f"{proc_dir}/fd"
        fds = os.listdir(fd_dir)
        print(f"Open File Descriptors ({len(fds)}):")
        for fd in fds:
            try:
                link_path = os.readlink(f"{fd_dir}/{fd}")
                print(f"  FD {fd}: -> {link_path}")
            except Exception as e:
                print(f"  FD {fd}: Error reading link - {e}")
                
    except Exception as e:
        print(f"An error occurred: {e}")
    
    print("\n")


## Task 5: Process Prioritization
def task5_process_prioritization():
    """
    Demonstrates process scheduling impact using nice values.
    """
    print("--- Running Task 5: Process Prioritization with nice() ---")
    nice_values = [19, 10, 0] # Lower nice value means higher priority. 19 is lowest, 0 is default.
    print(f"Creating 3 CPU-bound child processes with nice values: {nice_values}")
    print("The child with the lowest nice value (highest priority) should finish first.")

    for nice_val in nice_values:
        pid = os.fork()
        if pid == 0:
            # Child process
            # Set the nice value. os.nice() returns the new nice value.
            os.nice(nice_val)
            
            start_time = time.time()
            print(f"Child (PID {os.getpid()}, Nice {os.nice(0)}): Starting CPU-bound task.")
            cpu_bound_task()
            end_time = time.time()

            print(f"--> Child (PID {os.getpid()}, Nice {os.nice(0)}): FINISHED in {end_time - start_time:.2f}s.")
            os._exit(0)
    
    # Parent waits for all children
    for _ in nice_values:
        os.wait()

    print("\nParent: All prioritized children have completed.\n")


def main():
    parser = argparse.ArgumentParser(description="ENCS351 - OS Process Management Lab")
    parser.add_argument('--task1', type=int, metavar='N', help='Run Task 1 with N child processes.')
    parser.add_argument('--task2', nargs='+', metavar='CMD', help='Run Task 2 with specified commands.')
    parser.add_argument('--zombie', action='store_true', help='Run Task 3 to simulate a zombie process.')
    parser.add_argument('--orphan', action='store_true', help='Run Task 3 to simulate an orphan process.')
    parser.add_argument('--inspect', type=int, metavar='PID', help='Run Task 4 to inspect the given PID.')
    parser.add_argument('--priority', action='store_true', help='Run Task 5 for process prioritization.')

    args = parser.parse_args()

    if args.task1:
        task1_create_processes(args.task1)
    elif args.task2:
        task2_execute_commands(args.task2)
    elif args.zombie:
        task3_zombie_process()
    elif args.orphan:
        task3_orphan_process()
    elif args.inspect:
        task4_inspect_proc(args.inspect)
    elif args.priority:
        task5_process_prioritization()
    else:
        print("Please specify a task to run. Use --help for options.")

if __name__ == "__main__":
    main()
