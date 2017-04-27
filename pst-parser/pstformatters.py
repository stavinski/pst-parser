
def create_formatter(type="screen", *args, **kwargs):
    formatters = {
        "screen": ScreenFormatter,
        "csv": CsvFormatter
    }
    
    if not formatters.has_key(type):
        raise ValueError("type [%s] is invalid" % type)
        
    return formatters[type](*args, **kwargs)


class Formatter:
    def format_folder(self, path=None, folder=None):
        pass
    
    def format_message(self, idx, message):
        pass

class ScreenFormatter(Formatter):
    
    def format_folder(self, path, folder):
        formatted_path = "root" if path is None else "/".join(map(str, path))  
    
        print "Path: %s" % formatted_path
        print "ID: %s" % folder.get_identifier()
        print "Name: %s" % folder.get_name()
        print "No. of sub folders: %d" % folder.get_number_of_sub_folders()
        print "No. of messages: %d" % folder.get_number_of_sub_messages()
        
        if folder.get_number_of_sub_folders() > 0:
            print "Sub folders:"
            
            for i in range(0, folder.get_number_of_sub_folders()):
                if path is None:
                    print "%d: %s" % (i, folder.get_sub_folder(i).get_name())
                else:
                    print "%s/%d: %s" % (formatted_path, i, folder.get_sub_folder(i).get_name())
 
    
    def format_message(self, index, message):
        print "%d:" % index,
        print "[%s]" % message.get_subject()
    
        
 
class CsvFormatter(Formatter):
    pass