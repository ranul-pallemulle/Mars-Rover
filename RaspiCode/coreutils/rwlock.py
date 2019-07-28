from threading import Condition, Lock
import time

class RWLock:
    "A read-write lock - Multiple readers can simultaneously hold the lock but if a writer is present, only the writer can hold the lock while the readers wait. There can only be a single writer."

    def __init__(self):
        self.lock = Lock()        
        self.read_cond = Condition(self.lock)
        self.write_cond = Condition(self.lock)
        self.waiting_writer = False # writer waiting to obtain lock
        self.reader_count = 0        # number of readers that have acquired the lock

    def acquire_read(self):
        with self.lock:
            # wait to be notified that writer is done writing, if writer is already writing or is waiting to write.
            while self.reader_count < 0 or self.waiting_writer:
                self.read_cond.wait()
            self.reader_count += 1

    def acquire_write(self):
        with self.lock:
            while self.reader_count != 0:
                self.waiting_writer = True
                self.write_cond.wait()
            self.reader_count = -1
            self.waiting_writer = False

    def release(self):
        with self.lock:
            if self.reader_count == -1:
                self.reader_count = 0
            else:
                self.reader_count -= 1
            if self.waiting_writer and self.reader_count == 0:
                self.write_cond.notify()
            elif not self.waiting_writer:
                self.read_cond.notifyAll()
