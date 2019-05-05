from autonomous.auto_mode import Goal

class DummyGoal(Goal):
    def __init__(self):
        self.register_name("Dummy goal")
        
    def initialise(self):
        pass

    def deinitialise(self):
        pass
    
