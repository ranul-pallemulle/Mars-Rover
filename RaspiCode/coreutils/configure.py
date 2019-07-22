import xml.etree.ElementTree as ET
from threading import Lock

# global configuration managers
overall_config = None
motor_config = None
cam_config = None
auto_config = None

class ConfigurationError(Exception):
    '''Exception class for configuration.'''
    pass

class Configuration:
    def __init__(self, name="settings.xml"):
        try:
            self.tree = ET.parse(name)
        except FileNotFoundError as e:
            raise ConfigurationError(str(e))
        self.root = self.tree.getroot()
        self.tree_lock = Lock()

    @staticmethod
    def ready():
        global overall_config
        global motor_config
        global cam_config
        global auto_config
        if overall_config is None \
           or motor_config is None \
           or cam_config is None \
           or auto_config is None:
            return False
        return True

    @staticmethod
    def settings_file(name="settings.xml"):
        global overall_config
        global motor_config
        global cam_config
        global auto_config
        overall_config = OverallConfiguration(name)
        motor_config = MotorConfiguration(name)
        cam_config = CameraConfiguration(name)
        auto_config = AutonomousConfiguration(name)

    def _getsubelemvalue(self,elem, pred, match):
        for things in elem:
            for subthing in things:
                try:
                    if subthing.attrib[pred] == match:
                        return subthing
                except KeyError:
                    return None
                
    def _getsubelemvaluebyname(self, elem, subname, pred, match):
        for things in elem:
            for subthing in things:
                if subthing.tag == subname:
                    try:
                        if subthing.attrib[pred] == match:
                            return subthing
                    except KeyError:
                        return None


    def _make_searchstr_list(self, req_list):
        searchstr_list = []
        for elemstr in req_list:
            searchstr = "."
            elem_list = elemstr.split('.')
            for elem in elem_list:
                idx1 = elem.find('{')
                idx2 = elem.find('}')
                tagname = elem[idx1+1:idx2]
                searchstr = searchstr + "/" + tagname.upper()
                idx3 = elem.find('[')
                idx4 = elem.find(']')
                if (idx3 == -1) or (idx4 == -1):
                    continue
                attrtype = elem[idx3+1:idx4].upper()
                attrname = elem[idx4+1:]
                searchstr = searchstr + "[@"+attrtype+"='"+attrname+"']"
            searchstr_list.append(searchstr)
        return searchstr_list
    
    def provide_settings(self, req_list):
        if not req_list:
            return None
        searchstr_list = self._make_searchstr_list(req_list)
        res_list = []
        with self.tree_lock:
            for searchstr in searchstr_list:
                res = self.root.findall(searchstr)
                res_list.append(res)
        if not res_list[0]:
            return None
        return res_list

    def top_level_element_value(self, name):
        elem_list = self.provide_settings(["{"+name+"}"])
        if not elem_list:
            return None
        return (elem_list[0][0].text.strip())

class MotorConfiguration(Configuration):
    def __init__(self, name="settings.xml"):
        Configuration.__init__(self, name)
    
    def get_pwm_pin(self, motor_group ,motor_name):
        req = ["{Motors}[name]"+motor_group+".{Motor}[name]"
               +motor_name]
        motor = self.provide_settings(req)
        # pin = self._getsubelemvalue(motor[0],"TYPE","PWM")
        pin = self._getsubelemvaluebyname(motor[0], "PIN", "TYPE", "PWM")
        try:
            return int(pin.text)
        except ValueError as e:
            raise ConfigurationError("Bad value in settings file for pwm pin of motor '"+motor_name+"'. Error: "+str(e))

    def get_digital_pin(self, motor_group, motor_name):
        req = ["{Motors}[name]"+motor_group+".{Motor}[name]"
               +motor_name]
        motor = self.provide_settings(req)
        # pin = self._getsubelemvalue(motor[0], "TYPE", "Digital")
        pin = self._getsubelemvaluebyname(motor[0], "PIN", "TYPE", "Digital")
        try:
            return int(pin.text)
        except ValueError as e:
             raise ConfigurationError("Bad value in settings file for digital pin of motor '"+motor_name+"'. Error: "+str(e))

    def get_pin(self, motor_group, motor_name):
        req = ["{Motors}[name]"+motor_group+".{Motor}[name]"
               +motor_name]
        motor = self.provide_settings(req)
        # pin = self._getsubelemvalue(motor[0], "TYPE", "Other")
        pin = self._getsubelemvaluebyname(motor[0], "PIN", "TYPE", "Other")
        try:
            return int(pin.text)
        except ValueError as e:
            raise ConfigurationError("Bad value in settings file for pin of motor '"+motor_name+"'. Error: "+str(e))        

    def get_limit(self, motor_group, motor_name, lim_name):
        req = ["{Motors}[name]"+motor_group+".{Motor}[name]"+motor_name]
        motor = self.provide_settings(req)
        lim_name = str.capitalize(lim_name)
        lim = self._getsubelemvaluebyname(motor[0], "LIMIT" ,"NAME", lim_name)
        try:
            return float(lim.text)
        except ValueError as e:
            raise ConfigurationError("Bad value in settings file for limit '{}'\
 of motor '{}'. Error: {}".format(lim_name,motor_name,str(e)))
        except AttributeError as e:
            raise ConfigurationError("Search for limit '{}' on motor '{}' \
of group '{}' returned no result".format(lim_name,motor_name,motor_group))


class CameraConfiguration(Configuration):
    def __init__(self, name="settings.xml"):
        Configuration.__init__(self,name)

    def _generic_integer_setting(self, name):
        req = ["{Camera}.{"+name+"}"]
        elem_list = self.provide_settings(req)
        if not elem_list:
            return None
        val = int(elem_list[0][0].text.strip())
        return val

    def _generic_string_setting(self, name):
        req = ["{Camera}.{"+name+"}"]
        elem_list = self.provide_settings(req)
        if not elem_list:
            return None
        val = elem_list[0][0].text.strip()
        return val

    def device(self):
        dev = self._generic_string_setting('device')
        if dev == 'rpicamsrc' or dev == 'v4l2src' or dev == 'avfvideosrc' or \
           dev == 'autovideosrc':
            return dev
        raise ConfigurationError("Error in camera settings: invalid device specified, can only be 'rpicamsrc','v4l2src' or 'avfvideosrc'.")
           

    def capture_framerate(self):
        return self._generic_integer_setting('capture_framerate')

    def capture_frame_width(self):
        return self._generic_integer_setting('capture_frame_width')

    def capture_frame_height(self):
        return self._generic_integer_setting('capture_frame_height')

    def stream_port(self):
        return self._generic_integer_setting('stream_port')

    def stream_framerate(self):
        return self._generic_integer_setting('stream_framerate')
    def stream_frame_width(self):
        return self._generic_integer_setting('stream_frame_width')

    def stream_frame_height(self):
        return self._generic_integer_setting('stream_frame_height')

class AutonomousConfiguration(Configuration):
    def __init__(self, name="settings.xml"):
        Configuration.__init__(self,name)
        
    def _generic_integer_setting(self,name):
        req = ["{Autonomous}.{"+name+"}"]
        elem_list = self.provide_settings(req)
        if not elem_list:
            return None
        val = int(elem_list[0][0].text.strip())
        return val
    
    def _generic_string_setting(self,name):
        req = ["{Autonomous}.{"+name+"}"]
        elem_list = self.provide_settings(req)
        if not elem_list:
            return None
        val = elem_list[0][0].text.strip()
        return val

    def cv_engine(self):
        return self._generic_string_setting('cvengine')
    
    def capture_framerate(self):
        return self._generic_integer_setting('capture_framerate')

    def capture_frame_width(self):
        return self._generic_integer_setting('capture_frame_width')

    def capture_frame_height(self):
        return self._generic_integer_setting('capture_frame_height')

    def stream_port(self):
        return self._generic_integer_setting('stream_port')

    def stream_framerate(self):
        return self._generic_integer_setting('stream_framerate')
    
    def stream_frame_width(self):
        return self._generic_integer_setting('stream_frame_width')

    def stream_frame_height(self):
        return self._generic_integer_setting('stream_frame_height')

    def ultrasound_trigger_pin(self):
        return self._generic_integer_setting('ultrasound_trigger_pin')

    def ultrasound_echo_pin(self):
        return self._generic_integer_setting('ultrasound_echo_pin')
    
    def ultrasound_power_pin(self):
        return self._generic_integer_setting('ultrasound_power_pin')
    
    def ultrasound_ground_pin(self):
        return self._generic_integer_setting('ultrasound_ground_pin')

class OverallConfiguration(Configuration):
    def __init__(self, name="settings.xml"):
        Configuration.__init__(self, name)
        self.connected_ip = '0.0.0.0' # ip address to which remote has connected
        self.running_as_unit = False # if start_rover was called with --as-unit

    def opmodes_directories(self):
        dir_list_str = self.top_level_element_value("OPMODES_DIRECTORIES")
        if dir_list_str is None:
            raise ConfigurationError("No settings found for operational mode directories.")
        dir_list_str = dir_list_str.replace('\n','').replace(' ','')
        dir_list = dir_list_str.split(',')
        if '' in dir_list and len(dir_list) > 1:
            raise ConfigurationError("Error in operational mode settings: probably extra comma in list.")
        return dir_list

    def resources_directories(self):
        dir_list_str = self.top_level_element_value("RESOURCES_DIRECTORIES")
        if dir_list_str is None:
            raise ConfigurationError("No settings found for resources directories.")
        dir_list_str = dir_list_str.replace('\n','').replace(' ','')
        dir_list = dir_list_str.split(',')
        if '' in dir_list and len(dir_list) > 1:
            raise ConfigurationError("Error in resource settings: probably extra comma in list.")
        return dir_list

    def diagnostics_enabled(self):
        req = ["{Diagnostics}.{state}"]
        elem_list = self.provide_settings(req)
        if not elem_list:
            raise ConfigurationError("No settings found for Diagnostics state.")
        en_str = elem_list[0][0].text.strip()
        if en_str == "Enabled":
            return True
        elif en_str == "Disabled":
            return False
        raise ConfigurationError("Error in Diagnostics settings: invalid state, can only be 'Enabled' or 'Disabled'.")

    def diagnostics_port(self):
        req = ["{Diagnostics}.{port}"]
        elem_list = self.provide_settings(req)
        if not elem_list:
            raise ConfigurationError("No settings found for Diagnostics.")
        port_str = elem_list[0][0].text.strip()
        try:
            port = int(port_str)
        except TypeError:
            raise ConfigurationError("Error in Diagnostics settings: port number setting must be an integer.")
        if port < 1000:
            raise ConfigurationError("Error in Diagnostics settings: port number needs to be larger than 1000 to prevent conflict with reserved ports.")
        return port
    
    def set_unitname(self, unitname):
        self.unitname = unitname
        
    def main_hostname(self):
        hostname = self.top_level_element_value("MAIN_HOSTNAME")
        if hostname is None:
            raise ConfigurationError("No settings found for main unit hostname.")
        hostname = hostname.replace(' ','')
        return hostname
        
    def set_ip(self, ip):
        self.connected_ip = ip
        
    def get_connected_ip(self):
        return self.connected_ip

