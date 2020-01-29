#!/usr/bin/python
# Include Python libraries for system, OS and reg-ex functions
import sys
import os.path
import re

###############################################################################
#
#   Name: ProcessSQL.py
# Author: Tele Charalambous
#
# Description:
#   The goal of this script is to be able to investigate/import multiple
#   databases into one MySQL server by omitting data which is not required
#   e.g. history, logging, debug tables.
#
#   This script processes, reformats and reduces the MySQL database dump size
#   for importing MySQL server. It lists the top 10 largest tables by counting
#   the INSERT statements. E.g. some databases have huge tables which can be
#   stripped out where required turning a 20GB SQL dump into a 150MB file
#   By reducing this dump file size, multiple copies of the database take
#   less time and space to import on a MySQL server.
#
#   It also reformats hugely long INSERT lines so that each row is on a
#   separate line making it easier for reading & grepping, and syntax is
#   unaffected so it can still be imported into a MySQL server.
#
#   This script removes the (6) from the TIMESTAMP column definition which
#   specifies 6-digit precision. MySQL imports into servers with default
#   installs, e.g. turnkey VMs, which tend to choke on the (6) format.
#
#   This script was built and tested with Python v2.7. Free Python for
#   Windows is available from https://www.python.org/downloads/windows/
#   Linux will most likely already have it installed
#
# USAGE Examples:
#
# - To list large tables:
#    ./ProcessSQL.py  Original.sql
#
# - To reformat INSERT statements into readable rows (good for grepping)
#    ./ProcessSQL.py  Original.sql  Output.sql
#
# - To exclude INSERT statements for 3 tables: BigTable1 BigTable2 BigTable3
#    ./ProcessSQL.py  Original.sql Output.sql  BigTable1 BigTable2 BigTable3
#
#
# KNOWN ISSUES:
#   This will potentially split valid SQL data if it contains the un-escaped
#   character sequence of "),(" since this is the INSERT row delimiter which
#   is used to split the lines into readable SQL.
#
###############################################################################
# Revision History
# ----------------
#  *** Current ***
Version = "v1.02.01"
#  Updated by: Tele Charalambous
#        Date: 2019-08-16
#       Notes: Fixed syntax to be PEP-08 compliant (except for one line)
#
#  *** Previous Changes ***
#  Updated by: Tele Charalambous
#        Date: 2019-05-31
#       Notes: Fixed some filenames vs file handles. Created backward
#              compatible version ye olde Python 2.4.3
#
#  Updated by: Tele Charalambous
#        Date: 2019-05-15
#       Notes: Reworded help message to say 'tables to exclude' & added usage
#
#     Version: v1.00.00
#  Updated by: Tele Charalambous
#        Date: 2019-04-12
#       Notes: Will overwrite an existing destination file with a warning but
#              without asking. Code has no current known issues if args are
#              observed correctly. Large SQL files obviously take longer, but
#              we're not buffering the whole file to avoid consuming RAM.
#              Added this header/documentation and some comments in code.
#
#     Version: v0.01.00 beta
#  Updated by: Tele Charalambous
#        Date: 2019-03-05
#       Notes: Converted from Bash to Python for cross-compatibility with
#              Windows, Linux, etc. Previously built on CygWin but not
#              everyone has that installed. Python is easier to install
#              and maintain on Windows. Script is easier to read.
#
###############################################################################


# Define Global variables
# Timestamp() replacement counter, Reg-ex string definition, Table list array
TSCount = 0
TStamps = {"timestamp(6)": "timestamp", "TIMESTAMP(6)": "TIMESTAMP"}
TblList = {}
FormatFlag = True


# Function to create the reg-ex to remove the '(6)' from timestamp definitions.
# Used this string to maintain CaSe in SQL file
def TimeStamp_replace(text):
    global TSCount
    # Create a regular expression from all of the dictionary keys
    regex = re.compile("|".join(map(re.escape, TStamps.keys())))
    TSCount += 1
    # For each match, look up the corresponding value in the dictionary
    return regex.sub(lambda match: TStamps[match.group(0)], text)


# Display basic usage if no parameters or error occurs.
def Usage():
    print "\n\nUsage: ProcessSQL.py [InFile] [OutFile] [TableName] ...\n"
    print "      with just InFile     - List top 10 tables by INSERT count."
    print "\n"
    print "      with In/Out files    - Create OutFile with readable SQL.\n"
    print "      with --NoReformat    - Disable reformat to readable INSERTs"
    print "                             Currently must be given as 3rd param\n"
    print "      with TableName(s) to exclude"
    print "                           - Create OutFile as above & exclude"
    print "                             INSERT statements of those tables."
    print "\n\n"
    return


# Simple Error Handler, instead of duplicating the same strings/actions
def ThrowError(errorStr):
    print "\nERROR: " + errorStr
    print "\nTerminating Process.\n"
    exit(1)
    return


# No Args Given
if len(sys.argv) == 1:
    Usage()
    exit(1)

# Start banner here...
print "\nStarting ProcessSQL.py - " + Version

# At least InFileName was given
if len(sys.argv) == 2:
    InFileName = sys.argv[1]
    if not os.path.isfile(InFileName):
        ThrowError("File \"" + InFileName + "\" not found.")
    else:
        print "\nProcessing: " + InFileName + "\n"
        with open(InFileName, "r") as InFile:
            for myLine in InFile:
                if myLine[:12] == "INSERT INTO ":
                    myFields = myLine.strip().split()
                    TblName = myFields[2]
                    if (TblName in TblList):
                        TblList[TblName] += 1
                    else:
                        TblList[TblName] = 1
        print "\tCount\tTableName"
        print "\t-----\t---------"
        for myCount in sorted(TblList, key=TblList.get, reverse=True)[:10]:
            print "\t" + str(TblList[myCount]) + "\t" + myCount


# At least InFileName and OutFileName were specified
if len(sys.argv) >= 3:
    InFileName = sys.argv[1]
    OutFileName = sys.argv[2]
    if not os.path.isfile(InFileName):
        ThrowError("File \"" + InFileName + "\" not found.")
    else:
        if InFileName == OutFileName:
            ThrowError("Input and Output cannot be the same file.")
        else:
            print "\nProcessing Input File: " + InFileName
            sys.stdout.write("          Output File: " + OutFileName)
            if os.path.isfile(OutFileName):
                sys.stdout.write(" (will be overwritten)\n")
            else:
                sys.stdout.write("\n")
            sys.stdout.flush()
            # Now will also check if table names followed...
            FoundTbls = []
            if len(sys.argv) >= 4:
                if sys.argv[3] == "--NoReformat":
                    print "Reformatting of SQL disabled"
                    FormatFlag = False
                    TblList = sys.argv[4:]
                else:
                    print "Reformatting of SQL enabled (default)"
                    TblList = sys.argv[3:]
                    FormatFlag = True  # Make no assumptions
                sys.stdout.write("\nTables requested to exclude: ")
                print(', '.join(TblList))
            with open(OutFileName, "w") as OutFile:
                with open(InFileName, "r") as InFile:
                    for myLine in InFile:
                        if "timestamp(6)" in myLine.lower():
                            myLine = TimeStamp_replace(myLine)
                        if myLine[:12] == "INSERT INTO ":
                            myFields = myLine.strip().split()
                            TblName = myFields[2].replace("`", "")
                            if TblName in TblList:
                                if TblName not in FoundTbls:
                                    # Confirm we found tables & excluded them
                                    print "   Excluded INSERTS for: " + TblName
                                    FoundTbls.append(TblName)
                            else:
                                if FormatFlag is True:
                                   OutFile.write(re.sub(r"\),\(","),\n\t(",myLine))
                                else:
                                    OutFile.write(myLine)
                        else:
                            OutFile.write(myLine)

# Give some final stats and finish
if TSCount > 0:
    print "\nLines with TIMESTAMP(6) modified: " + str(TSCount)
print "\nDone.\n"
