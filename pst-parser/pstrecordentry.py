import pypff
import constants

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
