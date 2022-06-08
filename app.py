import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
       return (
        f"<h1>Welcome to my climate app API</h1>"

        f"<h3>To use, add the text below the description into the address bar - they are your Available Routes:</h3>"

        f"--------------------------------------------------------------------------------------------------------<br/>"
        f"Data for the preceeding 12 months from the latest results (23/08/2017):<br/>"
        f"--------------------------------------------------------------------------------------------------------<br/><br/>"
        f"<b><u>Precipitation Data:</b></u><br/><br/>"
        f"/api/v1.0/precipitation<br/><br/><br/>"

        f"<b><u>Full Listing of All Stations in the latest dataset:</b></u><br/><br/>"
        f"/api/v1.0/stations<br/><br/><br/>"

        f"<b><u>Data for the most active station over the time period:</b></u><br/><br/>"
        f"/api/v1.0/tobs<br/><br/><br/>"

        f"--------------------------------------------------------------------------------------------------------<br/>"
        f"Data for specific date and date range: (Available Dates 1/01/2010 - 23/08/2017)<br/>"
        f"--------------------------------------------------------------------------------------------------------<br/><br/>"

        f"<b><u>Specified Date:</u></b></b><br>"
        f"<i>Returns a JSON list of the minimum temperature (TMIN), the average temperature (TAVG),</i><br/>"
        f"<i>and the max temperature (TMAX) for all dates equal to or greater than the given date.<br/> (Enter Date in this format - <b><u><i>YYYY-MM-DD</b></u></i>)<br/><br>"

        f"</i>/api/v1.0/<start><br/><br/><br/>"

        f"<b><u>Start/End Date Range:</u></b></b><br>"
        f"<i>Returns a JSON list of the minimum temperature (TMIN), the average temperature (TAVG),</i><br/>"
        f"<i>and the max temperature (TMAX) for dates between a given start date and end date inclusive. <br/>"
        f"(Enter Dates in this format - <b><u><i>YYYY-MM-DD/YYYY-MM-DD</b></u></i>)<br/><br>"
        f"/api/v1.0/<start>/<end>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
   """Return the precipitation data for the last year"""
   # Calculate the date 1 year ago from last date in database
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   # Query for the date and precipitation for the last year
   precipitation = session.query(Measurement.date, Measurement.prcp).\
       filter(Measurement.date >= prev_year).all()
   session.close()
   # Dict with date as the key and prcp as the value
   precip = {date: prcp for date, prcp in precipitation}
   return jsonify(precip)
@app.route("/api/v1.0/stations")
def stations():
   """Return a list of stations."""
   results = session.query(Station.station).all()
   session.close()
   # Unravel results into a 1D array and convert to a list
   stations = list(np.ravel(results))
   return jsonify(stations=stations)
@app.route("/api/v1.0/tobs")
def temp_monthly():
   """Return the temperature observations (tobs) for previous year."""
   # Calculate the date 1 year ago from last date in database
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   # Query the primary station for all tobs from the last year
   results = session.query(Measurement.tobs).\
       filter(Measurement.station == 'USC00519281').\
       filter(Measurement.date >= prev_year).all()
   session.close()
   # Unravel results into a 1D array and convert to a list
   temps = list(np.ravel(results))
   # Return the results
   return jsonify(temps=temps)
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
   """Return TMIN, TAVG, TMAX."""
   # Select statement
   sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
   if not end:
       # start = dt.datetime.strptime(start, "%m/%d/%Y")
       # # calculate TMIN, TAVG, TMAX for dates greater than start
       # results = session.query(*sel).\
       #     filter(Measurement.date >= start).all()
       # # Unravel results into a 1D array and convert to a list
       # temps = list(np.ravel(results))
       # return jsonify(temps)
       start = dt.datetime.strptime(start, "%d%m%y")
       results = session.query(*sel).\
           filter(Measurement.date >= start).all()
       session.close()
       temps = list(np.ravel(results))
       return jsonify(temps)
   # calculate TMIN, TAVG, TMAX with start and stop
   start = dt.datetime.strptime(start, "%d%m%y")
   end = dt.datetime.strptime(end, "%d%m%y")
   results = session.query(*sel).\
       filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
   session.close()

   # Unravel results into a 1D array and convert to a list
   temps = list(np.ravel(results))
   return jsonify(temps=temps)

if __name__ == '__main__':
   app.run()


   # Just need to get the dates to work website using the date format in the file...