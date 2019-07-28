from autonomous.auto_mode import Goal, GoalError
from autonomous.cv_engine import OpenCVHaar, CVEngineError
from threading import Thread
class Stream(Goal):
    '''Stream result of object detection.'''
    
    def __init__(self):
        Goal.__init__(self)
        self.register_name("Stream")
        self.cv_engine = OpenCVHaar()
        
    def run(self):
        try:
            self.cv_engine.activate()
        except CVEngineError as e:
            raise GoalError(str(e))
        thread_obj_detect = Thread(target=self.obj_detect, args=[])
        thread_obj_detect.start()
        import time
        time.sleep(1)           # allow time to acquire camera
        if self.cv_engine.is_active():
            self.cv_engine.begin_stream(self.cv_engine)
        
    def obj_detect(self):
        while self.cv_engine.is_active():
            self.cv_engine.find_obj()
            
    def cleanup(self):
        if self.cv_engine.is_active():
            self.cv_engine.end_stream()    
            self.cv_engine.deactivate()
