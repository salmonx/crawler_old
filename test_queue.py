from multiprocessing import Process, Queue
import time

def do(q):
    time.sleep(1)
    while q.qsize() > 0:
        print q.get()

def put(q):
    import time
    i = 0
    while i < 10:
        #time.sleep(1)
        q.put_nowait(i)
        i += 1
    

def main():
    q = Queue()
    p1 = Process(target=put, args = (q,))
    p1.start()

    do(q)
    p1.join()


if __name__ == '__main__': main()
