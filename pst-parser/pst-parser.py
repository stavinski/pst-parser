#!/usr/bin/env python

# script properties
__description__ = "Parses PST files using pypff"
__author__ = "Mike Cromwell"
__version__ = "0.1.0"
__date__ = "2017/04/20"

prog_name = r"""
  ___  ___ _____    ___  _   ___  ___ ___ ___ 
 | _ \/ __|_   _|__| _ \/_\ | _ \/ __| __| _ \
 |  _/\__ \ | ||___|  _/ _ \|   /\__ \ _||   /
 |_|  |___/ |_|    |_|/_/ \_\_|_\|___/___|_|_\
"""

import traceback
import sys
import os
import pypff
import csv
import constants

from pstformatters import create_formatter
from argparse import ArgumentParser, FileType, ArgumentDefaultsHelpFormatter
from pstrecordentry import PSTRecordEntry

global handlers

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
    folder = get_folder(data_folder, args.path)
    msgs = {}
    
    if folder.get_number_of_sub_messages() == 0:
        return
    
    if args.index is not None:
        for idx in args.index:
            if idx < 0 or idx > folder.get_number_of_sub_messages():
                sys.exit("[!] index [%d] is outside the bounds of the messages available" % idx)
            
            msgs[idx] = folder.get_sub_message(idx)
    
    for i in range(0, folder.get_number_of_sub_messages()):
        msg = folder.get_sub_message(i)
        
        if args.body is not None:
            for search in args.body:
                body = msg.get_plain_text_body()
                if search in body:
                    msgs[i] = msg
                    
        if args.subject is not None:
            for search in args.subject:
                subject = msg.get_subject()
                if search in subject:
                    msgs[i] = msg
                    
    for (idx, msg) in msgs.iteritems():
        formatter.format_message(idx, msg)
        
def main(args):
    handle_message_fields()
    pst_file = args.pstfile
    output = args.output
    formatter = create_formatter(args.format)
    
    try:
        data_folder = open_data_folder(pst_file)
        handler = entity_handlers[args.entity]
        handler(data_folder, args, formatter)
    finally:
        pst_file.close()
        output.close()
        

# parses the path expresssion passed, expects path to be separated via forward slashes like
# directory traversing i.e. 1/4/10
def parse_path_expr(path):
    if path is not None:
        return [segment for segment in path.split("/") if segment != ""]
        
    return None

entity_handlers = {
    "folder": handle_folder_entity,
    "message": handle_message_entity
}

if __name__ == "__main__":
    parser = ArgumentParser(prog_name, formatter_class=ArgumentDefaultsHelpFormatter, version=__version__)
    
    # required
    parser.add_argument("pstfile", help="PST file to be parsed", type=FileType("r"), metavar="PST_FILE")
    parser.add_argument("entity", help="Entity type to be parsed (folder or message)", choices=["folder", "message"], type=str, metavar="ENTITY_TYPE")
    
    # options
    parser.add_argument("-p", "--path", help=r"context path traverse like directory using /", type=parse_path_expr, default=None)
    parser.add_argument("-f", "--format", type=str, help="format to display output in", choices=["screen", "csv"], default="screen")
    parser.add_argument("-o", "--output", help="file to write output to", type=FileType("w"), default=sys.stdout)
    parser.add_argument("--message-fields", help="list message fields available", action="store_true")
    parser.add_argument("--index", help="index of the message(s) to return", nargs="+", type=int)    
    parser.add_argument("--body", help="search text for message body text", nargs="+", type=str)
    parser.add_argument("--recipient", help="search text for message recipient(s)", nargs="+", type=str)
    parser.add_argument("--sender", help="search text for message sender", nargs="+", type=str)
    parser.add_argument("--subject", help="search text for message subject", nargs="+", type=str)
    
    args = parser.parse_args()
    main(args)
    
    
#TODO: REMOVE THIS:

#if args.entity == "message":
    #output = sys.stdout
    #if args.output is not None:
        #output = open(args.output, "w")
    
    #try:
        #msg = inbox.get_sub_message(args.details)
        #sender = msg.get_sender_name()
        #subject = msg.get_subject()
        #attachments = msg.get_number_of_attachments()
        #rs = msg.get_record_set(0)
    
        #body = msg.get_plain_text_body()
        
        #if attachments > 0:
            #output.write("!")

        #if subject is not None:
            #output.write("[%s]" % subject.encode(errors="replace"))
        #else:
            #output.write("[no subject]")

        #if sender is not None:
            #output.write(" (%s) " % sender.encode(errors="replace"))
        
        #output.write(os.linesep)
        
        #if body is not None:
            #output.write(body)
            #output.write(os.linesep)
        
        #for entry_index in range(0, rs.get_number_of_entries()):
            #entry = PSTRecordEntry(rs.get_entry(entry_index))
            #output.write("[%s] => %s" % (unicode(entry.get_type()).encode("utf-8", errors="replace"), unicode(entry.get_value()).encode("utf-8", errors="replace")))
            #output.write(os.linesep) 
    #finally:
        #output.close()
    
#if args.query is not None:
    #found = 0
    #for index in range(0, inbox_number_of_messages):
        #msg = inbox.get_sub_message(index)
        #sender = msg.get_sender_name()
        #subject = msg.get_subject()
        #attachments = msg.get_number_of_attachments()
        #rs = msg.get_record_set(0)
        
        #body = msg.get_plain_text_body()
            
        #if body is not None and args.query in body:
            #print "[+] message: %d" % index, 
                            
            #if attachments > 0:
                #print "!",
    
            #if subject is not None:
                #print u"[%s]" % subject.encode(errors="replace"),
            #else:
                #print "[no subject]",
    
            #if sender is not None:
                #print u" (%s) " % sender.encode(errors="replace")
            
            #found += 1
        
    #print "[*] Messages with query found: %d" % found
