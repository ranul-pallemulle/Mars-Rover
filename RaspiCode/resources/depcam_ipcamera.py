import ipcamera as icam
import coreutils.configure as cfg
from coreutils.diagnostics import Diagnostics as dg
from resources.resource import Resource, ResourceRawError, Policy

class IPCamera(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.policy = Policy.SHARED
        self.register_name("IPCamera")
        self.host = None
        self.port = 5520

    def shared_init(self):
        self.host = cfg.overall_config.get_connected_ip()
        icam.initialise(self.host, self.port)
        icam.start_stream()
        dg.print("IPCamera streaming on ip address {} and port {}".format(self.host, self.port))
        
        
    def shared_deinit(self):
        icam.cleanup()
