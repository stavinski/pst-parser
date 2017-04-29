#!/usr/bin/env python

# script properties
__description__ = r"""
 ___  ___ _____    ___  _   ___  ___ ___ ___ 
| _ \/ __|_   _|__| _ \/_\ | _ \/ __| __| _ \
|  _/\__ \ | ||___|  _/ _ \|   /\__ \ _||   /
|_|  |___/ |_|    |_|/_/ \_\_|_\|___/___|_|_\
"""
__author__ = "Mike Cromwell"
__version__ = "0.1.0"
__date__ = "2017/04/20"

import traceback
import sys
import os
import pypff
import csv
import constants

from pstformatters import create_formatter
from argparse import ArgumentParser, FileType, RawTextHelpFormatter
from pstrecordentry import PSTRecordEntry

def open_data_folder(pst_file):
    try:
        pff_file = pypff.file()
        pff_file.open_file_object(pst_file)
        root_folder = pff_file.get_root_folder()
        return root_folder.get_sub_folder(constants.OUTLOOK_DATA_FOLDER_IDX)
    except Exception as e:
        sys.exit("[!] could not open data folder")
        traceback.print_exc()
     
    
def get_folder(root, path_segments):
    if path_segments is None: # use root data folder
        return root
    
    # walk down the path segments
    folder = root
    
    try:
        for i in path_segments:
            folder = folder.get_sub_folder(int(i))
        
        return folder
    except IOError:
        sys.exit("[!] unable to access folder please check path is correct")
    
    
def handle_message_fields():
    # user just wants list of message fields
    if args.message_fields:
        print "[*] message fields available:"
        for field in constants.NAME_TO_ENTRY_TYPE.iterkeys():
            print field
        sys.exit(0)
        

def handle_folder_entity(data_folder, args, formatter):
    folder = get_folder(data_folder, args.path)
    formatter.format_folder(args.path, folder)
    

def handle_message_entity(data_folder, args, formatter):
    # in case user just wants the fields available
    if args.message_fields:
        handle_message_fields()
        sys.exit(0)
            
    folder = get_folder(data_folder, args.path)
    number_of_msgs = folder.get_number_of_sub_messages()
    msgs = { i: folder.get_sub_message(i) for i in range(0, number_of_msgs) }
            
    formatted_path = "root" if args.path is None else "/".join(map(str, args.path))  
    print "Path: %s" % formatted_path
    print "Folder: %s" % folder.get_name()
    
    
    for (idx, msg) in msgs.iteritems():
                
        #if args.body is not None:
            #for search in args.body:
                #body = msg.get_plain_text_body()
                #if search in body:
                    #msgs[i] = msg
                            
        formatter.format_message(idx, msg)
        
        
def main(args):
    pst_file = args.pstfile
    output = args.output
    formatter = create_formatter(args.format, args=args)
    
    try:
        data_folder = open_data_folder(pst_file)
        args.handler(data_folder, args, formatter)
    finally:
        pst_file.close()
        output.close()
        

# parses the path expresssion passed, expects path to be separated via forward slashes like
# directory traversing i.e. 1/4/10
def parse_path_expr(path):
    if path is not None:
        return [segment for segment in path.split("/") if segment != ""]
        
    return None


if __name__ == "__main__":
    root_parser = ArgumentParser(formatter_class=RawTextHelpFormatter, version=__version__, description=__description__)
    
    # global args   
    root_parser.add_argument("pstfile", help="PST file to be parsed", type=FileType("r"), metavar="PST_FILE")
    root_parser.add_argument("-f", "--format", type=str, help="format to display output in", choices=["screen", "csv"], default="screen")
    root_parser.add_argument("-o", "--output", help="file to write output to", type=FileType("w"), default=sys.stdout)
    root_parser.add_argument("-V", "--verbose", help=r"turn on extra logging to the screen", action="store_true")
        
    sub_parsers = root_parser.add_subparsers(title="commands", help="valid commands")
    
    # folder args
    folder_parser = sub_parsers.add_parser("folder", help="folder operations in PST")
    folder_parser.add_argument("-p", "--path", help=r"context path traverse like directory using /", type=parse_path_expr, default=None)
    folder_parser.set_defaults(handler=handle_folder_entity)
        
    # message args
    message_parser = sub_parsers.add_parser("message", help="message operations in PST")
    message_parser.add_argument("-p", "--path", help=r"context path traverse like directory using /", type=parse_path_expr, default=None)
    message_parser.add_argument("-mf", "--message-fields", help="klist message fields available", action="store_true")
    message_parser.add_argument("-s", "--search", help="search text to use", nargs="+", type=str, default=[])
    message_parser.add_argument("-l", "--look", help="where to look for search text provided", nargs="+", choices=["html", "plaintext", "subject", "sender"], default=[])
    message_parser.add_argument("-i", "--include", help="extra fields to return (list available retrieved via -mf, --message-fields)", default=[])
    message_parser.add_argument("-bP", "--bPlaintext", help="include plaintext content in output", action="store_true", dest="include_plaintext")
    message_parser.add_argument("-bH", "--bHTML", help="include html content in output", action="store_true", dest="include_html")
    message_parser.set_defaults(handler=handle_message_entity)
    
    args = root_parser.parse_args()
    main(args)