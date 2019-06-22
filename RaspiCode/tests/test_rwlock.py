import unittest
from unittest.mock import patch, Mock
from threading import Thread
from coreutils.rwlock import RWLock
import time

global_count = 0
sleep_time = 0.01
iteration_count = 20

def reader(lock, name):
    while global_count < iteration_count:
        lock.acquire_read()
        print("acquired read lock on "+name)
        time.sleep(sleep_time)
        lock.release()
        print("released read lock on "+name)

def writer(lock):
    global global_count
    while global_count < iteration_count:
        lock.acquire_write()
        print("acquired write lock")
        time.sleep(sleep_time)
        global_count += 1
        lock.release()
        print("released write lock")
        

class TestRWLock(unittest.TestCase):

    def test_time(self):
        lock = RWLock()
        thread1 = Thread(target=reader, args=[lock, 'thread1'])
        thread2 = Thread(target=reader, args=[lock, 'thread2'])
        thread3 = Thread(target=writer, args=[lock])

        t1 = time.time()
        thread1.start()
        thread2.start()
        thread3.start()
        thread1.join()
        thread2.join()
        thread3.join()
        t2 = time.time()

        print("Elapsed time = {}s".format(t2-t1))
