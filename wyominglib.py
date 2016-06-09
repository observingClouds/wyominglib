"""
	Download and parse wyoming soundings into
	pandas DataFrames, then store to HDF5 file

	Original code: Philip Austin
	Source: https://github.com/phaustin/A405

	Raul Valenzuela
	raul.valenzuela@colorado.edu

	Examples:

	1)
	import wyominglib as wl

	years = np.arange(2000,2003)
	for yr in years:
			wl.download_wyoming(region='samer',
											 station=dict(name='ptomnt',number='85799'),
											 out_directory='/home/raul'
											 year=yr)

	2)
	import wyominglib as wl

	wl.download_wyoming(region='samer',
											station=dict(name='puerto_montt',number='85799'),
											out_directory='/home/raul',
											dates=['2001-01-01 00:00','2001-01-10 12:00'])

	3)
	import wyominglib as wl

	wl.download_wyoming(region='samer',
											station=dict(name='puerto_montt',number='85799'),
											out_directory='/home/raul',
											date='2001-01-01 00:00')


"""

import sys
import urllib
import re
import numpy as np
import h5py
import pandas as pd

from thermlib import find_esat
from constants import constants as con
from bs4 import BeautifulSoup

# We need to parse a set of lines that look like this:

#                              Station number: 82965
#                            Observation time: 110201/0000
#                            Station latitude: -9.86
#                           Station longitude: -56.10
#                           Station elevation: 288.0
#                             Showalter index: -0.37
#                                Lifted index: -0.68

# Here's a regular expresion that does that:


re_text="""
					 .*Station\snumber\:\s(.+?)\n
					 \s+Observation\stime\:\s(.+?)\n
					 \s+Station\slatitude\:\s(.+?)\n
					 \s+Station\slongitude\:\s(.+?)\n
					 \s+Station\selevation\:\s(.+?)\n
					 .*
				"""

#
# DOTALL says: make . include \n
# VERBOSE says: ignore whitespace and comments within the regular expression
#         to help make the expression more readable
#
header_re=re.compile(re_text,re.DOTALL|re.VERBOSE)

def parse_header(header_text):
		"""
		Read a header returned by make_frames and
		return station information

		Parameters
		----------

		header_text : str
									string containing wyoming header read with make_frames

		Returns
		-------
																	
		the_id  : int
							5 digit souding id

		lat     : float
							latitude (degrees North)

		lon     : float
							longitude (degrees east)
		
		elev    : float
							station elevation (meters)
		"""
		header_text=header_text.strip()
		the_match = header_re.match(header_text)
		try:
				the_id,string_time,lat,lon,elev=the_match.groups()
		except AttributeError:
				print('parse failure with: \n',header_text)
		the_id,string_time,lat,lon,elev=the_match.groups()
		elev=elev.split('\n')[0]  #some soundings follow elev with Shoalwater, not Lifted
		lat=float(lat)
		lon=float(lon)
		elev=float(elev)
		day,hour = string_time.strip().split('/')
		year=int(day[:2]) + 2000
		month=int(day[2:4])
		day=int(day[4:6])
		minute=int(hour[2:])
		hour=int(hour[:2])
		return the_id,lat,lon,elev

def parse_data(data_text):
		"""
		Read a single sounding into a dataframe

		Parameters
		----------

		data_text : str
								sounding text

		Returns
		-------

		df_out : dataframe
						 11 column data frame with sounding values

		unit_name : list
								list of strings with name of units of each column
		
		"""

		"""
			read lines with 11 numbers and convert to dataframe

			data_text looks like:

				-----------------------------------------------------------------------------
					 PRES   HGHT   TEMP   DWPT   RELH   MIXR   DRCT   SKNT   THTA   THTE   THTV
						hPa     m      C      C      %    g/kg    deg   knot     K      K      K 
				-----------------------------------------------------------------------------
				 1000.0    100                                                               
					979.0    288   24.0   23.0     94  18.45      0      0  299.0  353.0  302.2
					974.0    333   25.2   21.1     78  16.46    348      0  300.6  349.1  303.6
					932.0    719   24.0   16.0     61  12.42    243      3  303.2  340.3  305.4
					925.0    785   23.4   15.4     61  12.03    225      3  303.2  339.2  305.4
		"""
		all_lines=data_text.strip().split('\n')
		count=0
		theLine=all_lines[count]
		try:
				while theLine.find('PRES   HGHT   TEMP   DWPT') < 0:
						count += 1
						theLine = all_lines[count]
				header_names=all_lines[count].lower().split()
		except IndexError:
				print("no column header line found in sounding")
				sys.exit(1)
		count += 1  #go to unit names
		unit_names=all_lines[count].split()
		count+=2  #skip a row of ------
		data_list=[]
		while True:
				try:
						the_line=all_lines[count]
						dataFields = the_line.split()
						if len(dataFields) == 11:
								try:
										dataFields = [float(number) for number in dataFields]
										es = find_esat(dataFields[3] + 273.15)*0.01  #get vapor pressure from dewpoint in hPa
										dataFields[5] = (con.eps*es/(dataFields[0] - es))*1.e3   #g/kg
								except ValueError:
										print('trouble converting dataFields to float')
										print(dataFields)
										sys.exit(1)
								data_list.append(dataFields)
								#
								# get the next line
								#
						count += 1
						theLine = all_lines[count]
				except IndexError:
						break
		df_out=pd.DataFrame.from_records(data_list,columns=header_names)
		return df_out,unit_names

def make_frames(html_doc):
		"""
		turn an html page retrieved from the wyoming site into a dataframe

		Parameters
		----------

		html_doc : string
							 web page from wyoming upperair sounding site
							 http://weather.uwyo.edu/cgi-bin/sounding retrieved by
							 the urllib module

		Returns
		-------

		attr_dict : dict
							 attr_dict dictionary with ['header', 'site_id','longitude','latitude', 'elevation', 'units']
							
		sound_dict : dict  
								 sounding dictionary with sounding times as keys and sounding as dataframes
		"""
		soup=BeautifulSoup(html_doc,'html.parser')
		keep=list()
		sounding_dict=dict()
		pre = soup.find_all('pre')
		# print(len(pre))
		if len(pre)>0:
				for item in pre:
						keep.append(item.text)

				evens=np.arange(0,len(keep),2)
				for count in evens:
						df,units=parse_data(keep[count])
						the_id,lat,lon,elev=parse_header(keep[count+1])    
						
				header= soup.find_all('h2')[0].text
				attr_dict=dict(units=';'.join(units),site_id=the_id,
											 latitude=lat,longitude=lon,elevation=elev,
											 header = header)
				resp = 'OK'
		else:

				attr_dict=dict()
				df=pd.DataFrame(np.nan,
												index=[0],
												columns=['data'])
				resp = 'NO SOUNDING'

		html_doc.close()

		return attr_dict,df,resp

		
def download_wyoming(region=None,station=None,year=None,
											date=None,dates=None,out_directory=None):
		"""
		function to test downloading a sounding
		from http://weather.uwyo.edu/cgi-bin/sounding and
		creating an hdf file with soundings and attributes

		see the notebook newsoundings.ipynb for use
		"""

		st_num = station['number']
		st_name = station['name']

		url_template=("http://weather.uwyo.edu/cgi-bin/sounding?"
							"region={region:s}"
							"&TYPE=TEXT%3ALIST"
							"&YEAR={year:s}"
							"&MONTH={month:s}"
							"&FROM={start:s}"
							"&TO={stop:s}"
							"&STNM={station:s}")

		name_template = out_directory+'/wyoming_{0}_{1}_{2}.h5'    

		# Parse date to download and output h5 name
		if date and year is None and dates is None:
			dates=pd.date_range(start  =date,
													periods=1,
													freq   ='12H')
			dstr = dates[0].strftime('%Y%m%d%H')
			out_name = name_template.format(region,st_name,dstr)      
		elif dates and date is None and year is None:
			date0=dates[0]
			date1=dates[1]
			dates=pd.date_range(start=date0,
													end  =date1,
													freq ='12H')
			dstr = dates[0].strftime('%Y%m%d%H-')+ \
						 dates[-1].strftime('%Y%m%d%H')
			out_name = name_template.format(region,st_name,dstr)
		else:
			yr=str(year)
			dates=pd.date_range(start=yr+'-01-01 00:00',
													end  =yr+'-12-31 12:00',
													freq ='12H')
			out_name = name_template.format(region,st_name,yr)

		# start downloading for each date
		with pd.HDFStore(out_name,'w') as store:

				for date in dates:

						values=dict(region  = region,
												year    = date.strftime('%Y'),
												month   = date.strftime('%m'),
												start   = date.strftime('%d%H'),
												stop    = date.strftime('%d%H'),
												station = st_num)

						url=url_template.format_map(values)

						html_doc = urllib.request.urlopen(url)

						at_dict,sounding_df,resp = make_frames(html_doc)
						if resp == 'OK':
							attr_dict = at_dict
						else:
							attr_dict = dict()

						print_str ='Read/Write sounding date {}: {}'
						print_date=date.strftime('%Y-%m-%d_%HZ')
						print(print_str.format(print_date, resp))

						thetime=date.strftime("Y%Y%m%dZ%H")
						store.put(thetime,sounding_df,format='table')

		attr_dict['history']="written by wyominglib.py"
		key_list=['header', 'site_id','longitude','latitude',
						 'elevation', 'units','history']

		with h5py.File(out_name,'a') as f:
				print('Writing HDF5 file attributes')
				for key in key_list:
						try:
							print('writing key, value: ',key,attr_dict[key])
							f.attrs[key]=attr_dict[key]
						except KeyError:
							pass
				f.close()

		print('hdf file {} written'.format(out_name))
		print('reading attributes: ')
		with h5py.File(out_name,'r') as f:
				keys=f.attrs.keys()
				for key in keys:
						try:
								print(key,f.attrs[key])
						except OSError:
								pass
