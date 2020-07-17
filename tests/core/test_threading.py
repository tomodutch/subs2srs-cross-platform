from subs2srs.core.threading import do_worker_pool
import queue
import time

def setup(item):
    pass


def producer(q: queue.Queue):
    for i in range(10):
        q.put(i)
        yield i

if __name__ == "__main__":
    for i in do_worker_pool(10, setup, producer):
        print(i)
        
    for i in do_worker_pool(10, setup, producer):
        print(i)
    