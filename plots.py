#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plots

GTN Planning Tool
Created on May 2020
@author: Callum Gilmour

Plots for GTN Planning Tool
for Humber Estuary Region Only

To see figures in browser or IDE use plot(fig)
with from plotly.offline import plot
"""

# from plotly.offline import plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def plots(ais_dict, icoads_dict, param, test_numbers):

    # define colours
    yl = '#edb95f'  # yellow
    tl = '#3f5d73'  # teal
    lb = '#87a0b2'  # light blue
    pl = '#ba7cde'  # purple
    # faded versions
    ylf = '#F0D6A8'
    tlf = '#75818A'
    plf = '#D8C4E3'


    # AIS
    # Funnel Plots
    funnel = lambda x, y: go.Figure(
        go.Funnel(x=x, y=y,
                  textinfo='value+percent initial',
                  marker={'color': [tl, yl, tl, yl, tl, yl,
                                    tl, yl, tl, yl]}))
    # Total AIS Datapoints
    aisr_len = (ais_dict['review']['filtering']
                .drop([5, 6, 7])
                .round({'len': -4}))
    fig1 = funnel(aisr_len['len'], aisr_len['operation'])
    fig1.update_layout(
        title='Filtering Effectiveness: Total AIS Datapoints',
        yaxis_title='Operation')

    # Uniq Ships
    aisr_uships = ais_dict['review']['filtering'].drop([4, 5, 6, 7])
    fig2 = funnel(aisr_uships['uniqships'], aisr_uships['operation'])
    fig2.update_layout(
        title='Filtering Effectiveness: Unique Ships',
        yaxis_title='Operation')

    # Uniq Destination
    aisr_udest = ais_dict['review']['filtering'].drop(9)
    fig3 = funnel(aisr_udest['uniqdest'], aisr_udest['operation'])
    fig3.update_layout(
        title='Scrubbing: Unique Destination',
        yaxis_title='Operation')

    # Ship distrubution over time
    # Ships per month at each port as stacked bar (Unique to year)
    year_uship = ais_dict['review']['uship']['year_uship']
    bar = lambda name, abrv, color: go.Bar(
        name=name+': '+str(int(year_uship.loc['sum', abrv])),
        x=param['months'], y=year_uship[abrv],
        marker_color=color)
    # plot and adjust layout
    name_gri = 'Grimby'+': '+str(int(year_uship.loc['sum', 'GRI']))
    fig4 = go.Figure(data=[
        bar('Immingham', 'IMM', lb), bar('Hull', 'HUL', yl),
        bar('Goole', 'GOO', tl), go.Bar(name=name_gri,
                                        x=param['months'], y=year_uship['GRI'],
                                        marker_color=pl,
                                        text=year_uship['Perc'])])
    fig4.update_layout(
        barmode='stack',
        title='Unique Ships by Month and Port (Year)',
        yaxis_title='Number of Unique Ships',
        xaxis_title='Months',
        legend_title_text='Port: Total Ships (2019)')
    fig4.update_traces(selector={'name': name_gri},
                       texttemplate='%{text}%',
                       textposition='outside')  # add monthly percentages

    # unique ships per month (unique to month)
    month_uship = ais_dict['review']['uship']['month_uship']
    bar = lambda name, abrv, color: go.Bar(
        name=name+': '+str(int(month_uship.loc['sum', abrv])),
        x=param['months'], y=month_uship[abrv],
        marker_color=color)
    # plot and adjust layout
    name_gri = 'Grimby'+': '+str(int(month_uship.loc['sum', 'GRI']))
    fig5 = go.Figure(data=[
        bar('Immingham', 'IMM', lb), bar('Hull', 'HUL', yl),
        bar('Goole', 'GOO', tl), go.Bar(
            name=name_gri, x=param['months'], y=month_uship['GRI'],
            marker_color=pl, text=month_uship['Perc'])])
    fig5.update_layout(
        barmode='stack',
        title='Unique Ships by Month and Port (Month)',
        yaxis_title='Number of Unique Ships',
        xaxis_title='Months',
        legend_title_text='Port: Total Ships (2019)')
    fig5.update_traces(selector={'name': name_gri},
                       texttemplate='%{text}%',
                       textposition='outside')  # add monthly percentages

    # Time of Day Trends
    hour_ships = ais_dict['review']['uship']['hour_ships']
    fig6 = go.Figure(go.Scatter(name='Day-Night', x=hour_ships.index,
                                y=hour_ships['count adj'], marker_color=tl))
    fig6.update_layout(
        title='Time of Day Trends',
        yaxis_title='Total Number Ships over Year',
        xaxis_title='Time of Day')

    # Total number of entries for each month: filtered
    ais_month = ((ais_dict['data'][['date', 'IMO']])
                 .groupby(pd.Grouper(key='date', freq='M'))
                 .count())
    ais_month.index = param['months']
    ais_month.rename(columns={'IMO': 'filtered'}, inplace=True)
    ais_month['all'] = ais_dict['review']['entries']
    fig7 = make_subplots(rows=1, cols=2)
    fig7.add_scatter(row=1, col=1, name='Total', x=param['months'],
                     y=ais_month['all'], marker_color=tl)
    fig7.add_scatter(row=1, col=2, name='Filtered', x=param['months'],
                     y=ais_month['filtered'], marker_color=yl)
    fig7.update_layout(
        title='AIS: Number of Entries',
        yaxis_title='Entries',
        xaxis_title='Months')


    # ICOADS
    # Filtering effectivness
    nanperc = icoads_dict['review']['filt nanperc']     # extract relevent

    # Total Datapoints
    fig8 = funnel(nanperc['len'].round(-3), nanperc['operation'])
    fig8.update_layout(
        title='Filtering Effectiveness: Total ICOADS Datapoints',
        yaxis_title='Operation')

    # Percentage of NaN entries for Key Values
    scatter = lambda name, y, color: go.Scatter(
        name=name, x=nanperc['operation'], y=nanperc[y], marker_color=color)
    fig9 = go.Figure(data=[scatter('Wind Speed', 'wind speed', tl),
                           scatter('Vis & Present Weather', 'vis', yl),
                           scatter('Wave Height', 'wave height', pl)])
    fig9.update_layout(
        title='Percentage of NaN entries for Key Values',
        xaxis_title='Operation',
        yaxis_title='%')

    # Box plots of filtered data for windspeed and visability
    fig10 = make_subplots(rows=1, cols=2)
    box = lambda name, x, color: go.Box(
        y=icoads_dict['data']['filtered'][x], name=name, marker_color=color)
    (fig10
     .add_trace(box('Wind Speed', 'wind speed', yl), row=1, col=1)
     .add_trace(box('Visability', 'vis', tl), row=1, col=2))
    fig10.update_layout(
        title='Distrubution of Entries (filtered dataset)',
        showlegend=False)
    (fig10
     .update_yaxes(title_text='Speed (m/s)', row=1, col=1)
     .update_yaxes(title_text='Visability (see report)', row=1, col=2))

    # monthly operatonal downtime due to weather
    # retrive data and frormat for plotting
    ic_month_ratio = (icoads_dict['results']['ratio']['month']
                      [['datetime', 'wind', 'vis', 'weather', 'check']])
    ic_month_ratio.datetime = ic_month_ratio.datetime.dt.month
    ic_month_ratio = (ic_month_ratio
                      .groupby('datetime')
                      .mean()
                      .drop('count', axis=1, level=1))
    ic_month_ratio.index = param['months']
    ic_month_ratio = round((1-ic_month_ratio)*100, 2)  # calc percentage
    scatter = lambda name, var, kind, color: go.Scatter(
        name=name, x=ic_month_ratio.index, y=ic_month_ratio[var][kind],
        marker_color=color)
    fig11 = go.Figure(data=[
        scatter('System Inoperable (All)', 'check', 'every', plf),
        scatter('Wind Speed Flag (All)', 'wind', 'flag', ylf),
        scatter('Visability Flag (All)', 'vis', 'flag', tlf),
        scatter('Weather Condition Flag', 'weather', 'flag', lb),
        scatter('System Inoperable (Avg)', 'check', 'avg', pl),
        scatter('Wind Speed Flag (Avg)', 'wind', 'avg', yl),
        scatter('Visability Flag (Avg)', 'vis', 'avg', tl)
        ])
    fig11.update_layout(
        title='Operational Downtime due to Weather by Month',
        xaxis_title='Month',
        yaxis_title='% Time Over Operationl Limit')

    # split all and avg across two subplots
    fig12 = make_subplots(rows=1, cols=2, shared_yaxes=True)
    (fig12
     .add_trace(scatter('System Inoperable (All)', 'check', 'every', plf),
                row=1, col=1)
     .add_trace(scatter('Wind Speed Flag (All)', 'wind', 'flag', ylf),
                row=1, col=1)
     .add_trace(scatter('Visability Flag (All)', 'vis', 'flag', tlf),
                row=1, col=1)
     .add_trace(scatter('Weather Condition Flag', 'weather', 'flag', lb),
                row=1, col=1)
     .add_trace(scatter('System Inoperable (Avg)', 'check', 'avg', pl),
                row=1, col=2)
     .add_trace(scatter('Wind Speed Flag (Avg)', 'wind', 'avg', yl),
                row=1, col=2)
     .add_trace(scatter('Visability Flag (Avg)', 'vis', 'avg', tl),
                row=1, col=2)
     .add_trace(scatter('Weather Condition Flag', 'weather', 'flag', lb),
                row=1, col=2))
    fig12.update_layout(
        title='Operational Downtime due to Weather by Month: Split',
        xaxis_title='Month',
        yaxis_title='% Time Over Operationl Limit')

    # Overall
    fig13 = go.Figure(data=[
        scatter('System Inoperable (All)', 'check', 'every', plf),
        scatter('System Inoperable (Avg)', 'check', 'avg', pl),
        go.Scatter(name='total (avg)',
                   x=ic_month_ratio.index,
                   y=ic_month_ratio['check']['avg'] +
                   (param['non_op_maint']*100),
                   marker_color=yl)])
    fig13.update_layout(
        title='Operational Downtime due to Weather by Month: Overall',
        xaxis_title='Month',
        yaxis_title='% Time Over Operationl Limit')


    # Test Numbers
    xnames = ('max', 'min')
    fig14 = go.Figure(data=[
        go.Bar(name='Normal', y=test_numbers['normal'], x=xnames,
               marker_color=yl),
        go.Bar(name='Adjusted', y=test_numbers['imovc adj'], x=xnames,
               marker_color=tl)])
    fig14.update_layout(
        title='Estimated Test Numbers (Year)',
        yaxis_title='Number of Ships Tested')
    fig14.update_traces(texttemplate='%{value}',
                        textposition='outside')

    # save to file as interactive html and png
    figs = {'AIS_Funnel Plots_Filtering Effectiveness': fig1,
            'AIS_Filtering Effectiveness_Unique Ships': fig2,
            'AIS_Scrubbing_Unique Destination': fig3,
            'AIS_Unique Ships by Month and Port (Year)': fig4,
            'AIS_Unique Ships by Month and Port (Month)': fig5,
            'AIS_Time of Day Trends': fig6,
            'AIS_Number of Entries': fig7,
            'ICOADS_Filtering Effectiveness_Total ICOADS Datapoints': fig8,
            'Percentage of NaN entries for Key Values': fig9,
            'Distrubution of Entries (filtered dataset)': fig10,
            'Operational Downtime by Month': fig11,
            'Operational Downtime by Month_Split': fig12,
            'Operational Downtime due to Weather by Month_Overall': fig13,
            'Estimated Yearly Test Number': fig14}
    for key, value in figs.items():
        value.write_image('plots/'+key+'.png', scale=6)
        value.write_html('plots/'+key+'.html')
