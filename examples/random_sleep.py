import random
import time

t = random.random() * 10
print(f"Sleeping {t:.2f}s")
time.sleep(t)
print(f"Done Sleeping")
time.sleep(1)
