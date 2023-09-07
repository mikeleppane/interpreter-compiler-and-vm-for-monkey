import time


def fibonacci(n: int) -> int:
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


if __name__ == "__main__":
    t1_start = time.perf_counter()

    fibonacci(35)

    t1_stop = time.perf_counter()

    print(
        f"Fibonacci(35) in Python3.11: execution time in seconds: {t1_stop - t1_start}",
    )
