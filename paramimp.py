#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
paramimp

GTN Planning Tool
Created on May 2020
@author: Callum Gilmour

imports parameters set by operator in this script

RegEx discussed in report, diagrams for Humber found in 'regex' folder
"""
from pathlib import Path
from pandas import Timestamp as ts


def paramimp(area):

    # varaibles relating to system and file paths
    system = {
        'non_op_maint': 1/7,  # non operational days due to maintance
                              # (1 day out of 7)
        'windlimit': 15,  # m/s (UAV or sensor whichever is lower)
        'boundsize': (30, 80),  # (out,along coast with port at middle) NM
        # data range to use for ICOADS data
        'icdaterange': [ts(2019, 12, 31, 23, 59), ts(2018, 1, 1)]}

    files = {'datafolder': Path('data/'),
             'plotsfolder': Path('plots/'),
             'aisfile': area + '.csv',
             'imovcfile': 'imovc.csv',
             'icoadsfile': area + '_icoads.csv'}
    # regex for work ships and similar to ignore
    reg = {'ignore': r'(?i)TOW|TUG|PILOT|DREDGE|DRYDOCK|ANC|DOCK|PS|'
                     r'OFFSHORE|DRIFT|\?{2,}'}

    lists = {'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']}

    # Varaibles relating to particular region
    if area == 'humber':
        ports = {'area': area,
                 'port_loc': {
                     'imm': (53.63635, -0.1851795),       # Immingham
                     'hul': (53.74237, -0.2797584),       # Hull
                     'goo': (53.71931, -0.6709594),       # Goole
                     'gri': (53.579235, -0.073521255)},   # Grimsby (lat,lon)
                 'ports': ['IMM', 'GOO', 'GRI', 'HUL'],
                 'portlatlon': (53.63635, -0.1851795),  # primary loc
                 'portorien': 'W'}  # coast it is on
        # area specific regex
        reg_area = {'targetport': r'(?i)IMM|GRI|HUL|GOO',
                    'qualifiers': r'(?i) |U.?K.?|ROAD|GB|EU|HUMBER',
                    'abrv':
                        r'(?i)(^.*)(IMM|HUL|GOO|GRI)(?:INGHAM|L(?!E)|'
                        r'LE|MSBY)(.*$)',
                    'are dest':
                        r'(?i)(^.*(IMM|HUL|GOO|GRI)(?:(?:[^A-Z]*[A-Z]'
                        r'{,2}|\(?[A-Z]*)[^A-Z]*)?$)',
                    'extract': r'^(?:IMM|HUL|GOO|GRI)$'}

    elif area == 'southampton':
        ports = {'area': area,
                 'port_loc': {'sou': (50.898175, -1.4205025)},  # southampton
                 'ports': ['IMM', 'GOO', 'GRI', 'HUL'],
                 'portlatlon': (50.898175, -1.4205025),  # primary loc
                 'portorien': 'N'}  # coast it is on
        # area specific regex
        reg_area = {'targetport': '(?i)SOU',
                    'qualifiers': r'(?i) |U.?K.?|ROAD|GB|EU',
                    'abrv': r'(?i)(^.*)(SOU)(?:THAMPTON)(.*$)',
                    'are dest':
                        r'(?i)(^.*(SOU)(?:(?:[^A-Z]*[A-Z]{,2}|\(?[A-Z]*)'
                        r'[^A-Z]*)?$)',
                    'extract': r'^(?:SOU)$'}

    elif area == 'wales':

        ports = {'area': area,
                 'port_loc': {'byg': (51.39865, -3.261056),    # Barry
                              'cdf': (51.46206, -3.162041),    # Cardiff
                              'swa': (51.61409, -3.921255),    # Swansea
                              'npt': (51.559525, -2.983841),   # Newport
                              'ptb': (51.57865, -3.798372)},   # Port Talbot
                 'ports': ['BYG', 'CDF', 'SWA', 'NPT', 'PTB'],
                 'portlatlon': (51.39865, -3.261056),  # primary loc
                 'portorien': 'mid'}  # coast it is on
        # area specific regex
        reg_area = {'targetport': r'(?i)BAR|BYG|CAR|CDF|SWA|NEW|NPT|PTB',
                    'qualifiers': r'(?i) |U.?K.?|ROAD|GB|EU',
                    'abrv':
                        r'(?i)(^.*)(IMM|HUL|GOO|GRI)(?:INGHAM|L(?!E)|'
                        r'LE|MSBY)(.*$)',
                    'are dest':
                        r'(?i)(^.*)(BAR|CAR|SWA|NEW)(?:RY|R?DIF?F|NSEA|'
                        ' ?PORT)(.*$)',
                    'extract': r'^(?:BAR|BYG|CAR|CDF|SWA|NEW|NPT|PTB)$'}

    # join for export
    param = {**system, **files, **reg, **lists, **ports, **reg_area}

    return param
