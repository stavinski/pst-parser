
def create_formatter(type="screen", *args, **kwargs):
    formatters = {
        "screen": ScreenFormatter,
        "csv": DelimiterFormatter
    }
    
    if not formatters.has_key(type):
        raise ValueError("type [%s] is invalid" % type)
        
    return formatters[type](*args, **kwargs)


class ScreenFormatter:
    
    def __init__(self, args=None):
        assert args is not None, "args must be provided"
        self._args = args
    
    
    def format_folder(self, path, folder):
        formatted_path = "root" if path is None else "/".join(map(str, path))  
    
        print "Path: %s" % formatted_path
        print "ID: %s" % folder.identifier
        print "Name: %s" % folder.name
        print "No. of sub folders: %d" % folder.number_of_sub_folders
        print "No. of messages: %d" % folder.number_of_messages
        
        if folder.has_sub_folders:
            print "Sub folders:"
           
            for (idx, sub_folder) in folder.get_folders_iter():
                if path is None:
                    print "%d: %s" % (idx, sub_folder.name)
                else:
                    print "%s/%d: %s" % (formatted_path, idx, sub_folder.name)
 
    
    def format_message(self, index, message):
        print "%d:" % index,
        print "-" * 80
        print "%s" % message.subject
        print "Sender: %s" % message.sender
        print "No. of attachments: %d" % message.number_of_attachments
        
        if self._args.include_plaintext:
            print "Plaintext:"
            print message.plain_text
            
        if self._args.include_html:
            print "HTML:"
            print message.html
        
 
class DelimiterFormatter:
    
    def __init__(self, args=None, delimiter=","):
        self._args = args
    