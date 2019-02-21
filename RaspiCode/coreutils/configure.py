import xml.etree.ElementTree as ET

class ConfigurationError(Exception):
    '''Exception class for configuration.'''
    pass

class Configuration:
    def __init__(self, name="settings.xml"):
        self.tree = ET.parse(name)
        self.root = self.tree.getroot()

    def _getsubelemvalue(self,elem, pred, match):
        for things in elem:
            for subthing in things:
                try:
                    if subthing.attrib[pred] == match:
                        return subthing
                except KeyError as e:
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

    def get_digital1_pin(self, motor_group, motor_name):
        req = ["{Motors}[name]"+motor_group+".{Motor}[name]"
               +motor_name]
        motor = self.provide_settings(req)
        pin = self._getsubelemvalue(motor[0], "TYPE", "Digital1")
        try:
            return int(pin.text)
        except ValueError as e:
             raise ConfigurationError("Bad value in settings file for digital pin of motor '"+motor_name+"'. Error: "+str(e))

    def get_digital2_pin(self, motor_group, motor_name):
        req = ["{Motors}[name]"+motor_group+".{Motor}[name]"
               +motor_name]
        motor = self.provide_settings(req)
        pin = self._getsubelemvalue(motor[0], "TYPE", "Digital2")
        try:
            return int(pin.text)
        except ValueError as e:
             raise ConfigurationError("Bad value in settings file for digital pin of motor '"+motor_name+"'. Error: "+str(e))
         
class OverallConfiguration(Configuration):
    def __init__(self, name="settings.xml"):
        Configuration.__init__(self, name)

    def operation_mode(self):
        val = self.top_level_element_value("MODE")
        if val is None:
            raise ConfigurationError("No settings found for operation mode.")
        return val

    def pwm_hardware_setting(self):
        val = self.top_level_element_value("PWMHARDWARE")
        if val is None:
            raise ConfigurationError("No settings found for pwm hardware.")
        return val

global_config = OverallConfiguration()
