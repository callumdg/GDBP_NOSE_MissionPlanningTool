#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
imovcimp

GTN Planning Tool
Created on May 2020
@author: Callum Gilmour

imports IMO Vessel Code list
from csv found in data folder
data from: https://github.com/warrantgroup/IMO-Vessel-Codes
note: data last updated 03/03/16
"""
import re
import pandas as pd


def imovcimp(filename):

    # import imo vessel codes csv
    imovc = pd.read_csv(filename, header=0, sep=",")
    imovc.rename(columns={'imo': 'IMO'}, inplace=True)
    # Clean Up Names
    reg = re.compile(r'(^.*(Bulker|Container|Ro-Ro|Cargo|Tanker|Carrier|Reefer'
                     '|Other|Bulk).*$)')
    # replace Ro-Ro and Bulk
    imovc['type'] = (imovc['type']
                     .str.replace('^.*Ro-Ro.*$', 'Ro-Ro')
                     .str.replace('^.*Bulk.*$', 'Bulker'))
    reg = re.compile(r'(Container|Ro-Ro|Cargo|Tanker|Carrier|Reefer|Other'
                     '|Bulk)')
    imovc['type'] = imovc['type'].str.extract(reg)
    # Drop na types
    imovc = imovc[imovc['type'].notna()]
    # drop duplicates
    imovc = imovc.drop_duplicates(subset='IMO')

    return imovc
