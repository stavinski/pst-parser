import re
import pypff

import constants


def parse_path_expr(expr):
    """
    parses the path expresssion passed, expects path to be separated via forward slashes like
    directory traversing i.e. '1/4/10'
    """
    
    if expr is not None:
        return [segment for segment in expr.split("/") if segment != ""]
        
    return None


class PSTFolder(object):
    """Represents a PST folder to make it easier to work with"""    
    
    def __init__(self, index, folder):
        self.index = index
        self.folder = folder
                
        # map the pypff folder object getters
        self.identifier = self.folder.get_identifier()
        self.name = self.folder.get_name()
        self.number_of_messages = self.folder.get_number_of_sub_messages()
        self.number_of_sub_folders = self.folder.get_number_of_sub_folders()
        self.has_sub_folders = self.number_of_sub_folders > 0
    
    def __repr__(self):
        return "PSTFolder [%s] => [%s]" % (self.identifier, self.name)
    
    def get_folder_from_path(self, path_segments):
        if path_segments is None:
            return PSTFolder(0, self.folder)
        
        # walk down the path segments
        folder = self.folder
        
        try:
            for i in path_segments:
                folder = folder.get_sub_folder(int(i))
            
            idx = path_segments[:-1]
            return PSTFolder(idx, folder)
        except IOError:
            raise PSTFolderAccessError("[!] unable to access folder please check path is correct")
    
    def get_folders_iter(self):
        for i in xrange(0, self.number_of_sub_folders):
            yield PSTFolder(i, self.folder.get_sub_folder(i))
            
    def get_messages_iter(self, max_messages=1000):
        max_messages_returned = min(self.number_of_messages, max_messages)
        for i in xrange(0, max_messages_returned):
            yield PSTMessage(i, self.folder.get_sub_message(i), self.folder)
    

class PSTMessage:
    """Represents a pypff message"""
    
    def __init__(self, index, message, folder):
        self.index = index
        self.message = message
        self.folder = folder
        
        # map pypff message getters
        self.sender = self.message.get_sender_name()
        self.html = self.message.get_html_body()
        self.plain_text = self.message.get_plain_text_body()
        self.number_of_attachments = self.message.get_number_of_attachments()
        self.subject = self.message.get_subject()
        
    def __repr__(self):
        return "PSTMessage [%s]" % self.subject
            
    @staticmethod
    def _get_val_or_empty_str(val):
        return "" if not val else val
            
    def has_senders(self, *senders):
        sender = self.sender
        if not sender:
            return True
        
        for search_sender in map(str.lower, senders):
            if search_sender in sender.lower():
                return True
        
        return False
        
    def contains_text(self, *contents):
        subject = PSTMessage._get_val_or_empty_str(self.subject).lower()
        plain_text = PSTMessage._get_val_or_empty_str(self.plain_text).lower()
        html = PSTMessage._get_val_or_empty_str(self.html).lower()
        
        return any(content in subject
                   or content in plain_text
                   or content in html 
                   for content in map(str.lower, contents))


class PSTRecordEntry:
    """Respresents a Record Entry from a PST"""
    
    # mappings to functions to retrieve the value of the entry
    value_type_funcs = {
        0x0000: lambda _: None, #LIBPFF_VALUE_TYPE_UNSPECIFIED
        0x0001: lambda _: None, #LIBPFF_VALUE_TYPE_NULL
        0x0002: pypff.record_entry.get_data_as_integer, #LIBPFF_VALUE_TYPE_INTEGER_16BIT_SIGNED
        0x0003: pypff.record_entry.get_data_as_integer, #LIBPFF_VALUE_TYPE_INTEGER_32BIT_SIGNED
        0x0004: pypff.record_entry.get_data_as_floating_point, #LIBPFF_VALUE_TYPE_FLOAT_32BIT						
        0x0005: pypff.record_entry.get_data_as_floating_point, #LIBPFF_VALUE_TYPE_DOUBLE_64BIT						
        0x0006: pypff.record_entry.get_data_as_floating_point, #LIBPFF_VALUE_TYPE_CURRENCY
        0x0007: pypff.record_entry.get_data_as_floating_point, #LIBPFF_VALUE_TYPE_FLOATINGTIME
        0x000a: pypff.record_entry.get_data, #LIBPFF_VALUE_TYPE_ERROR
        0x000b: pypff.record_entry.get_data_as_boolean, #LIBPFF_VALUE_TYPE_BOOLEAN
        0x000d: pypff.record_entry.get_data, #LIBPFF_VALUE_TYPE_OBJECT
        0x0014: pypff.record_entry.get_data_as_integer, #LIBPFF_VALUE_TYPE_INTEGER_64BIT_SIGNED
        0x001e: pypff.record_entry.get_data_as_string, #LIBPFF_VALUE_TYPE_STRING_ASCII
        0x001f: lambda x:unicode(pypff.record_entry.get_data_as_string(x)), #LIBPFF_VALUE_TYPE_STRING_UNICODE
        0x0040: pypff.record_entry.get_data_as_integer, #LIBPFF_VALUE_TYPE_FILETIME 
        0x0048: pypff.record_entry.get_data_as_string, #LIBPFF_VALUE_TYPE_GUID
        0x00fb: pypff.record_entry.get_data_as_string, #LIBPFF_VALUE_TYPE_SERVER_IDENTIFIER
        #0x00fd: pypff.record_entry.get_data, #LIBPFF_VALUE_TYPE_RESTRICTION
        #0x00fe: pypff.record_entry.get_data, #LIBPFF_VALUE_TYPE_RULE_ACTION
        #0x0102: pypff.record_entry.get_data #LIBPFF_VALUE_TYPE_BINARY_DATA 

        # not sure how to deal with these types yet!						
        #LIBPFF_VALUE_TYPE_MULTI_VALUE_INTEGER_16BIT_SIGNED			: 0x1002,
        #LIBPFF_VALUE_TYPE_MULTI_VALUE_INTEGER_32BIT_SIGNED			: 0x1003,
        #LIBPFF_VALUE_TYPE_MULTI_VALUE_FLOAT_32BIT				: 0x1004,
        #LIBPFF_VALUE_TYPE_MULTI_VALUE_DOUBLE_64BIT				: 0x1005,
        #LIBPFF_VALUE_TYPE_MULTI_VALUE_CURRENCY					: 0x1006,
        #LIBPFF_VALUE_TYPE_MULTI_VALUE_FLOATINGTIME				: 0x1007,
        #LIBPFF_VALUE_TYPE_MULTI_VALUE_INTEGER_64BIT_SIGNED			: 0x1014,
        #LIBPFF_VALUE_TYPE_MULTI_VALUE_STRING_ASCII				: 0x101e,
        #LIBPFF_VALUE_TYPE_MULTI_VALUE_STRING_UNICODE				: 0x101f,
        #LIBPFF_VALUE_TYPE_MULTI_VALUE_FILETIME					: 0x1040,
        #LIBPFF_VALUE_TYPE_MULTI_VALUE_GUID					: 0x1048,
        #LIBPFF_VALUE_TYPE_MULTI_VALUE_BINARY_DATA				: 0x1102                
    }

    def __init__(self, record_entry):
        self.record_entry = record_entry

    def get_type(self):
        entry_type = self.record_entry.get_entry_type()
        if not entry_type:
            return None

        if entry_type in constants.ENTRY_TYPE_TO_NAME:
            return constants.ENTRY_TYPE_TO_NAME[entry_type]

        return hex(entry_type)

    def get_value(self):
        val_type = self.record_entry.get_value_type()
        if not val_type:
            return None

        if val_type in PSTRecordEntry.value_type_funcs:
            func = PSTRecordEntry.value_type_funcs[val_type]
            return func(self.record_entry)

        return hex(val_type)

"""
PST Parser specific errors
"""

class PSTError(Exception):
    pass

class PSTFolderAccessError(PSTError):
    pass