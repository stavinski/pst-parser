
import csv
import sys

# registry of formatters filled when subclasses are created
formatters = {}

def available_formatters():
    return formatters.keys()

def from_name(name="screen", output=sys.stdout, args=None):
    """
    Helper function to create correct formatter based on type passed
    
    Args:
     - name (str): the name of formatter to create
     - output (file): the output location
     
    Returns:
     found PSTFormatter implementation
    """
    return formatters[name](output=output, args=args)


class PSTFormatterMeta(type):
    """used by PSTFormatter to validate sub classes and also auto register into formatters dict"""
    
    @staticmethod
    def _name_defined(name, fields):
        if not "name" in fields:
            raise ValueError("name not defined in %s" % name)

    @staticmethod
    def _register_formatter(name, cls):
        formatter_name = name
        formatters[formatter_name] = cls        
    
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        
        if name == "PSTFormatter":
            return cls
        
        PSTFormatterMeta._name_defined(name, class_dict)
        PSTFormatterMeta._register_formatter(class_dict["name"], cls)      
        
        return cls


class PSTFormatter(object):
    """base class for formatters"""
    
    # allows sub classes to be automatically registered
    __metaclass__ = PSTFormatterMeta
    
    # specified by sub classes
    name = None
    
    def __init__(self, output=None, args=None):
        assert output is not None, "output must be provided"
        self._output = output
        self._args = args
        
    def format_folder(self, path, folder):
        raise NotImplementedError()
    
    def format_message(self, message):
        raise NotImplementedError()
    

class PSTScreenFormatter(PSTFormatter):
    """formats output for screen"""
    
    name = "screen"
    
    def __init__(self, output, args):
        super(PSTScreenFormatter, self).__init__(output, args)
        
    def format_folder(self, path, folder):
        formatted_path = "root" if path is None else "/".join(map(str, path))  
    
        print >> self._output, "Path: %s" % formatted_path
        print >> self._output, "ID: %s" % folder.identifier
        print >> self._output, "Name: %s" % folder.name
        print >> self._output, "No. of sub folders: %d" % folder.number_of_sub_folders
        print >> self._output, "No. of messages: %d" % folder.number_of_messages
        
        if folder.has_sub_folders:
            print >> self._output, "Sub folders:"
           
            for sub_folder in folder.get_folders_iter():
                if path is None:
                    print >> self._output, "%d: %s" % (sub_folder.index, sub_folder.name)
                else:
                    print >> self._output, "%s/%d: %s" % (formatted_path, sub_folder.index, sub_folder.name)
 
    
    def format_message(self, message):
        print >> self._output, "%d:" % message.index,
        print >> self._output, "-" * 80
        print >> self._output, "%s" % message.subject
        print >> self._output, "Sender: %s" % message.sender
        print >> self._output, "No. of attachments: %d" % message.number_of_attachments
        
        if self._args.include_plaintext:
            print >> self._output, "Plaintext:"
            print >> self._output, message.plain_text
            
        if self._args.include_html:
            print >> self._output, "HTML:"
            print >> self._output, message.html
        
 
class PSTCSVFormatter(PSTFormatter):
    """formats output into csv""" 
    
    name = "csv"
    
    def __init__(self, output=None, args=None):
        super(PSTCSVFormatter, self).__init__(output, args)
        
    def format_folder(self, path, folder):
        pass
    
    def format_message(self, message):
        pass

