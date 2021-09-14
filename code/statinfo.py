import os
import time
import threading
from threading import Timer

def checksize(path_to_file):
    #return os.path.getsize(file)
    return os.path.getmtime(path_to_file)
    #statinfo = os.stat(file)
    #return statinfo.st_size


class TimerClass(threading.Thread):
    def __init__(self, file):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.counter = 0
        self.mtimes = []
        self.file = file

    def run(self):
        s = checksize(self.file)
        self.mtimes.append(s)
        print(self.mtimes)
        self.counter += 1

        while not self.event.is_set():
            self.event.wait(1)
            time.sleep(3)
            if len(self.mtimes) > 1:
                if self.mtimes[-1] == self.mtimes[-2]:
                    # stop interval
                    print("the file has been written")
                    #file_complete = True
                    #print(file_complete)
                    self.stop()
                else:
                    print("the file is being written")

    def stop(self):
        self.event.set()




counter = 0
size = []

def task_manager(path_to_file):
    global counter, size

    #print(filename)
    #do stuff
    s = checksize(path_to_file)
    size.append(s)
    print(size)
    counter += 1

    print("starting timer")
    t = Timer(5, task_manager, [path_to_file])
    t.start()

    print("comparing size")
    if len(size) > 1:
        if size[-1] == size[-2]:
            # stop interval
            print("the file has been written")
            t.cancel()
        else:
            print("the file is being written")



file = "package.omt"
#task_manager(filename, counter, size)

def f():
    for i in range(1, 10):
         print(i)

# thread = threading.Thread(target=task_manager(file))
# thread.start()

# print("This may print while the thread is running.")
# thread.join()
# print("This will always print after the thread has finished.")


# st = os.stat(file)
# print(st)