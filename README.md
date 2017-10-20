# createSIP
UAlbany command line utility for baging files and creating accession records in ArchivesSpace. Version 0.2 is incomplete.

## Getting Started

### Prerequisites

* Python 2.7 or Python 3
* ArchivesSpace and API access
* [The UAlbany experimental aspace library](https://github.com/UAlbanyArchives/archives_tools)
	* Will hopefully be replaced by the [ArchivesSnake project](https://github.com/archivesspace-labs/ArchivesSnake)
* [Bagit-python](https://github.com/LibraryOfCongress/bagit-python)
* [Bagit-Profiles](https://github.com/ruebot/bagit-profiles)


### Installing

* First you need to clone the `aspace` library repo, install it

		git clone https://github.com/UAlbanyArchives/archives_tools
		cd archives_tools
		python setup.py install

* Using the Python prompt, enter your ArchivesSpace credentials

		python	
		>from archives_tools import aspace as AS
		>AS.setURL("http://localhost:8089")
		>AS.setUser("admin")
		>AS.setPassword("admin")
		>exit()

* Next you need to clone and install createSIP

		git clone https://github.com/UAlbanyArchives/createSIP
		cd createSIP
		python setup.py install


## Using createSIP
		
		usage: createSIP.py [-h] [-m M] [-b] [-z] [-v] path output
		
		positional arguments:
		  path        Path of data you want to accession.
		  output      Directory where the bag will be made.
		
		optional arguments:
		  -h, --help  show this help message and exit
		  -m M        Use previously created metadata file instead of filesystem data.
		  -b          Validate bag with bagit-python after created.
		  -z          Compress bag to zip.
		  -v          Increase output verbosity.


## UAlbany Bagit Spec

[UAlbany Bagit Profile Spec](bag-profile-v0.1.json) Version 0.1 (2017-10-19)

* This documents the UAlbany bagit specification for transferring digital files. It uses [Bagit-Profiles](https://github.com/ruebot/bagit-profiles).
* Bags are usually created during periodic automated crawls of designated directories on university file shares where campus offices place permanent records in accordance with the [SUNY Retention Schedule](http://system.suny.edu/compliance/topics/records/records-retention/).

### UAlbany Bag stucture

		collectionID-tranferUUID/
			| bagit.txt
			| bag-info.txt
			| manifest-md5.txt
			| manifest-sha256.txt
			| metadata.json
			| tagmanifest-md5.txt
			\--- data/
				| [payload]

* The collectionID is a UAlbany collection number, like apap101, mss127, or ua500
* Transfer UUIDs are created with [shortuuid](https://pypi.python.org/pypi/shortuuid)
* These files are included as part of the [bagit spec](https://tools.ietf.org/html/draft-kunze-bagit-08)
	* bagit.txt
	* bag-info.txt
	* manifest-md5.txt
	* manifest-sha256.txt
	* tagmanifest-md5.txt
* metadata.json includes metadata, like filenames and timestamps, extracted from the filesystem before bagging


## Bag-Info Field Specifications

### Records-Creator
* **Definition:** Transferring office or department
* **Purpose:**  to define the organization that that created and used the records
* **Data type:** string
* **Obligation:** Required
* **Repeatability:** No
* **Examples:**
    * "Office of the President"
    * "Office of Academic Affairs and Provost"
    * "University Senate"
    * "Department of Digital Media"

### Creator-Identifier
* **Definition:** a repository-unique code for the organization that that created and used the records
* **Purpose:** Allows for making connections across multiple systems to a common creator
* **Data type:** string
* **Obligation:** Required
* **Repeatability:** No
* **Examples:**
	* apap313
	* ger107
	* mss005
	* ua300
	* ua902.011

### Transfer-Identifier
* **Definition:** A universally unique identifier created using the Python shortuuid library. Consists of the Creator-Identifier followed by a dash (-) and then the shortuuid.
* **Purpose:** for defining and maintaining a transfer over time
* **Data type:** string
* **Obligation:** Required
* **Repeatability:** No
* **Examples:**
	* ua500-7VsAhYXbfYg3EKXaypCJeD
	* ua809.001-Xakcp2JEs5fRo3DsSxpnNF

### Donor-Description
* **Definition:** A description of the records provided by the donor
* **Purpose:** To allow for additional prose description and exceptional cases
* **Data type:** text
* **Obligation:** Optional
* **Repeatability:** No

### Records-Donor
* **Definition:** The person who initiated the transfer of the records.
* **Purpose:** To provide context for the transfer
* **Data type:** string
* **Obligation:** Required
* **Repeatability:** No

### Donor-Contact
* **Definition:** a point of contact for the person who initiated the transferof the records, such as an email address, office number, physical address or phone number.
* **Purpose:** To enable communication between a donor and the repository.
* **Data type:** string
* **Obligation:** Optional
* **Repeatability:** yes

### Source-Location
* **Definition:** a filesystem path or system description that housed the records before transfer
* **Purpose:** Provides context by informing archivists and users about the immediate source location of the records.
* **Data type:** string
* **Obligation:** Required
* **Repeatability:** No
* **Examples:**
	* \\LINCOLN\Library\UA200
	* SmugMug API

### Transfer-Method
* **Definition:** a description of the method, usually an automated tool with a version
* **Purpose:** Provides context by informing archivists and users of how the records were transferred
* **Data type:** string
* **Obligation:** Required
* **Repeatability:** No
* **Examples:**
	* createSIP.py v0.2
	* ua200.py v0.1


### Transfer-Extent
* **Definition:** A human readable extent of the transfer
* **Purpose:** defines the size the the transfer in a way that is easily interpreted by humans
* **Data type:** string
* **Obligation:** Required
* **Repeatability:** No
* **Examples:**
	* 172.1 MB
	* 2.34 GB

### Bagging-Date
* **Definition:** ISO 8601 timestamp recorded at the point of transfer
* **Purpose:** Provides context and informs archivists and users the time in which the records were transfered
* **Data type:** date
* **Obligation:** Required
* **Repeatability:** No
* **Examples:**
	* 2017-08-02 13:36:29

### Posix-Date
* **Definition:** Posix timestamp recorded at the point of transfer
* **Purpose:** Documents the time of transfer a standard and timezone-independent way. Posix-Date is intended for machine consumption.
* **Data type:** integer
* **Obligation:** Required
* **Repeatability:** No
* **Examples:**
	* 1501695389.99

### Payload-Oxum
* **Definition:** The "octetstream sum" of the payload, namely, a two-part number of the form OctetCount.StreamCount, where OctetCount is the total number of octets (8-bit bytes) across all payload file content and StreamCount is the total number of payload files. Payload-Oxum should be included in bag-info.txt if at all possible. 
* **Purpose:** Payload-Oxum is intended for machine consumption. Defined the extent of the transfer
* **Data type:** OctetCount.StreamCount
* **Obligation:** Required
* **Repeatability:** No
* **Examples:**
	* 180470342.160

### BagIt-Profile-Identifier
* **Definition:** A URI that defines, this URI is not permanent at this time. 
* **Purpose:** Required to validated bags with the [Bagit-Progiles-Validator](https://github.com/ruebot/bagit-profiles-validator)
* **Data type:** string
* **Obligation:** Required
* **Repeatability:** No
* **Examples:**
	* http://library.albany.edu/speccoll/findaids/eresources/standards/bagit/bag-profile-v0.1.json


## The metadata.json file

This is an additional file required in all UAlbany bags that documents all of the metadata that could have easily extracted from the original filesystem prior to transfer.

**Sample folder model:**
		
		{
		  "path": "\\\\romeo\\SPE\\bagTesting\\ua200\\Subject Files (misc)",
		  "children": [...],
		  "type": "folder",
		  "name": "Subject Files (misc)",
		  "timestamps": {
		    "atimeHuman": "2017-10-19 12:29:34",
		    "ctime": 1508430574.08275,
		    "mtimeHuman": "2017-08-02 13:36:25",
		    "timeParser": "os.stat",
		    "timeType": "STANDARD_INFORMATION",
		    "mtime": 1501695385.752937,
		    "timeFormat": "posix",
		    "ctimeHuman": "2017-10-19 12:29:34",
		    "atime": 1508430574.08275,
			"os": "nt"
		  }
		}

**Sample file model:**

		{
		  "path": "\\romeo\SPE\bagTesting\ua200\Membership Lists\Histories by year\Senate Council History to 201617.xls",
		  "type": "file",
		  "name": "Senate Council History to 201617.xls",
		  "extension": ".xls",
		  "timestamps": {
		    "atimeHuman": "2017-10-19 12:29:33",
		    "ctime": "1508430573",
		    "mtimeHuman": "2017-06-16 11:44:16",
		    "timeParser": "os.stat",
		    "timeType": "STANDARD_INFORMATION",
		    "mtime": "1497627856",
		    "timeFormat": "posix",
		    "ctimeHuman": "2017-10-19 12:29:33",
		    "atime": "1508430573",
		    "os": "nt"
		  }
		}

## Contributing

Comments, feedback and pull requests welcome.

## Authors

Greg Wiedeman

## License

This project is in the public domain
