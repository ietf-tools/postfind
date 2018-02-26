Find postfix log-entries related to a given Message-ID
======================================================

Postfind takes an email Message-ID and one or more postfix log file names as
input, and searches the logs for mentions of the given Message-ID.  If found,
related log entries are followed as well, until terminated by finding a
queue-id 'removed' entry, the end of the log files, or a timeout (if following
a log file).

