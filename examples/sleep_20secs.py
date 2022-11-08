import time

print(f"Sleeping 20s\n")
start = time.time()
while 1:
    time.sleep(1)
    print("Slept:", round(time.time() - start), "s", end="\r")
    if time.time() - start > 20:
        break

print(f"\nDone Sleeping")
