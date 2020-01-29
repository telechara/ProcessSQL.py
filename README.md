# ProcessSQL.py
SQL dump processing script
###############################################################################
#
#   Name: ProcessSQL.py
# Author: Tele C
#
# Description:
#   The goal of this script is to be able to investigate/import multiple
#   databases into one MySQL server by omitting data which is not required
#   e.g. history, logging, debug tables.
#
#   This script processes, reformats and reduces the MySQL database dump size
#   for importing MySQL server. It lists the top 10 largest tables by counting the
#   INSERT statements. E.g. some databases have huge tables which can be
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
#  Version = "v1.02.01"
#  Updated by: Tele
#        Date: 2019-08-16
#       Notes: Fixed syntax to be PEP-08 compliant (except for one line)
#
#  *** Previous Changes ***
#  Updated by: Tele
#        Date: 2019-05-31
#       Notes: Fixed some filenames vs file handles. Created backward
#              compatible version ye olde Python 2.4.3
#
#  Updated by: Tele
#        Date: 2019-05-15
#       Notes: Reworded help message to say 'tables to exclude' & added usage
#
#     Version: v1.00.00
#  Updated by: Tele
#        Date: 2019-04-12
#       Notes: Will overwrite an existing destination file with a warning but
#              without asking. Code has no current known issues if args are
#              observed correctly. Large SQL files obviously take longer, but
#              we're not buffering the whole file to avoid consuming RAM.
#              Added this header/documentation and some comments in code.
#
#     Version: v0.01.00 beta
#  Updated by: Tele
#        Date: 2019-03-05
#       Notes: Converted from Bash to Python for cross-compatibility with
#              Windows, Linux, etc. Previously built on CygWin but not
#              everyone has that installed. Python is easier to install
#              and maintain on Windows. Script is easier to read.
#
###############################################################################
