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
					
					
