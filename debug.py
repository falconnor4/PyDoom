import time

def profile(fname, func):
    t0 = time.time()

    result = func()

    delta = time.time() - t0
    print(f"{fname} took {delta:.2f} seconds")

    return result