from datetime import datetime
import eXLib

# Release build: on-disk debug logging is DISABLED.
# DebugPrint/DebugPrintNT used to append to Log.txt and DumpObject wrote ObjectDump.txt
# in the client root. They are kept as no-ops so the many call sites across the bot keep
# working without generating files. To get debug logs back, restore the open()/write()
# bodies (and the import-time Log.txt truncate that used to live at the bottom).

def DebugPrint(arg):
	pass

def DebugPrintNT(arg):
	pass

def DumpObject(arg):
	pass

def handleRequest(id,msg):
	DebugPrint(msg)
