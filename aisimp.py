#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aisimp

GTN Planning Tool
Created on May 2020
@author: Callum Gilmour

Imports AIS data supplied from single CSV file curotesy of shipAIS.com
Scrubs and adds detail from IMO vessel codes

Discussion of RegEx used can be found in the report
RegEx visulisations have been included in the regex folder
"""
import os
import re
import pickle as pkl

import pandas as pd
from imovcimp import imovcimp


def aisimp(param, bounds):

    # if pickle exsists of data retrive it otherwise Import CSV
    # concatinate area string and file suffix
    raw_pkl_path = param['datafolder'] / (param['area'] + '_ais_raw.pkl')
    if os.path.exists(raw_pkl_path):
        with open(raw_pkl_path, 'rb') as file:
            ais_data = pkl.load(file)
    else:
        col_names = ["lat", "lon", "date", "shipname", "MMSI", "IMO",
                     "callsign", "len", "beam", "tonnage", "dwt", "heading",
                     "bearing", "speed", "dest"]
        # funtion to parse dates to UTC (as some BST) and define format
        dateparse = lambda x: pd.to_datetime(x, utc=True,
                                             infer_datetime_format=True,
                                             format='%Y-%m-%d %H:%M:%S %Z')
        aisfile = param['datafolder'] / param['aisfile']
        # import csv
        ais_data = pd.read_csv(aisfile, sep="	", names=col_names,
                               header=None, parse_dates=['date'],
                               date_parser=dateparse, cache_dates=True)
        with open(raw_pkl_path, 'wb') as file:
            pkl.dump(ais_data, file)


    # record monthly entries
    ais_review = {'entries': (ais_data[['date', 'IMO']]
                              .groupby(pd.Grouper(key='date', freq='M'))
                              .count())}
    ais_review['entries'].index = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ais_review['entries'].columns = ['Entries']


    # Begin scrubbing
    # Save info for quality review
    review_list = []
    review = lambda operation: review_list.append([operation, len(ais_data),
                                                   ais_data['IMO'].nunique(),
                                                   ais_data['dest'].nunique()])
    review('Orignal')   # save values before scrubbing
    # drop entries without IMO codes, all ships over 300gt must have one
    ais_data.query('IMO != 0', inplace=True)
    review('Has IMO code')
    # remove entries outside bounds
    ais_data.query('lat < @bounds[0] and lat > @bounds[2] '
                   'and lon < @bounds[1] and lon > @bounds[3]',
                   inplace=True)
    review('Within test boundaries')
    # remove work boats, and dest with more then 2 ?
    ais_data = ais_data[ais_data['dest'].str.contains(param['ignore'],
                                                      regex=True) == False]
    review('Not a utility vessel')
    # dest must mention target port(s)
    ais_data = ais_data[ais_data['dest'].str.contains(
        param['targetport'], regex=True) == True]
    review('Ref to target port in dest')
    # remove qualifiers
    reg = re.compile(param['qualifiers'])
    ais_data['dest'].replace(reg, '', inplace=True)
    review('Drop qualifiers')
    # Replace full names with abbreviation
    reg = re.compile(param['abrv'])
    ais_data['dest'].replace(reg, r'\1\2\3', inplace=True)
    review('Substitute abbreviation')
    # Target ports as destination
    reg = re.compile(param['are dest'])
    ais_data['dest'].replace(reg, r'\2', inplace=True)
    review('Sub abbr if correct dest')
    # Extract correct values (abvr at end)
    ais_data = ais_data[ais_data['dest'].str.match(param['extract'])]
    review('Drop other entries')
    # remove spaces ' ' from callsign
    ais_data['callsign'].replace(' ', '', inplace=True)

    # Create ship details data frame and strip back main df
    ais_ships = ais_data[['IMO', 'shipname', 'MMSI', 'callsign', 'len', 'beam',
                          'tonnage', 'dwt']].drop_duplicates(subset='IMO')
    # Read IMO Vessel Codes file and import scrubbed data frame
    imovcfile = param['datafolder'] / param['imovcfile']
    imovc = imovcimp(imovcfile)
    # Merge with 'type and flag' columns from IMO Vessel Codes df
    ais_ships = ais_ships.merge(imovc[['IMO', 'type', 'flag']],
                                on='IMO', how='left')
    ais_ships.dropna(subset=['type'], inplace=True)
    # drop unneed columns from data for stripped back ship location
    ais_data = ais_data.drop(['shipname', 'MMSI', 'callsign', 'len', 'beam',
                              'tonnage', 'dwt'], axis=1)
    # drop entries in ship_loc where ships are not in ship_det
    ais_data = ais_data[ais_data['IMO'].isin(ais_ships['IMO'])]
    review('IMO Vessel Codes')

    # convert review_list to df to return
    review_cols = ['operation', 'len', 'uniqships', 'uniqdest']
    ais_review['filtering'] = pd.DataFrame(review_list, columns=review_cols)


    # Determine unique ships by month and port
    # unique to year
    data = (ais_data[['date', 'IMO', 'dest']].drop_duplicates(subset='IMO'))
    year_uship = {}
    # loop over ports calculating monthly unique ships
    for port in param['ports']:
        year_uship[port] = ((data[['date', 'IMO']][data['dest'] == port])
                            .groupby(pd.Grouper(key='date', freq='M'))
                            .count())
        if len(year_uship[port]) != 12:  # chek dataframes include values
            year_uship.pop(port)
            continue
        year_uship[port].index = param['months']
    year_uship = pd.concat(year_uship, axis=1)
    year_uship.columns = year_uship.columns.droplevel(-1)
    # calculate monthly percentage
    year_uship['Perc'] = round((year_uship.sum(axis=1)/len(data))*100, 1)
    # Caculate total per port
    year_uship.loc['sum', :] = round(year_uship.sum())

    # unique to month (i.e. counts each month)
    data = ais_data[['date', 'IMO', 'dest']].copy(deep=True)
    data['month'] = data.date.dt.month
    data['hour'] = data.date.dt.hour
    data.drop_duplicates(subset=['IMO', 'month'], inplace=True)
    month_uship_pregroup = data
    data = (data[['month', 'IMO', 'dest']]
            .groupby(['month', 'dest'])
            .count()
            .reset_index())
    # format into monthly dataframe
    month_uship = {}
    for port in param['ports']:
        month_uship[port] = (data[data.dest == port]
                             .reset_index(drop=True)
                             .drop(columns=['dest', 'month']))
        if len(month_uship[port]) != 12:
            month_uship.pop(port)
            continue
        month_uship[port].index = param['months']
        month_uship[port].columns = [port]
    month_uship = pd.concat(month_uship, axis=1)
    month_uship.columns = month_uship.columns.droplevel(-1)
    # calculate monthly percentage
    month_uship['Perc'] = round((month_uship.sum(axis=1)
                                 / len(month_uship_pregroup)) * 100, 1)
    # Caculate total per port
    month_uship.loc['sum', :] = round(month_uship.sum())

    # Time of day trends
    hour_ships = month_uship_pregroup[['IMO', 'hour']].groupby('hour').count()
    hour_ships.columns = ['count']
    hour_ships['count adj'] = hour_ships['count']
    hour_ships.loc[0, 'count adj'] = round(
        hour_ships.loc[0, 'count'] -
        (hour_ships.loc[0, 'count']-hour_ships['count'].loc[1:23].mean()))

    ais_review['uship'] = {'year_uship': year_uship,
                           'month_uship': month_uship,
                           'hour_ships': hour_ships}


    # collate return dict
    ais_dict = {'data': ais_data, 'ships': ais_ships, 'review': ais_review}
    return ais_dict
