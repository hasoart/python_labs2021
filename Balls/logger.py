import json
import time


class Logger:
    def __init__(self, file='logs.json'):
        """
        Logger(file='logs.json')

        Creates logger which dumps in the file(file must exist before logging).
        """
        self.file = file
        self.log_data = {}

    def init(self, obj):
        """
        Logger.init(obj)
        returns - None

        Initializes object for logging.
        Object is required to have the following methods
            obj.get_obj_name()
            obj.get_obj_properties()
            obj.get_obj_id()
        """
        obj_dict = {'name': obj.get_obj_name(),
                    'properties': obj.get_obj_properties(),
                    'actions': []}

        self.log_data[obj.get_obj_id()] = obj_dict

    def log(self, obj, action):
        """
        Logger.log(obj, action(str))
        returns - None

        Logs the action. obj must be initializes with Logger.init() method before using method Logger.log().
        """
        action_dict = {'time': time.time(),
                       'action': action}
        self.log_data[obj.get_obj_id()]['actions'].append(action_dict)

    def dump(self):
        """
        Logger.dump()
        returns - None

        dumps the logs to a file.
        """
        with open(self.file, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, ensure_ascii=False, indent=4)
