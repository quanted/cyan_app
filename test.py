from django.http import JsonResponse
from django.views.decorators.http import require_GET
import sqlite3
import os
import time
from datetime import datetime, timedelta
import csv


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

start = time.clock()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "cyan.db")
db_con = sqlite3.connect(db_path)
db_con.row_factory = dict_factory
c = db_con.cursor()

cyan_data = {}
output = open('document.csv','a')

c.execute("SELECT comid FROM lakes")
lakes = c.fetchall()
data = []
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

    q = "SELECT DISTINCT start_date from cyan_lakes WHERE " + " comid=?"
    c.execute(q, (comid,))
    dates = c.fetchall()
    nDates = len(dates)
    if len(dates) == 0:
        continue
    start_date = dates[0]
    end_date = dates[nDates - 1]

    query = 'SELECT max(max), avg(mean), min(min) ' \
            'FROM cyan_lakes WHERE ' + ' comid =?'
    c.execute(query, (comid,))
    cI_data = c.fetchall()[0]

    query = 'SELECT DISTINCT start_date, high_extent ' \
            'FROM cyan_lakes WHERE high_extent > 0 AND ' + ' comid =?'
    c.execute(query, (comid,))
    high_extent = c.fetchall()

    query = 'SELECT DISTINCT start_date, moderate_extent ' \
            'FROM cyan_lakes WHERE moderate_extent > 0 AND ' + ' comid =?'
    c.execute(query, (comid,))
    moderate_extent = c.fetchall()

    query = 'SELECT DISTINCT start_date, low_extent ' \
            'FROM cyan_lakes WHERE low_extent > 0 AND ' + ' comid =?'
    c.execute(query, (comid,))
    low_extent = c.fetchall()

    query = 'SELECT max(high_extent), avg(high_extent), max(moderate_extent), avg(moderate_extent), ' \
            'max(low_extent), avg(low_extent) FROM cyan_lakes WHERE ' + ' comid=?'
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

    myData = comid 
    # myData = comid + "," + lake_data[0]["gnis_name"] + "," + lake_data[0]["areasqkm"]
    data.append(myData)

    # data.append(str(cyan_data[comid]))
metadata = base_metadata["metaInfo"]
metadata["url"]["href"] = "https://qedinternal.epa.gov/cyan/rest/api/v1/lakes/info"
metadata["timestamp"] = str(datetime.utcnow()) + "Z"
end = time.clock()
metadata["query_time"] = end - start
data = {"metaInfo": metadata, "outputs": {"lakeData": cyan_data}}
output.close()