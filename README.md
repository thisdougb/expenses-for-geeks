## Synopsis

A simple tool for those of us who prefer CLI and have to submit expenses forms.  I try to create expenses records with as few key strokes as possible, and my intention is only to solve the data entry part of the expenses claim process.

## Code Example
```
[vagrant@expenses ~]$ python expenses.py 
#####################################################################################################
rcpt     date     description                               vat %        cost         vat       gross
----  ----------  ----------------------------------------  -----  ----------  ----------  ----------
                                                                   ----------  ----------  ----------
                                                                         0.00        0.00        0.00
                                                                   ----------  ----------  ----------

>>>>  2016-12-17  None                                       20.0        0.00        0.00        0.00
(expenses) desc Hotel for Python Conference
(expenses) gross 65
(expenses) commit
#####################################################################################################
rcpt     date     description                               vat %        cost         vat       gross
----  ----------  ----------------------------------------  -----  ----------  ----------  ----------
   1  2016-12-17  Hotel for Python Conference                20.0       54.17       10.83       65.00
                                                                   ----------  ----------  ----------
                                                                        54.17       10.83       65.00
                                                                   ----------  ----------  ----------

>>>>  2016-12-17  Hotel for Python Conference                20.0       54.17       10.83       65.00
```

## Motivation

Filling out expenses claim forms is the bane of my life, so I decided to create a faster method.   GUI-based forms are slow and error prone, as you navigate around spreadsheet cells.   With a CLI interface and reusing data where possible I find this tool much faster to complete the data entry part of expenses claims.

The data sits in json files, but I will build an export function to dump expenses to accountant-friendly csv files.  Once the data is in digital form you can then export it to whatever post-processing tool you use.

## Installation

Simply copy the expenses.py script and use it.   When creating a new expenses sheet (eg, load 'MyEdinburghTrip') this will be created as a file on disk in the same directory.

## Usage
The line beginning with '>>>>' is the cached data line, and this is the data that will be written when you 'commit'.  Change any of the fields then commit.  The monetary values are worked out for you, so if you just enter 'gross 12' then you'll find the other values appear.   With this system you can also simply type 'cost 10' and automatically populate the vat and gross values.   The vat % is changed with 'rate <value>'.   At any time you can submit an empty line and it'll print the cached data line, incase you forget where you are.

Date changes are interesting.   With 'date -1' you can step backwards, and 'date +1' steps forwards again (any Int is ok, so long as it's not in the future).   The regular 'date 2016-12-04' works too.
```
>>>>  2016-12-17  Hotel for Python Conference                20.0       56.67       11.33       68.00
(expenses) date -5
(expenses) 

>>>>  2016-12-12  Hotel for Python Conference                20.0       56.67       11.33       68.00
(expenses) date 2016-12-15
(expenses) 

>>>>  2016-12-15  Hotel for Python Conference                20.0       56.67       11.33       68.00
```
If you want to remove a commited expenses line then 'del 3' will remove line 3.  While this does remove the line (from the data file too), the cached line ('>>>>') takes the values of the deleted item.   This means you can modify an existing expenses item with del 1, gross 68, commit:
```
#####################################################################################################
rcpt     date     description                               vat %        cost         vat       gross
----  ----------  ----------------------------------------  -----  ----------  ----------  ----------
   1  2016-12-17  Hotel for Python Conference                20.0       54.17       10.83       65.00
   2  2016-12-17  Lunch with Perl subversives                20.0       19.17        3.83       23.00
   3  2016-12-16  K&R C Book                                  0.0       13.00        0.00       13.00
                                                                   ----------  ----------  ----------
                                                                        86.33       14.67      101.00
                                                                   ----------  ----------  ----------

>>>>  2016-12-16  K&R C Book                                  0.0       13.00        0.00       13.00
(expenses) del 1
(expenses) gross 68
(expenses) commit
#####################################################################################################
rcpt     date     description                               vat %        cost         vat       gross
----  ----------  ----------------------------------------  -----  ----------  ----------  ----------
   1  2016-12-17  Lunch with Perl subversives                20.0       19.17        3.83       23.00
   2  2016-12-16  K&R C Book                                  0.0       13.00        0.00       13.00
   3  2016-12-17  Hotel for Python Conference                20.0       56.67       11.33       68.00
                                                                   ----------  ----------  ----------
                                                                        88.83       15.17      104.00
                                                                   ----------  ----------  ----------

>>>>  2016-12-17  Hotel for Python Conference                20.0       56.67       11.33       68.00
```

Basic help system:
```
(expenses) help

Documented commands (type help <topic>):
========================================
bye  commit  cost  date  del  desc  gross  help  load  rate  show
```
Expenses data is saved in .json files (which allows outside/shell manipulation if you want to).   If you want to create a new expenses data file then use the load command.   The command prompt displays the active expenses file.   Saves are made on each commit, so there is no 'save' option.
```
(expenses) load mynewexpenses
#####################################################################################################
rcpt     date     description                               vat %        cost         vat       gross
----  ----------  ----------------------------------------  -----  ----------  ----------  ----------
                                                                   ----------  ----------  ----------
                                                                         0.00        0.00        0.00
                                                                   ----------  ----------  ----------

>>>>  2016-12-17  None                                       20.0        0.00        0.00        0.00
(mynewexpenses)
```
