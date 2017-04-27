# USAGE

## COMMON PARAMS

### Required

* pstfile - the PST file to parse
* entity - the type of entity to perform actions against (either folder or message)

### Optional

* -p, --path - context path to use uses path seperators i.e. 1/5 (default is root)
* -r, --recurse - flag to recurse down the folder struture
* -f, --format - specify format for results to allow easier parsing, choices are screen or csv (default screen)
* -o, --output - file for outout (default stdout)
* --message-fields - lists message fields available to be used for message fields returned
* -v, --verbose - turn on verbose logging (stdout only)

## Folder Entity

Provides folder information about the path chosen (plus sub folders if recurse specified).

### RETURNS

* path
* identifier
* name
* no. of sub folders
* no. of sub messages
* sub folders

## Message Entity

Provides message information for messages in the path chosen (plus sub folders if recurse specified) using optional filters provided.

### PARAMS

* --index - index of message (takes multiple args)
* --body - contains search text in the message body (takes multiple args)
* --recipient - contains search text for recipient (takes multiple args)
* --sender - contains search text for sender (takes multiple args)
* --subject - contains search text for subject (takes multiple args)
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

    ./pst-parser folder --path 1 --recurse
    ./pst-parser -p 1 -f csv -o inbox_structure.csv
    ./pst-parser message --index 200 202 215 --fields "MESSAGE_PRIORITY" "MESSAGE_FLAGS"
    ./pst-parser message --path 1/3 --sender "foo@bar.com" --recipient "joe@somewhere.com"
    
