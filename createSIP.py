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

#hash function
#from http://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.digest()



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

		submitTime = meta.attrib["submittedPosix"]
		submitTimeReadable = meta.attrib["submitted"]
		accessionNumber = meta.attrib["number"]

	else:
		if args.v:
			print "Please enter metadata for this accession:"


		def getInput(collectionID, donor, transferMethod, transferLocation, creator, role, contactEmail, office, address1, address2, address3, archivistNotes, accessConcerns):
			collectionID = raw_input("Collection ID[" + collectionID + "]: ") or collectionID
			donor = raw_input("Donor[" + donor + "]: ") or donor

			accessConcerns = raw_input("Any access concerns?[" + accessConcerns + "]: ") or accessConcerns
			transferMethod = raw_input("Method of Transfer[" + transferMethod + "]: ") or transferMethod
			transferLocation = raw_input("SIP Destination[" + transferLocation + "]: ") or transferLocation
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
			print "Access Concerns: " + accessConcerns
			print "Method of Transfer: " + transferMethod
			print "Donor: " + transferLocation
			print "SIP Destination: " + transferLocation
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
				collectionID, donor, transferMethod, transferLocation, creator, role, contactEmail, office, address1, address2, address3, archivistNotes, accessConcerns = getInput(collectionID, donor, transferMethod, transferLocation, creator, role, contactEmail, office, address1, address2, address3, archivistNotes, accessConcerns)
			else:
				return collectionID, donor, transferMethod, transferLocation, creator, role, contactEmail, office, address1, address2, address3, archivistNotes, accessConcerns


		
		#get SIP metadata from processor input
		collectionID = ""
		donor = "Gregory Wiedeman"
		transferMethod = ""
		transferLocation = rootPath
		creator = ""
		role = "Archivist"
		contactEmail = ""
		office = ""
		address1 = ""
		address2 = ""
		address3 = ""
		archivistNotes = ""
		accessConcerns = ""
		collectionID, donor, transferMethod, transferLocation, creator, role, contactEmail, office, address1, address2, address3, archivistNotes, accessConcerns = getInput(collectionID, donor, transferMethod, transferLocation, creator, role, contactEmail, office, address1, address2, address3, archivistNotes, accessConcerns)
		accessionNumber = collectionID + str(uuid.uuid4())

	#move data into bag
	if args.v:
	    print "Moving data into bag"
	accessionPath = os.path.join(rootPath, accessionNumber)
	os.mkdir(accessionPath)
	os.mkdir(os.path.join(accessionPath, "data"))
	shutil.move(args.path, os.path.join(accessionPath, "data"))

	#move or create metadata file
	if args.m:
		if args.v:
			print "Moving metadata file to bag."
		shutil.move(args.b, accessionPath)
	else:
		if args.v:
			print "Creating metadata file."
	    #create sipXML root
		sipRoot = ET.Element("accession")
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

		#serializing metadata file
		outputMeta = os.path.join(accessionPath, accessionNumber + ".xml")
		XMLString = ET.tostring(sipRoot, pretty_print=True)
		file = open(outputMeta, "w")
		file.write(XMLString)
		file.close()

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
			manifestList.append(md5 + "  " + fp.split(accessionPath + "/")[1])
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

except:
	exceptMsg = str(traceback.format_exc())
	print exceptMsg