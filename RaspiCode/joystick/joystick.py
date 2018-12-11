from joystick.controller import Controller, ControllerError

class Joystick(Controller):

    xval = 0
    yval = 0

    def store_received(self, recvd_list):
        try:
            x = int(recvd_list[0])
            y = int(recvd_list[1])
        except (ValueError, IndexError) as e:
            print(str(e))
            return None
        else:
            if x<=100 and x>=-100 and y<=100 and y>=-100: # have a virtual function instead
                self.xval = x
                self.yval = y
                return 'ACK'
            else:
                return 'ERR:RANGE'
