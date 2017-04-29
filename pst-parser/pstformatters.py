
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
        print "-" * 80
        print "%s" % message.get_subject()
        print "Sender: %s" % message.get_sender_name()
        print "No. of attachments: %d" % message.get_number_of_attachments()
        
        if self._args.include_plaintext:
            print "Plaintext:"
            print message.get_plain_text_body()
            
        if self._args.include_html:
            print "HTML:"
            print message.get_html_body()
        
 
class DelimiterFormatter:
    
    def __init__(self, args=None, delimiter=","):
        self._args = args
    