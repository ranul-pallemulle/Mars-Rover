import coreutils.configure as cfg
from coreutils.diagnostics import Diagnostics as dg
from autonomous.auto_mode import Goal, GoalError
from autonomous.cv_engine import CVEngine, CVEngineError
from interfaces.controllers import IK3RArmController, PIDDriveController
from threading import Thread
import time

class Samples2(Goal):
    '''Autonomous mode goal for picking up samples.'''

    def __init__(self):
        Goal.__init__(self)
        self.register_name("Samples2")
        engine = cfg.auto_config.cv_engine()
        self.cv_engine = CVEngine.get_engine(engine) # object detection
        self.drive_controller = PIDDriveController()
        self.arm_controller = IK3RArmController(l1 = 6.5, l2 = 6.5, l3 = 11.5,
                                                thet1 = 83, thet2 = -56,
                                                thet3 = -111, gripper = 0)
        ground_height = 13      # distance to ground from base servo
        self.arm_controller.set_reference(0,-ground_height)

    def run(self):
        self.arm_controller.activate()
        self.drive_controller.activate()
        try:
            self.cv_engine.activate()
        except CVEngineError as e:
            raise GoalError('Could not activate CVEngine: '+str(e))
        thread = Thread(target=self.sequence, args=[])
        thread.start()

    def cleanup(self):
        try:
            self.cv_engine.deactivate()
        except CVEngineError as e:
            raise GoalError('Could not deactivate CVEngine: '+str(e))
        self.drive_controller.deactivate()
        self.arm_controller.deactivate()

    def sequence(self):
        '''Operations sequence for picking samples.'''
        while self.cv_engine.is_active():
            self.scout_area()   # look around, try to locate a sample
            self.drive_to_sample() # drive up to the sample
            self.pick_sample()     # pick it up

    def scout_area(self):
        dg.print("Scouting area...")
        self.drive_controller._pid(0,0)
        time.sleep(2)
        dg.print("Located sample.")

    def drive_to_sample(self):
        dg.print("Driving to sample...")
        self.drive_controller._pid(0.5,0.5)
        time.sleep(2)        
        dg.print("Arrived at sample location.")

    def pick_sample(self):
        dg.print("Collecting sample...")
        self.drive_controller._pid(1.0,1.0)
        time.sleep(2)
        dg.print("Collected.")

        
