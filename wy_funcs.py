"""

    Reads wyoming sounding HDF5 files
    and retrieve an xarray


    Example
    
    import wy_funcs
    out = wy_funcs.get_timeseries(lvl_temp=0)
    hgt_daily = out['hgt'].resample('D').mean()

"""

import h5py
import numpy as np
import pandas as pd
from datetime import datetime

source = "/Users/raulvalenzuela/Google Drive/WY_SOUNDINGS/"

file_fmt = 'wyoming_samer_{}_{}.h5'

colnames = ['pres','hgt','temp','dewp','relh','mixr'
            ,'wdir','sknt','thta','thte','thtv']


def get_df_year(year, station=None):

    hfile = file_fmt.format(station, year)
    f = h5py.File(source + hfile, "r")

    all_dfs = list()
    df_index = list()
    for k in list(f.keys()):
        sound = f[k]['table'].value
        # print k
        idx = datetime.strptime(k, 'Y%Y%m%dZ%H')
        df_index.append(idx)
        if sound.size <= 1:
            df = np.nan
        else:
            data = dict(pres=np.array([v[1][0] for v in sound]),
                        hght=np.array([v[1][1] for v in sound]),
                        temp=np.array([v[1][2] for v in sound]),
                        dewp=np.array([v[1][3] for v in sound]),
                        relh=np.array([v[1][4] for v in sound]),
                        mixr=np.array([v[1][5] for v in sound]),
                        drct=np.array([v[1][6] for v in sound]),
                        sknt=np.array([v[1][7] for v in sound]),
                        thta=np.array([v[1][8] for v in sound]),
                        thte=np.array([v[1][9] for v in sound]),
                        thtv=np.array([v[1][10] for v in sound])
                        )
            df = pd.DataFrame(data=data)

        all_dfs.append(df)

    data = {'sounding': all_dfs}

    df = pd.DataFrame(data, index=df_index)

    return df

def get_raw(year, index=None, isel=0, station=None):

    hfile = file_fmt.format(station, year)
    f = h5py.File(source + hfile, "r")

    for k in list(f.keys())[isel:isel+1]:

        sound = f[k]['table'].value
        print(k)
        if sound.size <= 1:
            data = np.array([np.nan]*48)
            df = pd.DataFrame(data=data)
        else:
            data = dict(pres=np.array([v[1][0] for v in sound]),
                        hght=np.array([v[1][1] for v in sound]),
                        temp=np.array([v[1][2] for v in sound]),
                        dewp=np.array([v[1][3] for v in sound]),
                        relh=np.array([v[1][4] for v in sound]),
                        mixr=np.array([v[1][5] for v in sound]),
                        drct=np.array([v[1][6] for v in sound]),
                        sknt=np.array([v[1][7] for v in sound]),
                        thta=np.array([v[1][8] for v in sound]),
                        thte=np.array([v[1][9] for v in sound]),
                        thtv=np.array([v[1][10] for v in sound])
                        )

            if index in ['h','hgt','height']:
                idx = data.pop('hght')
                df = pd.DataFrame(data=data,index=idx)
            elif index in ['p','pres','press']:
                idx = data.pop('pres')
                df = pd.DataFrame(data=data,index=idx)
            else:
                df = pd.DataFrame(data=data)

    return df


def get_interpolated(year, index=None, isel=0):

    if index in ['h', 'hgt', 'height']:

        raw = get_raw(year, index=index, isel=isel)

        new_levels = np.arange(100, 5000, 100)

        new_raw = raw.reindex(raw.index.union(new_levels))
        interp_raw = new_raw.interpolate('index')

    elif index in ['p','pres','press']:

        raw = get_raw(year, index=index, isel=isel)

        new_levels = np.arange(1000, 20, -10)

        new_raw = raw.reindex(raw.index.union(new_levels))
        interp_raw = new_raw.interpolate('index')

        interp_raw = interp_raw.sort_index(ascending=False)

    return interp_raw


def get_pw(year, index='p', isel=0, station=None):

    '''
        Check sounding_tools.py in CDDIS_ZTD, which is giving
        correct values of PW
    '''

    rho = 1000.  # [kg m-3]
    g = 9.8  # [m s-2]

    raw = get_raw(year, index=index, isel=isel, station=station)

    try:
        dp = raw.index[:-2]-raw.index[2:]  # [hPa]
        dp = dp.values*100.  # [Pa]

        r = raw.mixr.iloc[1:-1].values  # [g kg-1]
        r = r/1000.  # [kg kg-1]

        pw = (1/(rho*g))*np.sum(r*dp)  # [m]
        pw = pw * 1000.  #[mm]

        return pw
    except AttributeError:
        print('Missing sounding')

def get_wysound_serie(station=None, year=None):

    ###
    # Replaced by get_raw
    ###

    hfile = file_fmt.format(station, year)
    f = h5py.File(source + hfile, "r")

    for k in list(f.keys()):

        sound = f[k]['table'].value

        if sound.size <= 1:
            array = np.array([np.nan]*48)
        else:
            # pres = np.array([v[1][0] for v in sound])
            # hght = np.array([v[1][1] for v in sound])
            # temp = np.array([v[1][2] for v in sound])
            # dewp = np.array([v[1][3] for v in sound])
            # relh = np.array([v[1][4] for v in sound])
            # mixr = np.array([v[1][5] for v in sound])
            # drct = np.array([v[1][6] for v in sound])
            # sknt = np.array([v[1][7] for v in sound])
            # thta = np.array([v[1][8] for v in sound])
            thte = np.array([v[1][9] for v in sound])
            # thtv = np.array([v[1][10] for v in sound])
            array = thte

        print(k)
        if k == list(f.keys())[0]:
            bigarray = array
        else:
            print(bigarray.shape, array.shape)
            bigarray = np.vstack((bigarray, array))

    return bigarray


def get_df(sounding):

    if sounding.size > 1:
        array = sounding[0][1]
        for row in sounding[1:]:
            array = np.vstack((array,row[1]))
        df = pd.DataFrame(data=array, columns=colnames)
    else:
        print('No sounding available')
        df = pd.DataFrame()

    return df


def interp_freezh(df, out='value'):

    """
    Linear interpolation of sounding to 
    50-m hgt resolution between 100-m and 5000-m
    
    Find freezH by ordering absolute temperatures
    from min to max and taking the min value (e.g. ~0).
    
    If there are two min values (e.g. due to an inversion)
    it retrieves the one at lower altitude.
    
    :param df: sounding in DataFrame format
    :param out: type of output ['value', 'serie']
    :return: interpolated freezing level in meters
    """

    from scipy.interpolate import interp1d

    x = df['hgt']
    xmin = x.min()
    xmax = x.max()
    y = df['temp'].values
    w = np.isnan(y)
    y[w] = 0.
    interp = interp1d(x, y)

    if np.isnan(xmin) and np.isnan(xmax):
        if out == 'value':
            ''' otherwise return a nan '''
            return np.nan
        elif out == 'serie':
            ''' or an empty series '''
            return pd.Series()
    elif xmin > 5000:
        if out == 'value':
            ''' otherwise return a nan '''
            return np.nan
        elif out == 'serie':
            ''' or an empty series '''
            return pd.Series()
    else:
        hgt_res = 1
        hgt_top = 6000
        # print xmin, xmax
        if (xmin < 100) and (xmax > hgt_top):
            xs = np.arange(100, hgt_top+hgt_res, hgt_res)
            ys = interp(xs)
        elif (xmin > 100) and (xmax > hgt_top):
            xs = np.arange(200, hgt_top+hgt_res, hgt_res)
            ys = interp(xs)
        elif (xmin < 100) and (xmax < hgt_top):
            ''' check if there is a temperature
                close to 0 to continue
            '''
            if ((y > -3) & (y < 3)).any():
                top_sound = int(np.ceil(xmax))
                xs = np.arange(100, top_sound+hgt_res, hgt_res)
                ys = interp(xs)
            else:
                if out == 'value':
                    ''' otherwise return a nan '''

                    return np.nan
                elif out == 'serie':
                    ''' or an empty series '''
                    return pd.Series()
        # except ValueError:
        #     if out == 'value':
        #         ''' otherwise return a nan '''
        #         return np.nan
        #     elif out == 'serie':
        #         ''' or an empty series '''
        #         return pd.Series()


    if out == 'value':
        # sorted = serie.abs().argsort()
        # freezH = serie.iloc[sorted[:2]].index.min()
        cond = np.abs(ys) == np.abs(ys).min()
        freezH = xs[np.where(cond)[0][0]]
        return freezH
    elif out == 'serie':
        serie = pd.Series(data=ys, index=xs)
        return serie


def get_timeseries_freezh(year=None, location=None,
                          output=None, interp=False):

    """
    :param year: 
    :param location: 
    :param output: 
    :return: closest altitude of freezing level
    """

    from datetime import datetime

    if year is None:
        years = list(range(2000, 2018))
    else:
        years = [year]

    x = np.array([])
    y = np.array([])
    t = np.array([])
    tmp_thres_degc = 3

    for yr in years:
        fname = "/wyoming_samer_{}_{}.h5"
        fpath = source + fname.format(location, yr)
        f = h5py.File(fpath, "r")
        print('Processing year: {}'.format(yr))
        for k in list(f.keys()):
            sound = f[k]['table'].value
            t = np.append(t, datetime.strptime(k,'Y%Y%m%dZ%H'))
            if interp:
                df = get_df(sound)
                if df.size == 0:
                    x = np.append(x, np.nan)
                    y = np.append(y, np.nan)
                else:
                    freezh = interp_freezh(df, out='value')
                    x = np.append(x, freezh)
                    y = np.append(y, 0.0)
            else:
                if sound.size > 1:
                    hght = np.array([v[1][1] for v in sound])
                    temp = np.array([v[1][2] for v in sound])
                    idx = np.abs(temp).argmin()

                    filter_ok = (temp[idx] > -tmp_thres_degc) and \
                                (temp[idx] < tmp_thres_degc) and \
                                (hght[idx] > 1000) and \
                                (hght[idx] < 5000)

                    if filter_ok:
                        if output == 'print':
                            txt = 'hgt={:1.0f}, temp={}'
                            print(txt.format(hght[idx], temp[idx]))
                        else:
                            x = np.append(x, hght[idx])
                            y = np.append(y, temp[idx])
                    else:
                        x = np.append(x, np.nan)
                        y = np.append(y, np.nan)
                else:
                    x = np.append(x, np.nan)
                    y = np.append(y, np.nan)

    if output is None:
        dictpd = dict(temp=y, hgt=x)
        df = pd.DataFrame(data=dictpd, index=t)
        return df


def check_hgt_range(year=None):

    f = h5py.File(source+file_fmt.format(year),
                  "r")

    min = np.array([])
    max = np.array([])
    for k in list(f.keys()):
        sound = f[k]['table'].value
        if sound.size > 1:
            hght = np.array([v[1][1] for v in sound])

            min = np.append(min, hght.min())
            max = np.append(max, hght.max())

    txt = 'top_min={:3.0f}, top_max={:3.0f}\nbot_min={:3.0f}, ' \
          'bot_max={:5.0f}'
    print(txt.format(max.min(), max.max(), min.min(), min.max()))
