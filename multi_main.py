import multiprocessing as mp


def worker(num):
    print(f"Worker {num}")


if __name__ == "__main__":
    jobs = []
    for i in range(5):
        p = mp.Process(target=worker, args=(i,))
        jobs.append(p)
        p.start()
