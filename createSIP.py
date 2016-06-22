import argparse
import os
import shutil
from lxml import etree as ET
import uuid
import traceback
import zipfile
import time
import hashlib
import bagit
import datetime
from openpyxl import load_workbook
from operator import itemgetter

#hash function
#from http://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.digest()


#version of createSIP.py
version = "0.1"
#preservation directory
if os.name == "nt":
	presDir = "\\\\LINCOLN\\Masters\\Special Collections\\accessions"
else:
	presDir = "/media/bcadmin/Lincoln/Special Collections/accessions"
	
argParse = argparse.ArgumentParser()
argParse.add_argument("path", help="Path of data you want to accession.")
argParse.add_argument("-m", help="Use previously created metadata XML instead of filesystem data.")
argParse.add_argument("-b", help="Validate bag with bagit-python after created.", action="store_true")
argParse.add_argument("-v", help="Increase output verbosity.", action="store_true")
args = argParse.parse_args()

try:
	print args.path
	if not os.path.isdir(args.path):
		raise ValueError("Invalid Directory")

	if args.v:
	    print "Creating SIP from " + args.path

	rootPath = os.path.abspath(os.path.join(args.path, os.pardir))
	submitTime = time.time()
	submitTimeReadable = str(time.strftime("%Y-%m-%d %H:%M:%S"))

	if os.name == "nt":
		pathDelimiter = "\\"
	else:
		pathDelimiter = "/"
		
	#if flag for premade metadata file
	if args.m:
		if args.v:
			print "Using metadata file " + args.m
		parser = ET.XMLParser(remove_blank_text=True)
		metaInput = ET.parse(args.m, parser)
		meta = metaInput.getroot()

		#get SIP metadata from premade metadata XML file
		collectionID = meta.find("profile/creatorID").text
		donor = meta.find("profile/donor").text
		transferMethod = meta.find("profile/method").text
		transferLocation = meta.find("profile/location").text
		creator = meta.find("profile/creator").text
		role = meta.find("profile/role").text
		contactEmail = meta.find("profile/email").text
		office = meta.find("profile/office").text
		address1 = meta.find("profile/address1").text
		address2 = meta.find("profile/address2").text
		address3 = meta.find("profile/address3").text
		archivistNotes = meta.find("profile/notes").text
		accessConcerns = meta.find("folder/access").text
		description = meta[1].find("description").text

		submitTime = meta.attrib["submittedPosix"]
		submitTimeReadable = meta.attrib["submitted"]
		accessionNumber = meta.attrib["number"]
		
		#add curatorial event to pre-made metadata file
		bagEvent = ET.Element("event")
		bagEvent.set("timestamp", str(time.time()))
		bagEvent.set("humanTime", str(time.strftime("%Y-%m-%d %H:%M:%S")))
		bagEvent.text = "Submission Information Package (SIP) created with createSIP.py version " + version
		meta[1].find("curatorialEvents").append(bagEvent)
		metaString = ET.tostring(meta, pretty_print=True)
		file = open(args.m, "w")
		file.write(metaString)
		file.close()

	else:
		if args.v:
			print "Please enter metadata for this accession:"


		def getInput(collectionID, donor, description, accessConcerns, transferMethod, transferLocation, creator, role, contactEmail, office, address1, address2, address3, archivistNotes):
			collectionID = raw_input("Collection ID[" + collectionID + "]: ") or collectionID
			donor = raw_input("Donor[" + donor + "]: ") or donor

			description = raw_input("Describe the accession:[" + description + "]: ") or description
			accessConcerns = raw_input("Any access concerns?[" + accessConcerns + "]: ") or accessConcerns
			transferMethod = raw_input("Method of Transfer[" + transferMethod + "]: ") or transferMethod
			transferLocation = raw_input("Transfer Location[" + transferLocation + "]: ") or transferLocation
			creator = raw_input("Records Creator[" + creator + "]: ") or creator
			role = raw_input("Role of " + donor + "[" + role + "]: ") or role
			contactEmail = raw_input("Contact Email[" + contactEmail + "]: ") or contactEmail
			office = raw_input("Contact Office[" + office + "]: ") or office
			address1 = raw_input("Contact Address Line 1[" + address1 + "]: ") or address1
			address2 = raw_input("Contact Address Line 2[" + address2 + "]: ") or address2
			address3 = raw_input("Contact Address Line 3[" + address3 + "]: ") or address3
			archivistNotes = raw_input("Any accession notes?[" + archivistNotes + "]: ") or archivistNotes
			
			#Check if data entered is correct:
			print "########################################"
			print "Is this correct?"
			print "########################################"
			print "Collection ID: " + collectionID
			print "Donor: " + donor
			print "Description: " + description
			print "Access Concerns: " + accessConcerns
			print "Method of Transfer: " + transferMethod
			print "Transfer Location: " + transferLocation
			print "Records Creator: " + creator
			print "Role of " + donor + ": " + role
			print "Contact Email: " + contactEmail
			print "Contact Office: " + office
			print "Contact Address Line 1: " + address1
			print "Contact Address Line 2: " + address2
			print "Contact Address Line 3: " + address3
			print "Accession Notes: " + archivistNotes

			entryCorrect = raw_input("Is this correct? (Y or N): ")
			if not entryCorrect.lower() == "y" or entryCorrect.lower() == "yes":
				collectionID, donor, description, accessConcerns, transferMethod, transferLocation, creator, role, contactEmail, office, address1, address2, address3, archivistNotes = getInput(collectionID, donor, description, accessConcerns, transferMethod, transferLocation, creator, role, contactEmail, office, address1, address2, address3, archivistNotes)
			else:
				return collectionID, donor, description, accessConcerns, transferMethod, transferLocation, creator, role, contactEmail, office, address1, address2, address3, archivistNotes


		
		#get SIP metadata from processor input
		#this is the default metadata
		collectionID = ""
		donor = ""
		description = ""
		accessConcerns = ""
		transferMethod = ""
		transferLocation = rootPath
		creator = ""
		role = ""
		contactEmail = ""
		office = ""
		address1 = ""
		address2 = ""
		address3 = ""
		archivistNotes = ""
		collectionID, donor, description, accessConcerns, transferMethod, transferLocation, creator, role, contactEmail, office, address1, address2, address3, archivistNotes, = getInput(collectionID, donor, description, accessConcerns, transferMethod, transferLocation, creator, role, contactEmail, office, address1, address2, address3, archivistNotes)
		accessionNumber = collectionID + "-" + str(uuid.uuid4())

	#get size of accession
	#from here: http://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python
	def get_size(start_path = '.'):
		total_size = 0
		for dirpath, dirnames, filenames in os.walk(start_path):
			for f in filenames:
				fp = os.path.join(dirpath, f)
				total_size += os.path.getsize(fp)
		return total_size
	sipSize = get_size(args.path)
	#make Human-readable
	#from here: http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
	from math import log
	unit_list = zip(['bytes', 'KB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])
	def sizeof_fmt(num):
		"""Human friendly file size"""
		if num > 1:
			exponent = min(int(log(num, 1024)), len(unit_list) - 1)
			quotient = float(num) / 1024**exponent
			unit, num_decimals = unit_list[exponent]
			format_string = '{:.%sf} {}' % (num_decimals)
			return format_string.format(quotient, unit)
		if num == 0:
			return '0 bytes'
		if num == 1:
			return '1 byte'
	sipSizeHR = sizeof_fmt(sipSize)
	
	#prepare bag
	accessionPath = os.path.join(rootPath, accessionNumber)
	os.mkdir(accessionPath)
	os.mkdir(os.path.join(accessionPath, "data"))	
	
	#move or create metadata file
	if args.m:
		if args.v:
			print "Moving metadata file to bag."
		shutil.move(args.m, accessionPath)
	else:
		if args.v:
			print "Creating metadata file."
	    #create sipXML root
		sipRoot = ET.Element("accession")
		sipRoot.set("version", version)
		sipRoot.set("number", accessionNumber)
		sipRoot.set("submitted", submitTimeReadable)
		sipRoot.set("submittedPosix", str(submitTime))

		#create profile
		profileXML = ET.SubElement(sipRoot, "profile")
		notesXML = ET.SubElement(profileXML, "notes")
		notesXML.text = archivistNotes
		creatorXML = ET.SubElement(profileXML, "creator")
		creatorXML.text = creator
		creatorIdXML = ET.SubElement(profileXML, "creatorId")
		creatorIdXML.text = collectionID
		donorXML = ET.SubElement(profileXML, "donor")
		donorXML.text = donor
		roleXML = ET.SubElement(profileXML, "role")
		roleXML.text = role
		emailXML = ET.SubElement(profileXML, "email")
		emailXML.text = contactEmail
		officeXML = ET.SubElement(profileXML, "office")
		officeXML.text = office
		address1XML = ET.SubElement(profileXML, "address1")
		address1XML.text = address1
		address2XML = ET.SubElement(profileXML, "address2")
		address2XML.text = address2
		address3XML = ET.SubElement(profileXML, "address3")
		address3XML.text = address3
		methodXML = ET.SubElement(profileXML, "method")
		methodXML.text = transferMethod
		locationXML = ET.SubElement(profileXML, "location")
		locationXML.text = transferLocation
		extentXML = ET.SubElement(profileXML, "extent")
		extentXML.set("unit", "bytes")
		extentXML.text = str(sipSize)
		extentXML.set("humanReadable", sipSizeHR)
		
		#create content metadata
		#create metadata record
		def makeRecord(path):
			if os.path.isdir(path):
				record = ET.Element("folder")
				atime = os.path.getatime(path)
				mtime = os.path.getmtime(path)
				ctime = os.path.getctime(path)
			else:
				record = ET.Element("file")
				(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)
			record.set("name", os.path.basename(path))
			idXML = ET.SubElement(record, "id")
			idXML.text = str(uuid.uuid4())
			pathXML = ET.SubElement(record, "path")
			pathXML.text = path
			descriptionXML = ET.SubElement(record, "description")
			accessXML = ET.SubElement(record, "access")
			curatorialEventsXML = ET.SubElement(record, "curatorialEvents")
			recordEventsXML = ET.SubElement(record, "recordEvents")
			#recordEvents
			atimeXML = ET.SubElement(recordEventsXML, "timestamp")
			atimeXML.text = str(atime)
			atimeXML.set("os", os.name)
			atimeXML.set("timeType", "posix")
			atimeXML.set("parser", "os.stat")
			if os.name == "nt":
				atimeXML.set("type", "STANDARD_INFORMATION")
			atimeXML.set("label", "atime")
			atimeXML.set("humanTime", datetime.datetime.fromtimestamp(int(atime)).strftime('%Y-%m-%d %H:%M:%S'))
			mtimeXML = ET.SubElement(recordEventsXML, "timestamp")
			mtimeXML.text = str(mtime)
			mtimeXML.set("os", os.name)
			mtimeXML.set("timeType", "posix")
			mtimeXML.set("parser", "os.stat")
			if os.name == "nt":
				mtimeXML.set("type", "STANDARD_INFORMATION")
			mtimeXML.set("label", "mtime")
			mtimeXML.set("humanTime", datetime.datetime.fromtimestamp(int(mtime)).strftime('%Y-%m-%d %H:%M:%S'))
			ctimeXML = ET.SubElement(recordEventsXML, "timestamp")
			ctimeXML.text = str(ctime)
			ctimeXML.set("os", os.name)
			ctimeXML.set("timeType", "posix")
			ctimeXML.set("parser", "os.stat")
			if os.name == "nt":
				ctimeXML.set("type", "STANDARD_INFORMATION")
			ctimeXML.set("label", "ctime")
			ctimeXML.set("humanTime", datetime.datetime.fromtimestamp(int(ctime)).strftime('%Y-%m-%d %H:%M:%S'))
			eventOsStat = ET.Element("event")
			eventOsStat.set("timestamp", str(time.time()))
			eventOsStat.set("humanTime", str(time.strftime("%Y-%m-%d %H:%M:%S")))
			eventOsStat.text = "ran os.stat to gather timestamps"
			curatorialEventsXML.append(eventOsStat)
			
			return record
		
		#loop thorugh directory and create records
		def loopAccession(path, root):
			if os.path.isdir(path):
				record = makeRecord(path)
				root.append(record)
				for item in os.listdir(path):
					root = loopAccession(os.path.join(path, item), record)
			else:
				root.append(makeRecord(path))
			return root
		sipRoot.append(loopAccession(args.path, sipRoot))
		bagEvent = ET.Element("event")
		bagEvent.set("timestamp", str(time.time()))
		bagEvent.set("humanTime", str(time.strftime("%Y-%m-%d %H:%M:%S")))
		bagEvent.text = "Submission Information Package (SIP) created with createSIP.py version " + version	
		if len(accessConcerns) > 0:
			sipRoot[1].find("access").text = accessConcerns
		if len(description) > 0:
			sipRoot[1].find("description").text = description
		if len(transferMethod) > 0:
			transferEvent = ET.Element("event")
			transferEvent.set("timestamp", "")
			transferEvent.set("humanTime", "")
			transferEvent.text = transferMethod
			sipRoot[1].find("curatorialEvents").insert(0, transferEvent)
			sipRoot[1].find("curatorialEvents").insert(1, bagEvent)
		else:
			sipRoot[1].find("curatorialEvents").insert(0, bagEvent)
		
		#serializing metadata file
		outputMeta = os.path.join(accessionPath, accessionNumber + ".xml")
		XMLString = ET.tostring(sipRoot, pretty_print=True)
		file = open(outputMeta, "w")
		file.write(XMLString)
		file.close()
	
	#create accession record
	accessionFile = os.path.join(presDir, "accessions.xlsx")
	accessionsWorkbook = load_workbook(accessionFile, False)
	accessions = accessionsWorkbook.get_sheet_by_name('accessions')
	if sipRoot[1].find("description").text is None:
		accessDesc = ""
	else:
		accessDesc = sipRoot[1].find("description").text
	if sipRoot[1].find("access").text is None:
		restrictSwitch = "False"
		accessRestrict = ""
	else:
		restrictSwitch = "True"
		accessRestrict = sipRoot[1].find("access").text
	accessions.append([accessionNumber, submitTimeReadable.split(" ")[0], creator + "; Transfer: " + transferMethod, accessDesc, str(sipSize), restrictSwitch, accessRestrict, "", "", archivistNotes])
	accessionsWorkbook.save(accessionFile)
	
	#move data into bag
	if args.v:
	    print "Moving data into bag"
	shutil.move(args.path, os.path.join(accessionPath, "data"))

	#create manifest and get Payload-Oxum
	if args.v:
	    print "Creating bag manifest and getting Payload-Oxum"
	octetCount = 0
	streamCount = 0
	manifestList = []
	for root, dirs, files in os.walk(os.path.join(accessionPath, "data")):
		streamCount += len(files)
		for f in files:
			fp = os.path.join(root, f)
			md5 = str(hashlib.md5(open(fp, 'rb').read()).hexdigest())
			manifestList.append(md5 + "  " + fp.split(accessionPath + pathDelimiter)[1])
			octetCount += os.path.getsize(fp)
	manifest = open(os.path.join(accessionPath, "manifest-md5.txt"), "w")
	for manLine in manifestList:
		manifest.write("%s\n" % manLine)
	manifest.close()

	
	#create bag metadata files
	if args.v:
	    print "Creating bag metadata files"
	#bag-into.txt
	bagInfo = open(os.path.join(accessionPath, "bag-info.txt"), "w")
	bagInfoText = "Bag-Software-Agent: createSIP.py <http://github.com/UAlbanyArchives/createSIP>"
	bagInfoText = bagInfoText + "\nBagging-Date: " + str(time.strftime("%Y-%m-%d"))
	bagInfoText = bagInfoText + "\nPayload-Oxum: " + str(octetCount) + "." + str(streamCount)
	bagInfoText = bagInfoText + "\naccession: " + accessionNumber
	if len(creator) > 0:
		bagInfoText = bagInfoText + "\ncreator: " + creator
	bagInfoText = bagInfoText + "\ncreatorId: " + collectionID
	if len(donor) > 0:
		bagInfoText = bagInfoText + "\ndonor: " + donor
	if len(transferLocation) > 0:
		bagInfoText = bagInfoText + "\nlocation: " + transferLocation
	if len(transferMethod) > 0:
		bagInfoText = bagInfoText + "\nmethod: " + transferMethod
	if len(role) > 0:
		bagInfoText = bagInfoText + "\nrole: " + role
	bagInfoText = bagInfoText + "\nsubmitted: " + submitTimeReadable
	bagInfoText = bagInfoText + "\nsubmittedPosix: " + str(submitTime)
	bagInfo.write(bagInfoText)
	bagInfo.close()

	#bagit.txt
	bagitFile = open(os.path.join(accessionPath, "bagit.txt"), "w")
	bagitText = "BagIt-Version: 0.97\nTag-File-Character-Encoding: UTF-8"
	bagitFile.write(bagitText)
	bagitFile.close()

	#tagmanifest-md5.txt
	tagManifest = open(os.path.join(accessionPath, "tagmanifest-md5.txt"), "w")
	for metaFile in os.listdir(accessionPath):
		if os.path.isfile(os.path.join(accessionPath, metaFile)):
			if not metaFile == "tagmanifest-md5.txt":
				tagmd5 = str(hashlib.md5(open(os.path.join(accessionPath, metaFile), 'rb').read()).hexdigest())
				tagManLine = tagmd5 + "  " + metaFile
				tagManifest.write("%s\n" % tagManLine)
	tagManifest.close()

	#validate bag
	if args.b:
		if args.v:
		    print "Validating bag"
		bag = bagit.Bag(accessionPath)
		if not bag.is_valid():
			print "invalid bag"
			raise ValueError("Bag failed to validate with bagit-python")
		else:
			if args.v:
				print "Bag is valid"

	#compress bag
	if args.v:
	    print "Compressing bag"
	shutil.make_archive(accessionPath, "zip", accessionPath)
	shutil.rmtree(accessionPath)
	
	#move bag to storage
	shutil.copy2(accessionPath + ".zip", os.path.join(presDir, "SIP"))
	os.remove(accessionPath + ".zip")

except:
	exceptMsg = str(traceback.format_exc())
	print exceptMsg