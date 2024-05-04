# wsu-campus-walking-route-plotter
## This is a Windows application mapping Washington State University's Pullman campus.
### Description
This application is designed to provide students at Washington State University with a helpful map and route-plotter to help guide them as they walk along the Pullman campus, looking for the correct building for which their classes are being held.

### Usage Instructions
Before anything else is done, the user's machine must have Python3 and Pip installed. Pip is a command line tool for downloading Python libraries, and instructions for download can be found here: https://pip.pypa.io/en/stable/installation/
After the user installs Pip (possibly adding the installation file to their machine's PATH variable), the user should run the following commands via Command Prompt on Windows:
> pip install mysqlx-connector-python
> pip install PyQt6
> pip install pygame
After this, the user should extract all files in the Main branch to a new folder on their machine, then run main.py either through Command Prompt with the following command:
> py main.py
or by running main.py through an IDE.

A login page should appear, from which the user should either sign up or log in. After successfully logging in, the user can click the nodes (red circles) on the WSU map to get a route between the two selected nodes.

NOTE: After the 8th of May, our database hosting service will expire. If one needs to access the program after this date, they should first revert to commit a002786, and then ignore instructions regarding the log-in page.

### Collaborators
  WSU ID	  Name	          Email	                  
  11802879	Joshua Evans	  Joshua.d.evans@wsu.edu	CONTACT
  
  11759304	Grace Anderson	  grace.j.anderson@wsu.edu	
  
  11742599	Khang Bui	  khang.bui@wsu.edu	

  11635434	Aaron Howe    	  aaron.howe@wsu.edu	

  11846994	Nathan Lassing    nathan.lassing@wsu.edu
				
				
