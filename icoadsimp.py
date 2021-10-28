#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
icoadsimp

GTN Planning Tool
Created on May 2020
@author: Callum Gilmour

Imports ICOADS (International Comprehensive Ocean-Atmosphere Data Set)
Full details of variables can be found at: https://icoads.noaa.gov/
A discussion is included in the report

ICOADS Varibles Used
Time:       YR,MO,DY,HR (time alrady UTC)
Loc:        LAT (DegN), Lon (DegE)
Wind:       W (Speed true)
Wave:       WH (height)
Weather:    VV (vis), WW (present weather) (see report for details),
            SLP (sea level pressure), AT (air temp)
Other:      SID (source ID), PT (Platform type), ND (night/day flag),
UID (unique entry identifier)
"""

import pandas as pd
import numpy as np


def icoadsimp(param, bounds):

    # file path
    icoadsfile = param['datafolder'] / param['icoadsfile']
    # columns to import
    cols = ['YR', 'MO', 'DY', 'HR', 'LAT', 'LON', 'W', 'VV', 'WW', 'SLP',
            'AT', 'WH', 'PT', 'ND']
    # read CSV
    data = pd.read_csv(icoadsfile, usecols=cols, dtype={'HR': np.int64})
    # rename cols
    data.rename(columns={'YR': 'year', 'MO': 'month', 'DY': 'day',
                         'HR': 'hour', 'LAT': 'lat', 'LON': 'lon',
                         'W': 'wind speed', 'VV': 'vis',
                         'WW': 'pres weather',
                         'SLP': 'sea level pressure', 'AT': 'air temp',
                         'WH': 'wave height', 'ND': 'nightday'},
                inplace=True)
    # parse datetime
    data['datetime'] = pd.to_datetime(data[['year', 'month', 'day', 'hour']],
                                      infer_datetime_format=True)
    data.drop(columns=['year', 'month', 'day', 'hour'], inplace=True)
    colorder = ['datetime', 'lat', 'lon', 'wind speed', 'vis', 'pres weather',
                'sea level pressure', 'air temp', 'wave height', 'PT',
                'nightday']
    data = data.reindex(columns=colorder)

    # review function
    review_list = []
    flatten = lambda l: [item for sublist in l for item in sublist]
    nanperc = lambda cols: ((data[cols].isna().sum() / len(data))*100)
    nanperc_cols = ['wind speed', 'vis', 'pres weather', 'sea level pressure',
                    'air temp', 'wave height']
    review = lambda operation: review_list.append(flatten(
        [[operation], [len(data)], nanperc(nanperc_cols).tolist()]))
    review('Original')  # record orignal percentages

    # begin filtering
    # filter by lat lon
    data.query('@bounds[2] < lat < @bounds[0] '
               'and @bounds[3] < lon < @bounds[1]', inplace=True)
    review('Within Bounds')
    # filter by date_range
    dt_range = param['icdaterange']
    data = (data[(data['datetime'] <= dt_range[0])
                 & (data['datetime'] >= dt_range[1])]
            .copy(deep=True))
    review('Limit Datetime Range')
    # take only moored bouys
    nanperc_pt = {'all platform types': nanperc('PT')}  # % nans b4 drop
    data.query('PT == 6', inplace=True)
    nanperc_pt['moored bouys only'] = nanperc('PT')  # % nans after drop
    data.drop(columns='PT', inplace=True)    # drop PT col
    review('Moored bouys only')

    # summary of data for hourly,monthly,daily,yearly,dataset
    cols = ['datetime', 'wind speed', 'wave height', 'air temp', 'vis',
            'sea level pressure', 'pres weather']  # cols to be analysed
    funcs = ['mean', 'std', 'max', 'min', 'count']  # list of funcs to apply
    # dict defining what functions to apply to each column
    col_func = {'wind speed': funcs,                         # m/s
                'wave height': funcs,                        # m
                'air temp': funcs,                           # deg c
                'vis': funcs,                                # see report
                'sea level pressure': funcs,                 # hPa
                'pres weather': [pd.Series.mode, 'count']}    # see report
    # lambda to apply groupby summary functions
    analysis = lambda freq: (data[cols].groupby(
        pd.Grouper(key='datetime', freq=freq)).agg(col_func).reset_index())
    # freq's to compute summary for
    freq_dict = {'hour': 'H', 'day': 'D', 'week': 'W',
                 'month': 'M', 'year': 'Y'}
    # loop to iterate of freq_dict values and apply analysis lambda
    summary = {}
    for key, value in freq_dict.items():
        summary[key] = analysis(value)
    # special case for all values
    col_func.pop('pres weather', None)
    all_gen = data[cols].agg(col_func)  # run col_func except pres_weather
    we_mode = data['pres weather'].mode()    # pres weather mode
    we_count = data['pres weather'].count()  # pres weather count
    # dataframe with correct col name for pres weather mode and count
    all_we = pd.DataFrame([we_mode, pd.Series(we_count)],
                          index=['mode', 'count'])
    all_we.rename(columns={0: 'pres weather'}, inplace=True)
    # concat to get final sumary for all data
    summary['set'] = pd.concat([all_gen, all_we], axis=1)

    # flags (based on average)
    # create new dataframe with required variables
    flags = data[['datetime', 'lat', 'lon', 'nightday']].copy(deep=True)
    # create dictionary with conditions for flags
    # present weather conditions
    we_cond = [((data['pres weather'] >= 0)  # 1, good conditions
                & (data['pres weather'] <= 4))
               | (data['pres weather'] == 10)
               | (data['pres weather'] == 11),
               (data['pres weather'].isnull())]  # nan, not provided
    # visability conditions
    vis_cond = [(data['vis'] >= 92),
                (data['vis'].isnull())]
    # wind conditions
    wind_cond = [(data['wind speed'] <= param['windlimit']),
                 (data['wind speed'].isnull())]
    cond_dict = {'weather': we_cond, 'vis': vis_cond, 'wind': wind_cond}
    # determine flags
    for key, value in cond_dict.items():
        flags[key] = np.select(value, [True, np.nan], default=False)

    # hourly flags: determine hourly flags, True only if ALL values true
    fhour = (flags[['datetime', 'vis', 'wind', 'weather']]
             .groupby(pd.Grouper(key='datetime', freq='H'))
             .agg(['all', 'count'])
             .reset_index())
    # overall check flag using all values
    fhour[('check', 'every')] = fhour[['vis', 'wind', 'weather']].all(axis=1)

    # wind and vis based on hourly avg
    hour_avg = ((summary['hour'][['wind speed', 'vis']])
                .loc[:, (slice(None), ('mean'))]
                .copy(deep=True))
    hour_avg.columns = hour_avg.columns.droplevel(level=1)
    # vis conditions
    vis_cond = [(hour_avg['vis'] >= 92),
                (hour_avg['vis'].isnull())]
    # wind conditions
    wind_cond = [(hour_avg['wind speed'] <= param['windlimit']),
                 (hour_avg['wind speed'].isnull())]
    cond_avg = {('vis', 'avg'): vis_cond, ('wind', 'avg'): wind_cond}
    # loop over cond_avg setting bool value dependnt on conditions
    for key, value in cond_avg.items():
        fhour[key] = (np.select(value, [True, np.nan], default=False)
                      .astype('bool'))
    # overall check flag using avg vis and rain values
    fhour[('check', 'avg')] = (pd.concat([
        fhour.xs('avg', axis=1, level=1, drop_level=False),
        fhour['weather']['all']], axis=1)  # retrive weather f
                               .all(axis=1))
    fhour.rename(columns={'all': 'flag'}, level=1, inplace=True)
    # reorder
    fhour = fhour.reindex(columns=['datetime', 'vis', 'wind',
                                   'weather', 'check'], level=0)
    # find differnce between respective means of check values
    check_diff = (fhour[('check', 'avg')].mean() -
                  fhour[('check', 'every')].mean())

    # flag ratio for time periods
    # lambda to apply groupby summary functions
    ratio_ana = lambda freq: (
        fhour.groupby(pd.Grouper(key='datetime', freq=freq))
        .mean()
        .reset_index())
    # freq's to compute summary for
    freq_dict = {'hour': 'H', 'day': 'D', 'week': 'W',
                 'month': 'M', 'year': 'Y'}
    ratio = {}
    # loop to iterate of freq_dict values and apply analysis lambda
    for key, value in freq_dict.items():
        ratio[key] = ratio_ana(value)
    # special case for all values, mean of year values
    ratio['set'] = ratio['year'].mean()

    # organise data for output
    # create dataframe from review function
    review_cols = ['operation', 'len', 'wind speed', 'vis', 'pres weather',
                   'sea level pressure', 'air temp', 'wave height']
    nanperc_df = pd.DataFrame(review_list, columns=review_cols)
    review = {'dt range': dt_range,  # datetime range
              'bouy loc': data[['lat', 'lon']].drop_duplicates(),
              'bounds': bounds,
              'platform type nanperc': nanperc_pt,  # nan% for plt ttpe
              # difference between flag methods
              'every avg diff': round(check_diff, 5),
              'filt nanperc': nanperc_df}  # review of filtering impact
    results = {'summary': summary,
               'ratio': ratio}
    alldata = {'filtered': data,
               'flag': flags,
               'hourly flags': fhour}
    icoads_dict = {'data': alldata,
                   'results': results,
                   'review': review}
    return icoads_dict
