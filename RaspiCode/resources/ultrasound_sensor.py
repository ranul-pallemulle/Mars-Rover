import RPi.GPIO as GPIO
import time
import coreutils.configure as cfg
from coreutils.rwlock import RWLock
from resources.resource import Resource, ResourceRawError, Policy
from threading import Thread


class UltrasoundSensor(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.policy = Policy.SHARED
        self.register_name("Ultrasound")
        try:
            self.trigger_pin = cfg.auto_config.ultrasound_trigger_pin()
            self.echo_pin = cfg.auto_config.ultrasound_echo_pin()
        except cfg.ConfigurationError as e:
            raise ResourceRawError(str(e))
        self.active = False
        self.distance = -1
        self.lock = RWLock()

    def shared_init(self):
        self.start_capture()

    def shared_deinit(self):
        self.stop_capture()
        
    def start_capture(self):
        if not self.active:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.trigger_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            GPIO.output(self.trigger_pin, GPIO.LOW)
            time.sleep(1)
            self.active = True
            Thread(target=self._capture, args=()).start()

    def stop_capture(self):
        if self.active:
            self.active = False
        time.sleep(1)
        GPIO.output(self.trigger_pin, GPIO.LOW)
        # GPIO.cleanup()

    def read(self):
        self.lock.acquire_read()
        distance = self.distance
        self.lock.release()
        return distance

    def _send_pulse(self):
        GPIO.output(self.trigger_pin, GPIO.HIGH)
        time.sleep(0.00001)     # 0.00001
        GPIO.output(self.trigger_pin, GPIO.LOW)

    def _capture(self):
        while self.active:
            start_fresh = False
            timeout_count = 0
            self._send_pulse()

            while self.active and GPIO.input(self.echo_pin) == 0:
                timeout_count += 1
                if timeout_count == 200:
                    start_fresh = True
                    break
                pulse_start = time.time()


            while self.active and GPIO.input(self.echo_pin) == 1:
                pulse_end = time.time()

            if start_fresh:
                time.sleep(0.2)
                continue

            if not self.active:
                break

            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration*17150
            distance = round(distance,2)
            self.lock.acquire_write()
            self.distance = distance
            self.lock.release()

