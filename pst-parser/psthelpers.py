import re
import pypff

import constants

"""
parses the path expresssion passed, expects path to be separated via forward slashes like
directory traversing i.e. 1/4/10
"""
def parse_path_expr(expr):
    if expr is not None:
        return [segment for segment in expr.split("/") if segment != ""]
        
    return None


"""
Represents a PST folder to make it easier to work with
"""

class PSTFolder:
       
    def __init__(self, folder):
        self.folder = folder
        
        
    @property
    def identifier(self):
        return self.folder.get_identifier()
    
    @property
    def name(self):
        return self.folder.get_name()
    
    
    @property
    def number_of_sub_folders(self):
        return self.folder.get_number_of_sub_folders()
    
    
    @property
    def has_sub_folders(self):
        return self.number_of_sub_folders > 0
            
    @property
    def number_of_messages(self):
        return self.folder.get_number_of_sub_messages()
    
    @property
    def name(self):
        return self.folder.get_name()
           
    
    def get_folder_from_path(self, path_segments):
        if path_segments is None:
            return PSTFolder(self.folder)
        
        # walk down the path segments
        folder = self.folder
        
        try:
            for i in path_segments:
                folder = folder.get_sub_folder(int(i))
            
            return PSTFolder(folder)
        except IOError:
            raise PSTFolderAccessError("[!] unable to access folder please check path is correct")
    
    
    def get_folders_iter(self):
        for i in range(0, self.number_of_sub_folders):
            yield (i, PSTFolder(self.folder.get_sub_folder(i)))
            
    
    def get_messages_iter(self):
        for i in range(0, self.number_of_messages):
            yield (i, PSTMessage(self.folder.get_sub_message(i)))
    

class PSTMessage:
    
    def __init__(self, message):
        self.message = message
        
        
    @classmethod
    def _get_val_or_empty(cls, val):
        if val is None:
            return ""
        else:
            return val

    @property
    def number_of_attachments(self):
        return self.message.get_number_of_attachments()

    
    @property
    def sender(self):
        return self.message.get_sender_name()
    
    
    @property
    def subject(self):
        return self.message.get_subject()
        
    
    @property
    def plain_text(self):
        return self.message.get_plain_text_body()
        

    @property
    def html(self):
        return self.message.get_html_body()
    
    
    def has_senders(self, *senders):
        sender = self.sender
        if sender is None:
            return True
        
        for search_sender in map(str.lower, senders):
            if search_sender in sender.lower():
                return True
        
        return False
    
    
    def contains_text(self, *contents):
        subject = PSTMessage._get_val_or_empty(self.subject).lower()
        plain_text = PSTMessage._get_val_or_empty(self.plain_text).lower()
        html = PSTMessage._get_val_or_empty(self.html).lower()
        
        return any(content in subject
                   or content in plain_text
                   or content in html 
                   for content in map(str.lower, contents))

"""
Respresents a Record Entry from a PST
"""

class PSTRecordEntry:

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
        if entry_type is None:
            return None


        if constants.ENTRY_TYPE_TO_NAME.has_key(entry_type):
            return constants.ENTRY_TYPE_TO_NAME[entry_type]

        return hex(entry_type)


    def get_value(self):
        val_type = self.record_entry.get_value_type()
        if val_type is None:
            return None

        if PSTRecordEntry.value_type_funcs.has_key(val_type):
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