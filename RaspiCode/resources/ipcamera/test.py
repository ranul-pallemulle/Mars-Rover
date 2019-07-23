import ipcamera as cam
from threading import Thread
import time

if __name__=='__main__':
    print("Initialise...")
    cam.initialise("192.168.2.44",5560)
    print("Start stream...")
    cam.start_stream()
    # Thread(target=cam.start_stream, args=[]).start()
    time.sleep(15)
    print("Stop stream...")
    cam.stop_stream()
    time.sleep(15)
    print("Start stream...")
    cam.start_stream()
    # Thread(target=cam.start_stream, args=[]).start()
    time.sleep(15)
    print("Cleanup...")
    cam.cleanup()
