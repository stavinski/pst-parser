# USAGE

## COMMON PARAMS

### Required

* pstfile - the PST file to parse
* command - commands to perform against PST (either folder or message)

### Optional

* -f, --format - specify format for results to allow easier parsing, choices are screen or csv (default screen)
* -o, --output - file for outout (default stdout)
* -v, --verbose - turn on verbose logging (stdout only)

## Folder Command

Folder operations against PST allow travsersing the folder structure to gain top level information.

### PARAMS

* -p, --path - context path to use uses path seperators i.e. 1/5 (default is root)

### RETURNS

* path
* identifier
* name
* no. of sub folders
* no. of sub messages
* sub folders

## Message Command

Message operations against PST allow retrieving individual messages with optional filtering and choosing information to be returned about the message.

### PARAMS

* -p, --path - context path to use uses path seperators i.e. 1/5 (default is root)
* -mf, --message-fields - lists message fields available to be used for message fields returned
* -s, --search - search text to filter messages in folder
* -l, --look - where to look for search text provided {html, plaintext, subject, sender} (takes multiple)
* -i, --include - extra fields to return (takes multiple args)
* -bP, --bPlaintext - include plaintext in output
* -bH, --bHTML - include html in output

### RETURNS

* path
* index
* sender
* subject
* no. of attachments

Body types specified via -b*, --b* params and additional fields specified with --i, --include param

## EXAMPLES

    ./pst-parser.py input.pst folder --path 1
    ./pst-parser.py input.pst -f csv -o inbox_structure.csv -p 1/2
    ./pst-parser.py input.pst message -s "username" "password" -l html plaintext subject --fields "MESSAGE_PRIORITY" "MESSAGE_FLAGS"
    ./pst-parser.py input.pst message --path 1/3 --s "foo@bar.com" --include sender
    
