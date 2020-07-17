import queue
import threading


class QueueThread:
    def __init__(self, run):
        self._run = run
        self._running = True

    def terminate(self):
        self._running = False

    def run(self, q: queue.Queue):
        # prevent queue.join to deadlock
        while self._running or q.qsize() > 0:
            item = q.get()
            self._run(item)
            q.task_done()


def do_worker_pool(max_size, do_work, producer):
    q = queue.Queue(max_size)
    max_workers = max_size
    threads: list[QueueThread] = []

    def do(item):
        print(item)

    def start_thread_pool():
        for i in range(max_size):
            # turn-on the worker thread
            queue_thread = QueueThread(do_work)
            t = threading.Thread(target=queue_thread.run, args=(q,), daemon=True)
            t.start()
            threads.append(queue_thread)

    def shutdown_thread_pool():
        for thread in threads:
            thread.terminate()

    start_thread_pool()
    for i in producer(q):
        yield i

    q.join()
    shutdown_thread_pool()
