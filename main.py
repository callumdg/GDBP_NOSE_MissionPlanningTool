#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main

GTN Planning Tool
Created on May 2020
@author: Callum Gilmour

Main program for GTN planning and sales tool:
    Estimates yearly test numbers for give area
    Plots graphs and maps analysis data
    (Plots and maps available for Humber Estuary Only)

User inputs should be predefined in paraimp script

Folder Structure:
    All data files should be stored in 'data' folder, with file names edited
    in paraimp
    All plots are export to the 'plots' folder
"""
# python libraries
import os
import pickle as pkl
# program moudles
from paramimp import paramimp
from bounds import bounds
from aisimp import aisimp
from icoadsimp import icoadsimp
from plots import plots
from pltmaps import pltmaps


def tool(area):  # humber,southampton,wales

    # Import Parameters
    param = paramimp(area)

    # AIS:retrive or scrub and analyse AIS data
    # Define ais bounds
    ais_bounds = bounds(param, param['boundsize'])
    # define path of pickle
    ais_path = param['datafolder'] / (param['area'] + '_ais_dict.pkl')
    # check if pickle of analysed data exsits in data directory
    if os.path.exists(ais_path):
        with open(ais_path, 'rb') as file:
            ais_dict = pkl.load(file)
    else:
        ais_dict = aisimp(param, ais_bounds)
        # save pickle of analysed data to file
        with open(ais_path, 'wb') as file:
            pkl.dump(ais_dict, file)

    # Weather: retrive or, scrub and analyse ICOADS
    # Define weather bounds
    weather_bounds = bounds(param, ((param['boundsize'][0])*2,
                                    (param['boundsize'][1])))
    ic_path = param['datafolder'] / (param['area'] + '_icoads_dict.pkl')
    # check if pickle exists
    if os.path.exists(ic_path):
        with open(ic_path, 'rb') as file:
            icoads_dict = pkl.load(file)
    else:
        icoads_dict = icoadsimp(param, weather_bounds)
        # save pickle to file of analysed data
        with open(ic_path, 'wb') as file:
            pkl.dump(icoads_dict, file)

    # results
    # calculate operational ratio based on weather and maintance
    # an explanation of average vs every values is included in the report
    op_ratio_we = {}
    op_ratio_we['avg'] = icoads_dict['results']['ratio']['set'][
        ('check', 'avg')]
    op_ratio_we['every'] = icoads_dict['results']['ratio']['set'][
        ('check', 'every')]
    op_range = {}
    op_range['avg'] = (
        op_ratio_we['avg'],  # 100% crossover
        op_ratio_we['avg']+param['non_op_maint'])  # 0% cross over
    op_range['every'] = (
        op_ratio_we['every'],  # 100%
        op_ratio_we['every']+param['non_op_maint'])  # 0%

    # Calculate number of ships tested
    ships_tested = [
        len(ais_dict['ships'])*op_range['avg'][0],
        len(ais_dict['ships'])*op_range['avg'][1],
        len(ais_dict['ships'])*op_range['every'][0],
        len(ais_dict['ships'])*op_range['every'][1]]
    ships_tested = [int(num) for num in ships_tested]
    ships_tested = [max(ships_tested), min(ships_tested)]  # max and min
    # number of vessels not found in IMO Vessel code list to estimate error
    imovc_pre = ais_dict['review']['filtering'].iloc[8, 2]
    imovc_multi = (
        1 + (imovc_pre - ais_dict['review']['filtering'].iloc[9, 2])
        / imovc_pre)  # calculate multiplier
    # apply multiplier
    ships_tested_imovcadj = [int(num*imovc_multi) for num in ships_tested]
    # creat dictionary to return
    test_numbers = {
        'normal': ships_tested, 'imovc adj': ships_tested_imovcadj,
        'ratio': {'avg': op_range['avg'], 'all': op_range['every']}}

# Plot graphs and maps
    if area == 'humber':
        # Graphs
        plots(ais_dict, icoads_dict, param, test_numbers)
        # Plot Map
        pltmaps(ais_bounds, weather_bounds, param,
                icoads_dict['review']['bouy loc'])

    return ais_dict, icoads_dict, test_numbers
