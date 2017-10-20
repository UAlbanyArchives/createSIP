import os
import json
import datetime

def pp(stuff):
	print (json.dumps(stuff, indent=2))

directory = {}
testDir = "\\\\romeo\\SPE\\bagTesting\\ua200"


def readDir (metadata, object):
	metadata["name"] = os.path.basename(object)
	path = os.path.abspath(object)
	if os.name == "nt":
		path = path.decode("mbcs")
	else:
		path = path.decode("utf8")
	metadata["path"] = path
	if os.path.isfile(object):
		metadata["type"] = "file"
		metadata["extension"] = os.path.splitext(object)[1]
		timestamps = {}
		(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)
		timestamps["atime"] = str(atime)
		timestamps["mtime"] = str(mtime)
		timestamps["ctime"] = str(ctime)
		timestamps["atimeHuman"] = str(datetime.datetime.fromtimestamp(int(atime)).strftime('%Y-%m-%d %H:%M:%S'))
		timestamps["mtimeHuman"] = str(datetime.datetime.fromtimestamp(int(mtime)).strftime('%Y-%m-%d %H:%M:%S'))
		timestamps["ctimeHuman"] = str(datetime.datetime.fromtimestamp(int(ctime)).strftime('%Y-%m-%d %H:%M:%S'))
		timestamps["os"] = str(os.name)
		timestamps["timeFormat"] = "posix"
		timestamps["timeParser"] = "os.stat"
		if os.name == "nt":
			timestamps["timeType"] = "STANDARD_INFORMATION"
		metadata["timestamps"] = timestamps

	elif os.path.isdir(object):
		metadata["type"] = "folder"
		timestamps = {}
		atime = os.path.getatime(path)
		mtime = os.path.getmtime(path)
		ctime = os.path.getctime(path)
		timestamps["atime"] = atime
		timestamps["mtime"] = mtime
		timestamps["ctime"] = ctime
		timestamps["atimeHuman"] = str(datetime.datetime.fromtimestamp(int(atime)).strftime('%Y-%m-%d %H:%M:%S'))
		timestamps["mtimeHuman"] = str(datetime.datetime.fromtimestamp(int(mtime)).strftime('%Y-%m-%d %H:%M:%S'))
		timestamps["ctimeHuman"] = str(datetime.datetime.fromtimestamp(int(ctime)).strftime('%Y-%m-%d %H:%M:%S'))
		timestamps["os"] = str(os.name)
		timestamps["timeFormat"] = "posix"
		timestamps["timeParser"] = "os.stat"
		if os.name == "nt":
			timestamps["timeType"] = "STANDARD_INFORMATION"
		metadata["timestamps"] = timestamps
		metadata["children"] = []
		for child in os.listdir(object):
			childObject = readDir({}, os.path.join(object, child))
			metadata["children"].append(childObject)
		
	return metadata
	
directory = readDir(directory, testDir)

pp(directory)