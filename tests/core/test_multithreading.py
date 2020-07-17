from multiprocessing import Process, Lock, Pool
import time
import datetime
import threading, queue

def f(i):
    print(i)
    time.sleep(2)
    return i

q = queue.Queue(maxsize=3)
def worker():
    while True:
        item = q.get()
        print(f'Working on {item}')
        time.sleep(1)
        print(f'Finished {item}')
        q.task_done()

def test_something():
    print("test")
    lock = Lock()
    for i in range(100):
        Process(target=f, args=(lock, i)).start()

def test_pool():
    def do():
        with Pool(processes=1) as pool:
            def callback(a):
                print("done", a)
            
            processes = []

            for i in range(5):
                start = datetime.datetime.now()
                # print("{} start {}".format(start.isoformat(), i))
                result = pool.apply_async(f, (i,), callback=callback)
                processes.append(result)
            
            for p in processes:
                p.wait()

    print(do())

def test_queue():
    # turn-on the worker thread
    threading.Thread(target=worker, daemon=True).start()
    # turn-on the worker thread
    threading.Thread(target=worker, daemon=True).start()
    # turn-on the worker thread
    threading.Thread(target=worker, daemon=True).start()
    def do():
        # send thirty task requests to the worker
        for item in range(30):
            q.put(item)
            yield item
        print('All task requests sent\n', end='')

        # block until all tasks are done
        q.join()
        print('All work completed')

    
    for i in do():
        print("Working on {}".format(i))