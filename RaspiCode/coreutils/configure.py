import xml.etree.ElementTree as ET
from threading import Lock

# global configuration managers
overall_config = None
motor_config = None

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
        if overall_config is None \
           or motor_config is None:
            return False
        return True

    @staticmethod
    def settings_file(name="settings.xml"):
        global overall_config
        global motor_config
        overall_config = OverallConfiguration(name)
        motor_config = MotorConfiguration(name)

    def _getsubelemvalue(self,elem, pred, match):
        for things in elem:
            for subthing in things:
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
        pin = self._getsubelemvalue(motor[0],"TYPE","PWM")
        try:
            return int(pin.text)
        except ValueError as e:
            raise ConfigurationError("Bad value in settings file for pwm pin of motor '"+motor_name+"'. Error: "+str(e))

    def get_digital_pin(self, motor_group, motor_name):
        req = ["{Motors}[name]"+motor_group+".{Motor}[name]"
               +motor_name]
        motor = self.provide_settings(req)
        pin = self._getsubelemvalue(motor[0], "TYPE", "Digital")
        try:
            return int(pin.text)
        except ValueError as e:
             raise ConfigurationError("Bad value in settings file for digital pin of motor '"+motor_name+"'. Error: "+str(e))

    def get_pin(self, motor_group, motor_name):
        req = ["{Motors}[name]"+motor_group+".{Motor}[name]"
               +motor_name]
        motor = self.provide_settings(req)
        pin = self._getsubelemvalue(motor[0], "TYPE", "Other")
        try:
            return int(pin.text)
        except ValueError as e:
            raise ConfigurationError("Bad value in settings file for pin of motor '"+motor_name+"'. Error: "+str(e))

class OverallConfiguration(Configuration):
    def __init__(self, name="settings.xml"):
        Configuration.__init__(self, name)

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
        

