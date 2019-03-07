from interfaces.cam_user import CameraUser, CameraUserError

class DefaultStream(CameraUser):

    def __init__(self):
        CameraUser.__init__(self)

    def is_running(self):
        return self.streaming

    def start(self):
        print("Starting simple camera stream mode...")
        self.acquire_camera()
        if not self.have_camera():
            self.stop()
            return
        self.begin_stream()
        print("Simple camera stream started.")

    def stop(self):
        if self.is_running():
            print("Stopping simple camera stream mode...")
            self.end_stream()
            if self.have_camera():
                self.release_camera()
            print("Stopped simple camera stream mode.")
