# USAGE

## COMMON PARAMS

* -m, --mode - switches into either folder or message mode (default is folder)
* -p, --path - context path to use takes multiple args for each section of the path i.e. -p 1 10  (default is root folder)
* -r, --recurse - flag to recurse down the folder struture
* -f, --format - specify format for results to allow easier parsing, choices are screen or csv (default screen)
* -o, --output - file for outout (default stdout)
* --message-fields - lists message fields available to be used for message fields returned

## Folder (default)

Provides folder information about the path chosen (plus sub folders if recurse specified).

### RETURNS

* index
* identifier
* name
* no. of sub folders
* no. of sub messages

## Message 

Provides message information for messages in the path chosen (plus sub folders if recurse specified) using optional filters provided.

### PARAMS

* --index - index of message (takes multiple args)
* --body - contains search text in the message body (takes multiple args)
* --recipient - contains search text for recipient (takes multiple args)
* --sender - contains search text for sender (takes multiple args)
* --fields - extra fields to return (takes multiple args)

*WARNING: specifying recurse with a tree with lots of folders and messaeges could take a long time to process*

### RETURNS

* path
* index
* sender
* recipient
* subject
* no. of attachments
* plaintext body
* html body

plus additional fields specified with --fields param

## EXAMPLES

    ./pst-parser --path 1 --recurse
    ./pst-parser -p 1 -f csv -o inbox_structure.log
    ./pst-parser -m message --index 200 202 215 --fields "MESSAGE_PRIORITY" "MESSAGE_FLAGS"
    ./pst-parser -m message --path 1 3 --sender "foo@bar.com" --recipient "joe@somewhere.com" --path 1 23
    
