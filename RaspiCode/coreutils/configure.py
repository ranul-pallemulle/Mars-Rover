import xml.etree.ElementTree as ET

class ConfigurationError(Exception):
    '''Exception class for configuration.'''
    pass

class Configuration:
    def __init__(self):
        self.tree = ET.parse("settings.xml")
        self.root = self.tree.getroot()

    def _getsubelemvalue(self,elem, pred, match):
        for things in elem:
            for subthing in things:
                if subthing.attrib[pred] == match:
                    return subthing

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
                attrname = elem[idx4+1:].capitalize()
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
        return res_list

    def top_level_element_value(self, name):
        elem_list = self.provide_settings(["{"+name+"}"])
        return (elem_list[0][0].text.strip())

class MotorConfiguration(Configuration):
    def __init__(self):
        Configuration.__init__(self)
    
    def get_pwm_pin(self, motor_group ,motor_name):
        req = ["{Motors}[name]"+motor_group+".{Motor}[name]"
               +motor_name]
        motor = self.provide_settings(req)
        pin = self._getsubelemvalue(motor[0],"TYPE","PWM")
        return int(pin.text)

    def get_digital_pin(self, motor_group, motor_name):
        req = ["{Motors}[name]"+motor_group+".{Motor}[name]"
               +motor_name]
        motor = self.provide_settings(req)
        pin = self._getsubelemvalue(motor[0], "TYPE", "Digital")
        return int(pin.text)

class OverallConfiguration(Configuration):
    def __init__(self):
        Configuration.__init__(self)

    def operation_mode(self):
        return self.top_level_element_value("MODE")

    def pwm_hardware_setting(self):
        return self.top_level_element_value("PWMHARDWARE")

global_config = OverallConfiguration()
