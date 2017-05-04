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

from pstformatters import from_name
from argparse import ArgumentParser, FileType, RawTextHelpFormatter
from pstobjects import PSTFolder, PSTRecordEntry, parse_path_expr

def open_data_folder(pst_file):
    try:
        pff_file = pypff.file()
        pff_file.open_file_object(pst_file)
        root_folder = pff_file.get_root_folder()
        return PSTFolder(0, root_folder.get_sub_folder(constants.OUTLOOK_DATA_FOLDER_IDX))
    except Exception as e:
        traceback.print_exc()
        sys.exit("[!] could not open data folder")
     

def handle_message_fields():
    # user just wants list of message fields
    if args.message_fields:
        print "[*] message fields available:"
        for field in constants.NAME_TO_ENTRY_TYPE.iterkeys():
            print field
        
        sys.exit(0)
        

def handle_folder_entity(data_folder, args, formatter):
    folder = data_folder.get_folder_from_path(args.path)
    formatter.format_folder(args.path, folder)
    

def handle_message_entity(data_folder, args, formatter):
    # in case user just wants the fields available
    if args.message_fields:
        handle_message_fields()
        sys.exit(0)
        
    folder = data_folder.get_folder_from_path(args.path)
    number_of_msgs = folder.number_of_messages
    
    # display folder info
    formatted_path = "root" if not args.path else "/".join(map(str, args.path))  
    print "[+] Path: %s" % formatted_path
    print "[+] Folder: %s" % folder.name
       
    msgs = folder.get_messages_iter()
    msg_count = 0
    for msg in msgs:
        
        # check if the sender matches if supplied
        if args.sender and not msg.has_senders(*args.sender):
            continue
        
        # check that search matches if supplied
        if args.search and not msg.contains_text(*args.search):
            continue
                
        formatter.format_message(msg)
        msg_count += 1
        
    if msg_count > 0:
        print "[+] Found %d messages" % msg_count
    else:
        print "[-] Found no messages"
 
        
def main(args):
    pst_file = args.pstfile
    output = args.output
    formatter = from_name(name=args.format, output=output, args=args)
    
    try:
        data_folder = open_data_folder(pst_file)
        args.handler(data_folder, args, formatter)
    finally:
        pst_file.close()
        output.close()
        

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
    message_parser.add_argument("-mf", "--message-fields", help="list available message fields", action="store_true")
    message_parser.add_argument("-s", "--search", help="search text to use", nargs="+", type=str)
    message_parser.add_argument("-S", "--sender", help="sender(s) to restrict to", nargs="+", type=str)
    message_parser.add_argument("-i", "--include", help="extra fields to return (list available retrieved via -mf, --message-fields)", default=[])
    message_parser.add_argument("-bP", "--bPlaintext", help="include plaintext content in output", action="store_true", dest="include_plaintext")
    message_parser.add_argument("-bH", "--bHTML", help="include html content in output", action="store_true", dest="include_html")
    message_parser.set_defaults(handler=handle_message_entity)
    
    args = root_parser.parse_args()
    main(args)