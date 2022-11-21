import sys
import time

sleep_time = float(sys.argv[1]) if len(sys.argv) > 1 else float(5)

print(f"Sleeping {sleep_time}s\n")
start = time.time()
while 1:
    time.sleep(1)
    print("Slept:", round(time.time() - start), "s", end="\r")
    if time.time() - start > sleep_time:
        break

print(f"\nDone Sleeping")
