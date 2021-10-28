#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pltmaps

GTN Planning Tool
Created on May 2020
@author: Callum Gilmour


Program to plot maps for GTN Planning Tool
Example of Humber Esturary given
Uses Cartopy and Natural Earth Data
"""

import cartopy.crs as ccrs
import cartopy.feature as cf
import matplotlib.pyplot as plt
import matplotlib.patches as mpatch
from matplotlib.lines import Line2D


def pltmaps(ais_bounds, weather_bounds, param, bouy_loc):

    # create plot
    fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.OSGB()))
    extn = [-1.5, 3, 54.5, 52.5]
    ax.set_extent(extn)
    # add oceans, rivers, lakes
    ax.add_feature(cf.OCEAN.with_scale('50m'), color='#3f5d73')
    ax.add_feature(cf.RIVERS.with_scale('10m'), edgecolor='#87a0b2')
    ax.add_feature(cf.LAKES.with_scale('10m'), color='#87a0b2')
    ax.add_feature(cf.NaturalEarthFeature('physical', 'rivers_europe', '10m',
                                          edgecolor='#87a0b2',
                                          facecolor=''))

    # Lambda to draw rectangles
    rect_draw = lambda loc, w, h, ecol, fcol, alpha: mpatch.Rectangle(
        loc, width=w, height=h, linewidth=1, edgecolor=ecol,
        facecolor=fcol, alpha=alpha, transform=ccrs.PlateCarree())
    # AIS bounds
    ax.add_patch(rect_draw((ais_bounds[3], ais_bounds[2]),
                           ais_bounds[1]-ais_bounds[3],
                           ais_bounds[0]-ais_bounds[2],
                           '#edb95f', '#ba7cde', 0.4))
    ax.text(ais_bounds[3], ais_bounds[2]+1.415, 'AIS\nBounds',
            fontsize='large', color='#ffffff', transform=ccrs.PlateCarree())
    # ICOADS bounds
    ax.add_patch(rect_draw((weather_bounds[3], weather_bounds[2]),
                           weather_bounds[1]-weather_bounds[3],
                           weather_bounds[0]-weather_bounds[2],
                           '#edb95f', '#87a0b2', 0.4))
    ax.text(weather_bounds[1]+0.1, weather_bounds[0]-0.5, 'ICOADS\nBounds',
            fontsize='large', color='#ffffff', transform=ccrs.PlateCarree())

    # port locations
    for value in param['port_loc'].values():
        ax.plot(value[1], value[0], marker='o', color='#edb95f',
                markersize=6, transform=ccrs.PlateCarree())
    ax.text((param['port_loc']['imm'][1]-0.5),
            (param['port_loc']['imm'][0]+0.17), 'ABP\nHumber',
            fontsize='large', color='#3f5d73', transform=ccrs.PlateCarree())
    # weather bouy locations
    for index, row in bouy_loc.iterrows():
        ax.plot(row['lon'], row['lat'], marker='^', color='#ffffff',
                markersize=5, transform=ccrs.PlateCarree())

    # legend
    legend_elements = [Line2D([0], [0], label='ABP Humber Port',
                              linestyle='none', markerfacecolor='#edb95f',
                              markeredgecolor='none',
                              markersize=8, marker='o'),
                       Line2D([0], [0], label='Moored Weather Bouy',
                              linestyle='none', markerfacecolor='#ffffff',
                              markeredgecolor='none',
                              markersize=8, marker='^')]
    leg = ax.legend(handles=legend_elements, loc=0)
    for text in leg.get_texts():
        plt.setp(text, color='#3f5d73')

    # save figure to file
    fig.savefig(param['plotsfolder']/'map.png')
