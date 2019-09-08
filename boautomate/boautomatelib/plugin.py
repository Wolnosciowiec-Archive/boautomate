
import importlib


class PluginUtils:
    """
    Utils related to plugins implementation
    """

    @staticmethod
    def import_class_if_is_a_class(name: str):
        if "." not in name or " " in name:
            return None

        split = name.split('.')
        classname = split[-1:][0]
        namespace = ".".join(split[:-1])
        try:
            exec('from %s import %s' % (namespace, classname))
            class_obj = eval(classname)

            return class_obj

        except ImportError:
            return None
