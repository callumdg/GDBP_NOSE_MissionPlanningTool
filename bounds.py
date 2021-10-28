#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bounds

GTN Planning Tool
Created on May 2020
@author: Callum Gilmour

function to calculating bounding box for AIS and ICOADS data filtering

           N
       A---P---B
       |       |
     W |       | E      port north orientation (similar for E,S,W)
       |       |
       D-------C
           S

           N
       A-------B
       |       |
     W |   P   | E      port middle orientation
       |       |
       D-------C
           S
"""
from geopy import distance


def bounds(param, size):

    out_km = size[0]*1.852
    along_ea_km = (size[1]*1.852)/2  # conver to km

    # lambdas for lat and lon
    destlat = lambda d, brg: round(distance.GeodesicDistance(d).destination(
        param['portlatlon'], brg).latitude, 5)
    destlon = lambda d, brg: round(distance.GeodesicDistance(d).destination(
        param['portlatlon'], brg).longitude, 5)

    if param['portorien'] == 'N':
        bounds = [round((param['portlatlon'][0]), 5),       # N, port loc
                  destlon(along_ea_km, 90),                 # E
                  destlat(out_km, 180),                     # S
                  destlon(along_ea_km, 270)]                # W
    elif param['portorien'] == 'E':
        bounds = [destlat(along_ea_km, 0),                  # N
                  round((param['portlatlon'][1]), 5),       # E, port loc
                  destlat(along_ea_km, 180),                # S
                  destlon(out_km, 270)]                     # W
    elif param['portorien'] == 'S':
        bounds = [destlat(out_km, 0),                       # N
                  destlon(along_ea_km, 90),                 # E
                  round((param['portlatlon'][0]), 5),       # S, port loc
                  destlon(along_ea_km, 270)]                # W

    elif param['portorien'] == 'W':
        bounds = [destlat(along_ea_km, 0),                  # N
                  destlon(out_km, 90),                      # E
                  destlat(along_ea_km, 180),                # S
                  round((param['portlatlon'][1]), 5)]       # W, port loc

    elif param['portorien'] == 'mid':
        bounds = [destlat(out_km/2, 0),
                  destlon(along_ea_km, 90),
                  destlat(out_km/2, 180),
                  destlon(along_ea_km, 270)]

    return bounds
