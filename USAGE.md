# USAGE

## COMMON PARAMS

* -p, --path - context path to use takes multiple args for each section of the path i.e. -p 1 10  (Default is root folder)
* -r, --recurse -  flag to recurse down the folder struture
* -f, --format - specify format for results to allow easier parsing, choices are screen or csv (Default screen)
* -o, --output - file for outout (Default stdout)
* --message-fields - lists message fields available to be used for message fields returned

## MODES

_Summary (Default) - provides summary information about the path chosen (plus sub folders if recurse specified)_

## RETURNS

* index
* identifier
* name
* no. of sub folders
* no. of sub messages

_Query - allows querying of messages using the path specified (plus sub folders if recurse specified)_

## PARAMS

* --body - contains search text in the message body (takes multiple args)
* --recipient - contains search text for recipient (takes multiple args)
* --sender - contains search text for sender (takes multiple args)
* --fields - extra fields to return (takes multiple args)

## RETURNS

* path
* index
* sender
* recipient
* subject
* no. of attachments
* plaintext body
* html body

plsuy additional fields specified with --fields param

## EXAMPLES

# ./pst-parser --
# ./pst-parser --path 1 --recurse
# ./pst-parser --query --path 1 3 --sender "foo@bar.com" --recipient "joe@somewhere.com" --body "" --path 1 23

