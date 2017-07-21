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
import time
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

# TODO: Where possible, merge database queries.


@require_GET
def getcyan_state_data_yearly(request, model='', state='', year='', header=''):

    if len(year) != 4:
        return JsonResponse({"error": "argument error: year value provided was not valid, please provide a valid year."
                                      " Provided value = " + year})
    y_query = " WHERE start_date LIKE '%" + year + "%'"
    return getcyan_state_data(request, model, state, y_query, header)


@require_GET
def getcyan_state_data(request, model='', state='', yearly='', header=''):
    """
    Rest endpoint for retrieving cyan data based on a specified state, aggregated data for the whole state.
    State argument takes a state abbreviation, will be testing using state name as well.
    URL: https://qedinternal.epa.gov/cyan/rest/api/v1/(state)
    :param request: Default request.
    :param model: Cyan
    :param state: Endpoint argument variable, state name abbreviation.
    :param header: Default header.
    :return: JSON string
    """
    start = time.clock()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "cyan.db")
    db_con = sqlite3.connect(db_path)
    db_con.row_factory = dict_factory
    c = db_con.cursor()
    # Place state variable into a tuple before inserting into query request, prevents sql vulnerability.
    if len(state) != 2:
        return JsonResponse({"error": "argument error: state value provided was not valid, please provide a valid state"
                                      " abbreviation. Provided value = " + state})
    state = state.upper()
    # state name and area
    c.execute("SELECT state_name, sqmi FROM states WHERE state_abbr=?", (state,))
    state_info = c.fetchall()

    # number of lakes in the state
    c.execute("SELECT count(comid) FROM state_lakes WHERE state_abbr=?", (state,))
    nLakes = c.fetchall()

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
    q = "SELECT DISTINCT start_date FROM cyan_lakes " + yearly
    c.execute(q)
    dates = c.fetchall()
    cyan_data = {}

    for date in dates:
        d = date['start_date']
        if d == None:
            continue
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
            "extentLow": float(date_data["sum(low_extent)"]) * 300,
            "extentModerate": float(date_data["sum(moderate_extent)"]) * 300,
            "extentHigh": float(date_data["sum(high_extent)"]) * 300
        }
    metadata = base_metadata["metaInfo"]
    metadata["url"]["href"] = "https://qedinternal.epa.gov/cyan/rest/api/v1/(state)"
    metadata["timestamp"] = str(datetime.utcnow()) + "Z"
    end = time.clock()
    metadata["query_time"] = end - start
    data = {"metaInfo": metadata, "inputs": state, "outputs": {
        "stateInfo":
            {
                "state": state_info[0]["state_name"],
                "numbLakes": nLakes[0]['count(comid)'],
                "stateArea": float(state_info[0]['sqmi']) * 2.58999,
                "lakeArea": lake_area[0]['sum(areasqkm)'],
                "meanCI": meanCI[0]['avg(mean)']
            },
        "timeseriesData": cyan_data
        }
    }
    return JsonResponse(data)


@require_GET
def getcyan_state_lake_data_yearly(request, model='', state='', year='', header=''):

    if len(year) != 4:
        return JsonResponse({"error": "argument error: year value provided was not valid, please provide a valid year."
                                      " Provided value = " + year})
    y_query = " start_date LIKE '%" + str(year) + "%' AND "
    return getcyan_state_lake_data(request, model, state, y_query, header)


@require_GET
def getcyan_state_lake_data(request, model='', state='', yearly='', header=''):
    """
    Rest endpoint for retrieving cyan data based on a specified state, data for each lake.
    State argument takes a state abbreviation, will be testing using state name as well.
    URL: https://qedinternal.epa.gov/cyan/rest/api/v1/(state)/lakes
    :param request: Default request.
    :param model: Cyan
    :param state: Endpoint argument variable, state abbreviation.
    :param header: Default header.
    :return: JSON string.
    """
    start = time.clock()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "cyan.db")
    db_con = sqlite3.connect(db_path)
    db_con.row_factory = dict_factory
    c = db_con.cursor()
    # Place state variable into a tuple before inserting into query request, prevents sql vulnerability.
    if len(state) != 2:
        return JsonResponse({"error": "argument error: state value provided was not valid, please provide a valid state"
                                      " abbreviation. Provided value = " + state})
    state = state.upper()
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
        q = "SELECT DISTINCT start_date FROM cyan_lakes WHERE" + yearly + " comid=?"
        c.execute(q, (comid,))
        dates = c.fetchall()
        if len(dates) == 0:
            continue
        cyan_data = {}
        for date in dates:
            d = date['start_date']
            if d == None:
                continue
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
                "extentLow": float(date_data["low_extent"]) * 300,
                "extentModerate": float(date_data["moderate_extent"]) * 300,
                "extentHigh": float(date_data["high_extent"]) * 300
            }
        cyan_lakes[comid] = {"lake_metadata": lake_data[0], "cyandata": cyan_data}
    metadata = base_metadata["metaInfo"]
    metadata["url"]["href"] = "https://qedinternal.epa.gov/cyan/rest/api/v1/(state)/lakes"
    metadata["timestamp"] = str(datetime.utcnow()) + "Z"
    end = time.clock()
    metadata["query_time"] = end - start
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
def getcyan_state_lake_info_yearly(request, model='', state='', year='', header=''):

    if len(year) != 4:
        return JsonResponse({"error": "argument error: year value provided was not valid, please provide a valid year."
                                      " Provided value = " + year})
    y_query = " start_date LIKE '%" + str(year) + "%' AND "
    return getcyan_state_lake_info(request, model, state, y_query, header)


@require_GET
def getcyan_state_lake_info(request, model='', state='', yearly='', header=''):
    """
        Rest endpoint for retrieving cyan data statistics based on a specified state, data for each lake.
        State argument takes a state abbreviation, will be testing using state name as well.
        URL: https://qedinternal.epa.gov/cyan/rest/api/v1/(state)/lakes/info
        :param request: Default request.
        :param model: Cyan
        :param state: Endpoint argument variable, state abbreviation.
        :param header: Default header.
        :return: JSON string.
        """
    start = time.clock()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "cyan.db")
    db_con = sqlite3.connect(db_path)
    db_con.row_factory = dict_factory
    c = db_con.cursor()
    # Place state variable into a tuple before inserting into query request, prevents sql vulnerability.
    if len(state) != 2:
        return JsonResponse({"error": "argument error: state value provided was not valid, please provide a valid state"
                                      " abbreviation. Provided value = " + state})
    state = state.upper()
    # state name
    c.execute("SELECT state_name, sqmi FROM states WHERE state_abbr=?", (state,))
    state_data = c.fetchall()

    # number of lakes in the state
    c.execute("SELECT count(comid) FROM state_lakes WHERE state_abbr=?", (state,))
    nLakes = c.fetchall()

    # area of the state
    # c.execute("SELECT sqmi FROM states WHERE state_abbr=?", (state,))
    # state_area = c.fetchall()

    # lake area in state
    c.execute("SELECT sum(areasqkm) FROM lakes INNER JOIN state_lakes WHERE lakes.comid = state_lakes.comid"
              " AND state_lakes.state_abbr=?", (state,))
    lakes_area = c.fetchall()

    # Mean CI for the state
    q = "SELECT avg(mean) FROM cyan_lakes INNER JOIN state_lakes WHERE " + yearly + \
        " cyan_lakes.comid = state_lakes.comid AND state_lakes.state_abbr=?"
    c.execute(q, (state,))
    meanCI = c.fetchall()

    cyan_lakes = {}
    c.execute("SELECT comid FROM state_lakes WHERE state_abbr=?", (state,))
    td = timedelta(days=6)
    cyan_data = {}
    for lake in c.fetchall():
        comid = lake['comid']
        # lake in states
        c.execute("SELECT state_abbr FROM state_lakes WHERE comid=?", (comid,))
        states = c.fetchall()
        stateList = []
        for state in states:
            stateList.append(state["state_abbr"])
        # area of lake
        c.execute("SELECT areasqkm, gnis_name FROM lakes WHERE comid=?", (comid,))
        lake_data = c.fetchall()

        q = "SELECT DISTINCT start_date from cyan_lakes WHERE " + yearly + " comid=?"
        c.execute(q, (comid,))
        dates = c.fetchall()
        nDates = len(dates)
        if len(dates) == 0:
            continue
        start_date = dates[0]
        end_date = dates[nDates - 1]

        query = 'SELECT max(max), avg(mean), min(min) ' \
                'FROM cyan_lakes WHERE ' + yearly + ' comid =?'
        c.execute(query, (comid,))
        cI_data = c.fetchall()[0]

        query = 'SELECT DISTINCT start_date, high_extent ' \
                'FROM cyan_lakes WHERE ' + yearly + ' high_extent > 0 AND comid =?'
        c.execute(query, (comid,))
        high_extent = c.fetchall()

        query = 'SELECT DISTINCT start_date, moderate_extent ' \
                'FROM cyan_lakes WHERE ' + yearly + ' moderate_extent > 0 AND comid =?'
        c.execute(query, (comid,))
        moderate_extent = c.fetchall()

        query = 'SELECT DISTINCT start_date, low_extent ' \
                'FROM cyan_lakes WHERE ' + yearly + ' low_extent > 0 AND comid =?'
        c.execute(query, (comid,))
        low_extent = c.fetchall()

        query = 'SELECT max(high_extent), avg(high_extent), max(moderate_extent), avg(moderate_extent), ' \
                'max(low_extent), avg(low_extent) FROM cyan_lakes WHERE ' + yearly + ' comid=?'
        c.execute(query, (comid,))
        extent = c.fetchall()[0]

        # states.values() get values from list of dictionary.
        cyan_data[comid] = {
            "lake_info": {
                "lakeCOMID": comid,
                "GNISname": lake_data[0]["gnis_name"],
                "lakeArea": lake_data[0]["areasqkm"],
                "state": stateList,
                "start_date": start_date["start_date"],
                "end_date": end_date["start_date"]
            },
            "lake_cyan_info": {
                "maxCI": cI_data["max(max)"],
                "meanCI": cI_data["avg(mean)"],
                "minCI": cI_data["min(min)"],
                "freqHigh": len(high_extent) / nDates,
                "freqModerate": len(moderate_extent) / nDates,
                "freqLow": len(low_extent) / nDates,
                "maxHighExtent": float(extent["max(high_extent)"]) * 300,
                "meanHighExtent": float(extent["avg(high_extent)"]) * 300,
                "maxModerateExtent": float(extent["max(moderate_extent)"]) * 300,
                "meanModerateExtent": float(extent["avg(moderate_extent)"]) * 300,
                "maxLowExtent": float(extent["max(low_extent)"]) * 300,
                "meanLowExtent": float(extent["avg(low_extent)"]) * 300
            }
        }
    metadata = base_metadata["metaInfo"]
    metadata["url"]["href"] = "https://qedinternal.epa.gov/cyan/rest/api/v1/(state)/lakes/info"
    metadata["timestamp"] = str(datetime.utcnow()) + "Z"
    end = time.clock()
    metadata["query_time"] = end - start
    data = {"metaInfo": metadata, "inputs": state, "outputs": {
        "stateInfo":
            {
                "state": state_data[0]["state_name"],
                "numbLakes": nLakes[0]['count(comid)'],
                "stateArea": float(state_data[0]['sqmi']) * 2.58999,
                "lakeArea": lakes_area[0]['sum(areasqkm)'],
                "meanCI": meanCI[0]['avg(mean)']
            },
        "lakeData": cyan_data
        }
    }
    return JsonResponse(data)


@require_GET
def getcyan_lake_data_yearly(request, model='', lake='', year='', header=''):

    if len(year) != 4:
        return JsonResponse({"error": "argument error: year value provided was not valid, please provide a valid year."
                                      " Provided value = " + year})
    y_query = " start_date LIKE '%" + str(year) + "%' AND "
    return getcyan_lake_data(request, model, lake, y_query, header)


@require_GET
def getcyan_lake_data(request, model='', lake='', yearly='', header=''):
    """
    Rest endpoint for retrieving cyan data for a specified  lake.
    State argument takes a state abbreviation, will be testing using state name as well.
    URL: https://qedinternal.epa.gov/cyan/rest/api/v1/lake/(comid)
    :param request: Default request.
    :param model: Cyan
    :param lake: Endpoint argument variable, lake comid.
    :param header: Default header.
    :return: JSON string.
    """
    start = time.clock()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "cyan.db")
    db_con = sqlite3.connect(db_path)
    db_con.row_factory = dict_factory
    c = db_con.cursor()
    # Place state variable into a tuple before inserting into query request, prevents sql vulnerability.
    if lake.isnumeric():
        query = "SELECT * FROM lakes WHERE comid=?"
        c.execute(query, (lake,))
        lake_test = c.fetchall()
        if len(lake_test) == 0:
            return JsonResponse({"error": "comid error: No lakes found with the given comid. Provided comid = " + lake})
    else:
        return JsonResponse({"error": "argument error: comid value provided was not valid, please provide a comid"
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

    # data by date
    td = timedelta(days=6)
    # state_data = c.fetchall()
    q = "SELECT DISTINCT start_date FROM cyan_lakes WHERE " + yearly + " comid=?"
    c.execute(q, (lake,))
    dates = c.fetchall()
    cyan_data = {}
    for date in dates:
        d = date['start_date']
        if d == None:
            continue
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
            "extentLow": float(date_data["low_extent"]) * 300,
            "extentModerate": float(date_data["moderate_extent"]) * 300,
            "extentHigh": float(date_data["high_extent"]) * 300
        }
    metadata = base_metadata["metaInfo"]
    metadata["url"]["href"] = "https://qedinternal.epa.gov/cyan/rest/api/v1/lake/(comid)"
    metadata["timestamp"] = str(datetime.utcnow()) + "Z"
    end = time.clock()
    metadata["query_time"] = end - start
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


@require_GET
def getcyan_lake_info_yearly(request, model='', lake='', year='', header=''):

    if len(year) != 4:
        return JsonResponse({"error": "argument error: year value provided was not valid, please provide a valid year."
                                      " Provided value = " + year})
    y_query = " start_date LIKE '%" + str(year) + "%' AND "
    return getcyan_lake_info(request, model, lake, y_query, header)


@require_GET
def getcyan_lake_info(request, model='', lake='', yearly='', header=''):
    """
    Rest endpoint for retrieving cyan data statistics based on a specified lake comid.
    URL: https://qedinternal.epa.gov/cyan/rest/api/v1/(state)/lakes/info
    :param request: Default request.
    :param model: Cyan
    :param lake: Endpoint argument variable, lake comid.
    :param header: Default header.
    :return: JSON string.
    """
    start = time.clock()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "cyan.db")
    db_con = sqlite3.connect(db_path)
    db_con.row_factory = dict_factory
    c = db_con.cursor()
    # Place state variable into a tuple before inserting into query request, prevents sql vulnerability.
    if lake.isnumeric():
        query = "SELECT * FROM lakes WHERE comid=?"
        c.execute(query, (lake,))
        lake_test = c.fetchall()
        if len(lake_test) == 0:
            return JsonResponse({"error": "comid error: No lakes found with the given comid. Provided comid = " + lake})
    else:
        return JsonResponse({"error": "argument error: comid value provided was not valid, please provide a comid"
                                      " abbreviation. Provided value = " + lake})
    cyan_data = {}

    # lake in states
    c.execute("SELECT state_abbr FROM state_lakes WHERE comid=?", (lake,))
    states = c.fetchall()
    stateList = []
    for state in states:
        stateList.append(state["state_abbr"])

    # area of lake
    c.execute("SELECT areasqkm, gnis_name FROM lakes WHERE comid=?", (lake,))
    lake_data = c.fetchall()

    q = "SELECT DISTINCT start_date from cyan_lakes WHERE " + yearly + " comid=?"
    c.execute(q, (lake,))
    dates = c.fetchall()
    nDates = len(dates)
    start_date = dates[0]
    end_date = dates[nDates - 1]

    query = 'SELECT max(max), avg(mean), min(min) ' \
            'FROM cyan_lakes WHERE ' + yearly + ' comid =?'
    c.execute(query, (lake,))
    cI_data = c.fetchall()[0]

    query = 'SELECT DISTINCT start_date, high_extent ' \
            'FROM cyan_lakes WHERE high_extent > 0 AND ' + yearly + ' comid =?'
    c.execute(query, (lake,))
    high_extent = c.fetchall()

    query = 'SELECT DISTINCT start_date, moderate_extent ' \
            'FROM cyan_lakes WHERE moderate_extent > 0 AND ' + yearly + ' comid =?'
    c.execute(query, (lake,))
    moderate_extent = c.fetchall()

    query = 'SELECT DISTINCT start_date, low_extent ' \
            'FROM cyan_lakes WHERE low_extent > 0 AND ' + yearly + ' comid =?'
    c.execute(query, (lake,))
    low_extent = c.fetchall()

    query = 'SELECT max(high_extent), avg(high_extent), max(moderate_extent), avg(moderate_extent), ' \
            'max(low_extent), avg(low_extent) FROM cyan_lakes WHERE ' + yearly + ' comid=?'
    c.execute(query, (lake,))
    extent = c.fetchall()[0]

    # states.values() get values from list of dictionary.
    cyan_data[lake] = {
        "lake_info": {
            "lakeCOMID": lake,
            "GNISname": lake_data[0]["gnis_name"],
            "lakeArea": lake_data[0]["areasqkm"],
            "state": stateList,
            "start_date": start_date["start_date"],
            "end_date": end_date["start_date"]
        },
        "lake_cyan_info": {
            "maxCI": cI_data["max(max)"],
            "meanCI": cI_data["avg(mean)"],
            "minCI": cI_data["min(min)"],
            "freqHigh": len(high_extent) / nDates,
            "freqModerate": len(moderate_extent) / nDates,
            "freqLow": len(low_extent) / nDates,
            "maxHighExtent": float(extent["max(high_extent)"]) * 300,
            "meanHighExtent": float(extent["avg(high_extent)"]) * 300,
            "maxModerateExtent": float(extent["max(moderate_extent)"]) * 300,
            "meanModerateExtent": float(extent["avg(moderate_extent)"]) * 300,
            "maxLowExtent": float(extent["max(low_extent)"]) * 300,
            "meanLowExtent": float(extent["avg(low_extent)"]) * 300
        }
    }
    metadata = base_metadata["metaInfo"]
    metadata["url"]["href"] = "https://qedinternal.epa.gov/cyan/rest/api/v1/lake/(comid)/info"
    metadata["timestamp"] = str(datetime.utcnow()) + "Z"
    end = time.clock()
    metadata["query_time"] = end - start
    data = {"metaInfo": metadata, "inputs": lake, "outputs": {
        "lakeData": cyan_data
    }
            }
    return JsonResponse(data)


@require_GET
def getcyan_all_lake_info_yearly(request, model='',year='', header=''):

    if len(year) != 4:
        return JsonResponse({"error": "argument error: year value provided was not valid, please provide a valid year."
                                      " Provided value = " + year})
    y_query = " start_date LIKE '%" + str(year) + "%' AND "
    return getcyan_all_lake_info(request, model, y_query, header)


@require_GET
def getcyan_all_lake_info(request, model='', yearly='', header=''):
    """
    Rest endpoint for retrieving cyan data statistics based on a specified lake comid.
    URL: https://qedinternal.epa.gov/cyan/rest/api/v1/lakes/info
    :param request: Default request.
    :param model: Cyan
    :param header: Default header.
    :return: JSON string.
    """
    start = time.clock()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "cyan.db")
    db_con = sqlite3.connect(db_path)
    db_con.row_factory = dict_factory
    c = db_con.cursor()

    cyan_data = {}

    c.execute("SELECT comid FROM lakes")
    lakes = c.fetchall()

    for lake in lakes:
        # lake in states
        comid = lake["comid"]
        c.execute("SELECT state_abbr FROM state_lakes WHERE comid=?", (comid,))
        states = c.fetchall()
        stateList = []
        for state in states:
            stateList.append(state["state_abbr"])

        # area of lake
        c.execute("SELECT areasqkm, gnis_name FROM lakes WHERE comid=?", (comid,))
        lake_data = c.fetchall()

        q = "SELECT DISTINCT start_date from cyan_lakes WHERE " + yearly + " comid=?"
        c.execute(q, (comid,))
        dates = c.fetchall()
        nDates = len(dates)
        if len(dates) == 0:
            continue
        start_date = dates[0]
        end_date = dates[nDates - 1]

        query = 'SELECT max(max), avg(mean), min(min) ' \
                'FROM cyan_lakes WHERE ' + yearly + ' comid =?'
        c.execute(query, (comid,))
        cI_data = c.fetchall()[0]

        query = 'SELECT DISTINCT start_date, high_extent ' \
                'FROM cyan_lakes WHERE high_extent > 0 AND ' + yearly + ' comid =?'
        c.execute(query, (comid,))
        high_extent = c.fetchall()

        query = 'SELECT DISTINCT start_date, moderate_extent ' \
                'FROM cyan_lakes WHERE moderate_extent > 0 AND ' + yearly +' comid =?'
        c.execute(query, (comid,))
        moderate_extent = c.fetchall()

        query = 'SELECT DISTINCT start_date, low_extent ' \
                'FROM cyan_lakes WHERE low_extent > 0 AND ' + yearly + ' comid =?'
        c.execute(query, (comid,))
        low_extent = c.fetchall()

        query = 'SELECT max(high_extent), avg(high_extent), max(moderate_extent), avg(moderate_extent), ' \
                'max(low_extent), avg(low_extent) FROM cyan_lakes WHERE ' + yearly + ' comid=?'
        c.execute(query, (comid,))
        extent = c.fetchall()[0]

        # states.values() get values from list of dictionary.
        cyan_data[comid] = {
            "lake_info": {
                "lakeCOMID": comid,
                "GNISname": lake_data[0]["gnis_name"],
                "lakeArea": lake_data[0]["areasqkm"],
                "state": stateList,
                "start_date": start_date["start_date"],
                "end_date": end_date["start_date"]
            },
            "lake_cyan_info": {
                "maxCI": cI_data["max(max)"],
                "meanCI": cI_data["avg(mean)"],
                "minCI": cI_data["min(min)"],
                "freqHigh": len(high_extent) / nDates,
                "freqModerate": len(moderate_extent) / nDates,
                "freqLow": len(low_extent) / nDates,
                "maxHighExtent": float(extent["max(high_extent)"]) * 300,
                "meanHighExtent": float(extent["avg(high_extent)"]) * 300,
                "maxModerateExtent": float(extent["max(moderate_extent)"]) * 300,
                "meanModerateExtent": float(extent["avg(moderate_extent)"]) * 300,
                "maxLowExtent": float(extent["max(low_extent)"]) * 300,
                "meanLowExtent": float(extent["avg(low_extent)"]) * 300
            }
        }
    metadata = base_metadata["metaInfo"]
    metadata["url"]["href"] = "https://qedinternal.epa.gov/cyan/rest/api/v1/lakes/info"
    metadata["timestamp"] = str(datetime.utcnow()) + "Z"
    end = time.clock()
    metadata["query_time"] = end - start
    data = {"metaInfo": metadata, "outputs": {"lakeData": cyan_data}}
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
