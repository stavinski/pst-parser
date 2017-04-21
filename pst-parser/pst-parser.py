#!/usr/bin/env python

# script properties
__description__ = "Parses PST files using pypff"
__author__ = "Mike Cromwell"
__version__ = "0.1.0"
__date__ = "2017/04/20"

import traceback
import sys
import os
import pypff
import csv

from argparse import ArgumentParser, FileType, ArgumentDefaultsHelpFormatter
from pstrecordentry import PSTRecordEntry

# consts
MODE_FOLDER = "folder"
MODE_MESSAGE = "message"

OUTLOOK_DATA_FOLDER = 1

def open_data_folder(pst_file):
    try:
        pff_file = pypff.file()
        pff_file.open_file_object(pst_file)
        root_folder = pff_file.get_root_folder()
        return root_folder.get_sub_folder(OUTLOOK_DATA_FOLDER)
    except Exception as e:
        sys.exit("[!] could not open data folder")
        traceback.print_exc()
    
    
def print_folder_summary(path, folder):
    formatted_path = "root" if path is None else "/".join(map(str, path))  
    
    print "Path: %s" % formatted_path
    print "ID: %s" % folder.get_identifier()
    print "Name: %s" % folder.get_name()
    print "No. of sub folders: %d" % folder.get_number_of_sub_folders()
    print "No. of messages: %d" % folder.get_number_of_sub_messages()
    
    if folder.get_number_of_sub_folders() > 0:
        print "Sub Folders:"
        
        for i in range(0, folder.get_number_of_sub_folders()):
            if path is None:
                print "[%d] => %s" % (i, folder.get_sub_folder(i).get_name())
            else:
                print "[%s/%d] => %s" % (formatted_path, i, folder.get_sub_folder(i).get_name())
    
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
    
    
def main(args):
    data_folder = open_data_folder(args.pstfile)
    
    if args.mode == "folder":
        folder = get_folder(data_folder, args.path)
        print_folder_summary(args.path, folder)
        sys.exit(0)
        
    
    folder = get_folder(data_folder, "1")
    print_folder_summary(folder)
    
    
    inbox = data_folder.get_sub_folder(INBOX)
    deleted = data_folder.get_sub_folder(DELETED)
    inbox_number_of_messages = inbox.get_number_of_sub_messages()
    deleted_number_of_messages = deleted.get_number_of_sub_messages()

    print "[*] message count"
    print "[inbox] => %d" % inbox_number_of_messages
    print "[deleted] => %d" % deleted_number_of_messages

    if args.details:
        output = sys.stdout
        if args.output is not None:
            output = open(args.output, "w")
        
        try:
            msg = inbox.get_sub_message(args.details)
            sender = msg.get_sender_name()
            subject = msg.get_subject()
            attachments = msg.get_number_of_attachments()
            rs = msg.get_record_set(0)
        
            body = msg.get_plain_text_body()
            
            if attachments > 0:
                output.write("!")
    
            if subject is not None:
                output.write("[%s]" % subject.encode(errors="replace"))
            else:
                output.write("[no subject]")
    
            if sender is not None:
                output.write(" (%s) " % sender.encode(errors="replace"))
            
            output.write(os.linesep)
            
            if body is not None:
                output.write(body)
                output.write(os.linesep)
            
            for entry_index in range(0, rs.get_number_of_entries()):
                entry = PSTRecordEntry(rs.get_entry(entry_index))
                output.write("[%s] => %s" % (unicode(entry.get_type()).encode("utf-8", errors="replace"), unicode(entry.get_value()).encode("utf-8", errors="replace")))
                output.write(os.linesep) 
        finally:
            output.close()
        
    if args.query is not None:
        found = 0
        for index in range(0, inbox_number_of_messages):
            msg = inbox.get_sub_message(index)
            sender = msg.get_sender_name()
            subject = msg.get_subject()
            attachments = msg.get_number_of_attachments()
            rs = msg.get_record_set(0)
            
            body = msg.get_plain_text_body()
                
            if body is not None and args.query in body:
                print "[+] message: %d" % index, 
                                
                if attachments > 0:
                    print "!",
        
                if subject is not None:
                    print u"[%s]" % subject.encode(errors="replace"),
                else:
                    print "[no subject]",
        
                if sender is not None:
                    print u" (%s) " % sender.encode(errors="replace")
                
                found += 1
            
        print "[*] Messages with query found: %d" % found
        
    args.pstfile.close()

def parse_path(path):
    if path is not None:
        return [segment for segment in path.split("/") if segment != ""]
        
    return None

if __name__ == "__main__":
    parser = ArgumentParser("PST parser", formatter_class=ArgumentDefaultsHelpFormatter, version=__version__, description=__description__)
    
    # required
    parser.add_argument("pstfile", help="PST file to be parsed", type=FileType("r"), metavar="PST_FILE")
    
    # options
    parser.add_argument("-m", "--mode", help="switches mode to folder or message", default="folder")
    parser.add_argument("-p", "--path", help="context path separate with /", type=parse_path, default=None)
    #parser.add_argument("-r", "--recurse", action="store_true", help="recurse sub folders")
    #parser.add_argument("-f", "--format", type=str, help="format to display output in")
    #parser.add_argument("-o", "--output", help="file to write output to", type=FileType("w"), default=sys.stdout)
    #parser.add_argument("--message-fields", help="list message fields available", action="store_true")
    parser.add_argument("--index", help="index of the message(s) to return", nargs="+", type=int)    
    parser.add_argument("--body", help="search text for message body text", nargs="+", type=str)
    parser.add_argument("--recipient", help="search text for message recipient(s)", nargs="+", type=str)
    parser.add_argument("--sender", help="search text for message sender", nargs="+", type=str)
    parser.add_argument("--subject", help="search text for message subject", nargs="+", type=str)
    
    args = parser.parse_args()
    main(args)