from autonomous.auto_mode import Goal, GoalError
from coreutils.diagnostics import Diagnostics as dg

class DummyGoal(Goal):
    def __init__(self):
        Goal.__init__(self)
        self.register_name("Dummy")
        
    def run(self):
        # raise GoalError("Dummy goal can't run")
        dg.print("Dummy goal started running.")

    def cleanup(self):
        dg.print("Dummy goal doing cleanup.")
    
class DummyGoal2(Goal):
    def __init__(self):
        Goal.__init__(self)
        self.register_name("Dummy2")

    def run(self):
        dg.print("Dummy goal 2 started running.")

    def cleanup(self):
        dg.print("Dummy goal 2 doing cleanup.")


