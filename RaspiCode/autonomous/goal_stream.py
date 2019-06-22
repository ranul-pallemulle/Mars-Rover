from autonomous.auto_mode import Goal, GoalError
from autonomous.cv_engine import OpenCVHaar
from threading import Thread
class Stream(Goal):
    '''Stream result of object detection.'''
    
    def __init__(self):
        Goal.__init__(self)
        self.register_name("Stream")
        self.cv_engine = OpenCVHaar()
        
    def run(self):
        thread_obj_detect = Thread(target=self.obj_detect, args=[])
        thread_obj_detect.start()
        import time
        time.sleep(1)           # allow time to acquire camera
        self.cv_engine.begin_stream(self.cv_engine)
        
    def obj_detect(self):
        self.cv_engine.activate()
        while self.cv_engine.is_active():
            self.cv_engine.find_obj()
            
    def cleanup(self):
        self.cv_engine.end_stream()        
        self.cv_engine.deactivate()
