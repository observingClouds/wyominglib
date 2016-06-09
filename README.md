# Download and parse wyoming soundings into pandas DataFrames, then store to HDF5 file

Raul Valenzuela
&nbsp;

raul.valenzuela@colorado.edu

&nbsp;

Original code: Philip Austin
&nbsp;

Source: https://github.com/phaustin/A405

## Install

Clone the repo:
```bash
$git clone git@gitlab.com/rvalenzuela/wyominglib.git
```

add PYTHONPATH (e.g. in bash):
```bash
export PYTHONPATH="/path/to/clone/directory/wyominglib:$PYTHONPATH"
```
## Dependencies

* numpy
* h5py
* BeautifulSoup
* pandas


## Examples
```python
import wyominglib as wl
import numpy as np

years = np.arange(2000,2003)
for yr in years:
	wl.download_wyoming(region='samer',
						 station=dict(name='ptomnt',number='85799'),
						 out_directory='/home/raul'
						 year=yr)
```
```python
import wyominglib as wl

wl.download_wyoming(region='samer',
					station=dict(name='puerto_montt',number='85799'),
					out_directory='/home/raul',
					dates=['2001-01-01 00:00','2001-01-10 12:00'])
```
```python
import wyominglib as wl

wl.download_wyoming(region='samer',
					station=dict(name='puerto_montt',number='85799'),
					out_directory='/home/raul',
					date='2001-01-01 00:00')
```					
					
