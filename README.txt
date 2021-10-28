README.txt

GTN Planning Tool
Created on May 2020
@author: Callum Gilmour
Written in Python 3.8.2
© Callum Gilmour


Program:
	Uses AIS and weather (ICOADS) data to determine to number of ships which could be tested in a year period by GTN N.O.S.E.

Inputs: (see also requirements, data)
	AIS data
	ICOADS data
	IMO Vessel Code data
	Parameters (User Input, see paraimp.py for more details)
		port locations
		port orientation (for use defining bounding box)
		system limits
		date ranges to use
		regex to use for filtering

Outputs: (full details in Mission_Planning.pdf)
	results_dict (test number estimations
	ais_dict
	icoads_dict

-----------------------

Requirements:

External Libraries:
	pandas
	numpy
	geopy
	cartopy
	matplotlib

data:
	AIS data from aisShips.com in csv format
	ICOADS data from NOAA (Extended, 4.5 sigma)
	IMO Vessel Code List (warrantproject)