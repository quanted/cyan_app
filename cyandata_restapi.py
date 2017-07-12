"""
Cyan REST API
description: Rest endpoints for accessing sqlite database containing cyan data processed using Google Earth Engine.
database file: cyan.db
date: 07-11-2017
author: deron smith
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import sqlite3
import os
from datetime import datetime, timedelta

base_metadata = {
    "metaInfo": {
        "model": "cyan",
        "collection": "qed",
        "modelVersion": 1.0,
        "description": "The Cyanobacteria Assessment Network (CyAN) /state endpoint provides weekly "
                       "estimates and summary statistics for the concentration of cyanobacteria (cells/ml) for each"
                       "state in the continental United States. "
                       "This dataset was produced through partnership with the National Oceanic and Atmospheric "
                       "Administration (NOAA), the National Aeronautics and Space Administration (NASA), the "
                       "United States Geological Survey (USGS), and the United States Environmental Protection "
                       "Agency (USEPA). This cyanobacteria dataset was derived using the European Space Agency "
                       "(ESA) Envisat satellite and 300x300 meter MEdium Resolution Imaging Spectrometer (MERIS) satellite"
                       " imagery.",
        "status": "Finished",
        "timestamp": "2017-06-29T13:37:07Z",
        "url": {
            "type": "application/json"
        }
    }
}


@require_GET
def getcyan_state_data(request, model='', state='', header=''):
    """
    Rest endpoint for retrieving cyan data based on a specified state, aggregated data for the whole state.
    State argument takes a state abbreviation, will be testing using state name as well.
    :param request: Default request.
    :param model: Cyan
    :param state: Endpoint argument variable, state name abbreviation.
    :param header: Default header.
    :return: JSON string
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "cyan.db")
    db_con = sqlite3.connect(db_path)
    db_con.row_factory = dict_factory
    c = db_con.cursor()
    # Place state variable into a tuple before inserting into query request, prevents sql vulnerability.
    if len(state) != 2:
        return JsonResponse({"error": "argument error: state value provided was not valid, please provide a valid state"
                                      " abbreviation. Provided value = " + state})
    # state name
    c.execute("SELECT state_name FROM states WHERE state_abbr=?", (state,))
    state_name = c.fetchall()

    # number of lakes in the state
    c.execute("SELECT count(comid) FROM state_lakes WHERE state_abbr=?", (state,))
    nLakes = c.fetchall()

    # area of the state
    c.execute("SELECT sqmi FROM states WHERE state_abbr=?", (state,))
    state_area = c.fetchall()

    # lake area in state
    c.execute("SELECT sum(areasqkm) FROM lakes INNER JOIN state_lakes WHERE lakes.comid = state_lakes.comid"
              " AND state_lakes.state_abbr=?", (state,))
    lake_area = c.fetchall()

    # Mean CI for the state
    c.execute("SELECT avg(mean) FROM cyan_lakes INNER JOIN state_lakes WHERE cyan_lakes.comid = state_lakes.comid"
              " AND state_lakes.state_abbr=?", (state,))
    meanCI = c.fetchall()

    # data by date
    td = timedelta(days=6)
    # state_data = c.fetchall()
    c.execute("SELECT DISTINCT start_date FROM cyan_lakes")
    dates = c.fetchall()
    cyan_data = {}
    for date in dates:
        d = date['start_date']
        query = 'SELECT sum(high_extent), sum(moderate_extent), sum(low_extent), max(max), avg(mean), min(min) ' \
                'FROM cyan_lakes INNER JOIN state_lakes ' \
                'WHERE cyan_lakes.comid = state_lakes.comid AND state_lakes.state_abbr="' + state + \
                '" AND cyan_lakes.start_date =?'
        c.execute(query, (d,))
        date_data = c.fetchall()[0]
        cyan_data[(d[:10])] = {
            "start-date": d[:10],
            "end-date": (datetime.strptime(d[:10], '%Y-%m-%d') + td).strftime('%Y-%m-%d'),
            "maxCI": date_data["max(max)"],
            "meanCI": date_data["avg(mean)"],
            "minCI": date_data["min(min)"],
            "extentLow": date_data["sum(low_extent)"],
            "extentModerate": date_data["sum(moderate_extent)"],
            "extentHigh": date_data["sum(high_extent)"]
        }
        # TODO: extents are currently whole numbers, may need to change to a decimal percentage.
    metadata = base_metadata["metaInfo"]
    metadata["url"]["href"] = "https://qedinternal.epa.gov/cyan/rest/api/v1/(state)"
    data = {"metaInfo": metadata, "inputs": state, "outputs": {
        "stateInfo":
            {
                "state": state_name[0]["state_name"],
                "numbLakes": nLakes[0]['count(comid)'],
                "stateArea": float(state_area[0]['sqmi']) * 2.58999,
                "lakeArea": lake_area[0]['sum(areasqkm)'],
                "meanCI": meanCI[0]['avg(mean)']
            },
        "timeseriesData": cyan_data
    }
            }
    return JsonResponse(data)


@require_GET
def getcyan_state_lake_data(request, model='', state='', header=''):
    """
    Rest endpoint for retrieving cyan data based on a specified state, data for each lake.
    State argument takes a state abbreviation, will be testing using state name as well.
    :param request: Default request.
    :param model: Cyan
    :param state: Endpoint argument variable, state abbreviation.
    :param header: Default header.
    :return: JSON string.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "cyan.db")
    db_con = sqlite3.connect(db_path)
    db_con.row_factory = dict_factory
    c = db_con.cursor()
    # Place state variable into a tuple before inserting into query request, prevents sql vulnerability.
    if len(state) != 2:
        return JsonResponse({"error": "argument error: state value provided was not valid, please provide a valid state"
                                      " abbreviation. Provided value = " + state})
    # state name
    c.execute("SELECT state_name FROM states WHERE state_abbr=?", (state,))
    state_name = c.fetchall()

    # number of lakes in the state
    c.execute("SELECT count(comid) FROM state_lakes WHERE state_abbr=?", (state,))
    nLakes = c.fetchall()

    # area of the state
    c.execute("SELECT sqmi FROM states WHERE state_abbr=?", (state,))
    state_area = c.fetchall()

    # lake area in state
    c.execute("SELECT sum(areasqkm) FROM lakes INNER JOIN state_lakes WHERE lakes.comid = state_lakes.comid"
              " AND state_lakes.state_abbr=?", (state,))
    lake_area = c.fetchall()

    # Mean CI for the state
    c.execute("SELECT avg(mean) FROM cyan_lakes INNER JOIN state_lakes WHERE cyan_lakes.comid = state_lakes.comid"
              " AND state_lakes.state_abbr=?", (state,))
    meanCI = c.fetchall()

    cyan_lakes = {}
    c.execute("SELECT comid FROM state_lakes WHERE state_abbr=?", (state,))
    td = timedelta(days=6)
    for lake in c.fetchall():
        comid = lake['comid']
        c.execute("SELECT * FROM lakes WHERE comid=?", (comid,))
        lake_data = c.fetchall()
        c.execute("SELECT DISTINCT start_date FROM cyan_lakes WHERE comid=?", (comid,))
        dates = c.fetchall()
        cyan_data = {}
        for date in dates:
            d = date['start_date']
            query = 'SELECT high_extent, moderate_extent, low_extent, max, mean, min ' \
                    'FROM cyan_lakes WHERE comid =' + str(comid) + ' AND cyan_lakes.start_date =?'
            c.execute(query, (d,))
            date_data = c.fetchall()[0]
            cyan_data[(d[:10])] = {
                "start-date": d[:10],
                "end-date": (datetime.strptime(d[:10], '%Y-%m-%d') + td).strftime('%Y-%m-%d'),
                "maxCI": date_data["max"],
                "meanCI": date_data["mean"],
                "minCI": date_data["min"],
                "extentLow": date_data["low_extent"],
                "extentModerate": date_data["moderate_extent"],
                "extentHigh": date_data["high_extent"]
            }
        cyan_lakes[comid] = {"lake_metadata": lake_data[0], "cyandata": cyan_data}
    metadata = base_metadata["metaInfo"]
    metadata["url"]["href"] = "https://qedinternal.epa.gov/cyan/rest/api/v1/(state)/lakes"
    data = {"metaInfo": metadata, "inputs": state, "outputs": {
                "stateInfo":
                {
                    "state": state_name[0]["state_name"],
                    "numbLakes": nLakes[0]['count(comid)'],
                    "stateArea": float(state_area[0]['sqmi']) * 2.58999,
                    "lakeArea": lake_area[0]['sum(areasqkm)'],
                    "meanCI": meanCI[0]['avg(mean)']
                },
                "lakeData": cyan_lakes
            }
            }
    return JsonResponse(data)


@require_GET
def getcyan_lake_data(request, model='', lake='', header=''):
    """
    Rest endpoint for retrieving cyan data for a specified  lake.
    State argument takes a state abbreviation, will be testing using state name as well.
    :param request: Default request.
    :param model: Cyan
    :param lake: Endpoint argument variable, lake comid.
    :param header: Default header.
    :return: JSON string.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "cyan.db")
    db_con = sqlite3.connect(db_path)
    db_con.row_factory = dict_factory
    c = db_con.cursor()
    # Place state variable into a tuple before inserting into query request, prevents sql vulnerability.
    if lake.isnumeric():
        query = "SELECT * FROM lakes WHERE comid=?"
    else:
        return JsonResponse({"error": "argument error: state value provided was not valid, please provide a valid state"
                                      " abbreviation. Provided value = " + lake})
    # lake in states
    c.execute("SELECT state_abbr FROM state_lakes WHERE comid=?", (lake,))
    states = c.fetchall()

    # area of lake
    c.execute("SELECT areasqkm FROM lakes WHERE comid=?", (lake,))
    lake_area = c.fetchall()

    # name of lake
    c.execute("SELECT gnis_name FROM lakes WHERE comid=?", (lake,))
    lake_name = c.fetchall()

    # c.execute(query, (state,))

    # data by date
    td = timedelta(days=6)
    # state_data = c.fetchall()
    c.execute("SELECT DISTINCT start_date FROM cyan_lakes WHERE comid=?", (lake,))
    dates = c.fetchall()
    cyan_data = {}
    for date in dates:
        d = date['start_date']
        query = 'SELECT high_extent, moderate_extent, low_extent, max, mean, min ' \
                'FROM cyan_lakes WHERE comid =' + lake + ' AND cyan_lakes.start_date =?'
        c.execute(query, (d,))
        date_data = c.fetchall()[0]
        cyan_data[(d[:10])] = {
            "start-date": d[:10],
            "end-date": (datetime.strptime(d[:10], '%Y-%m-%d') + td).strftime('%Y-%m-%d'),
            "maxCI": date_data["max"],
            "meanCI": date_data["mean"],
            "minCI": date_data["min"],
            "extentLow": date_data["low_extent"],
            "extentModerate": date_data["moderate_extent"],
            "extentHigh": date_data["high_extent"]
        }
    metadata = base_metadata["metaInfo"]
    metadata["url"]["href"] = "https://qedinternal.epa.gov/cyan/rest/api/v1/lake/(comid)"
    data = {"metaInfo": metadata, "inputs": lake, "outputs": {
                "lakeInfo":
                {
                    "lakeCOMID": lake,
                    "GNISname": lake_name[0]['gnis_name'],
                    "lakeArea": lake_area[0]['areasqkm'],
                    "state": states[0]['state_abbr']
                },
                "lakeData": cyan_data
            }
            }
    return JsonResponse(data)


def dict_factory(cursor, row):
    """
    Returns db row as a dictionary.
    :param cursor: current cursor
    :param row: current row
    :return: dictionary
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
