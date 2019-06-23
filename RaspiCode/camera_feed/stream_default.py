from interfaces.cam_user import CameraUser, CameraUserError
from interfaces.opmode import OpMode, OpModeError
from coreutils.diagnostics import Diagnostics as dg

class DefaultStream(CameraUser, OpMode):

    def __init__(self):
        CameraUser.__init__(self)
        OpMode.__init__(self)

        self.register_name("Stream")

    def start(self, args):
        try:
            self.acquire_camera()
        except CameraUserError as e:
            raise OpModeError(str(e))
        if not self.have_camera():
            self.stop(None)
            raise OpModeError(str(e))
        self.begin_stream()

    def stop(self, args):
        self.end_stream()
        if self.have_camera():
            self.release_camera()

    def submode_command(self, args):
        dg.print('Stream mode does not take submode commands.')

    def on_resources_unexp_lost(self):
        self.stop(None)
        
