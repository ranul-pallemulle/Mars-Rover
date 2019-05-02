from resources.resource import Resource, Policy
class DummyResource(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.policy = Policy.SHARED
        self.register_name('Dummy')
        
