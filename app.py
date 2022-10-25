# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd

# Import sqlalchemy dependencies 
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import flask dependencies
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect database into classes
Base = automap_base()
Base.prepare(engine, reflect=True)

# Create variable references
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session link
session = Session(engine)

#################################################
# Flask Setup
#################################################

import app
print("example __name__ = %s", __name__)

if __name__ == "__main__":
    print("example is being run directly.")
else:
    print("example is being imported")

# Define the flask
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Welcome route
@app.route("/")
def welcome():
    return(
        f"'''<br/>"
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"'''")


# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():

	# Calculate the date one year ago from the most recent date
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

	# Query: get date and precipitation for prev_year
    precipitation = session.query(Measurement.date,Measurement.prcp) .\
        filter(Measurement.date >= prev_year).all()

	# Create dictionary w/ jsonify
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


# Stations route
@app.route("/api/v1.0/stations")
def stations():

    # Query database for all stations
    results = session.query(Station.station).all()

    # Unravel results into a list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)


# Monthly temp route
@app.route("/api/v1.0/tobs")
def temp_monthly():

    # Calculate date for previous year
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query primary station for all temp observation from previous year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    # Unravel results into 1-D array and convert into list
    temps = list(np.ravel(results))

    # jsonify the temp list and return
    return jsonify(temps=temps)


# Minimum, average, and maximum temperature routes
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

# Add parameters to 'stats()'
def stats(start=None, end=None):

	# Querry the minimum, average, and maximum temps into list called `sel`
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

	# Add `if-not` statement to note start and end date
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        temps = list(np.ravel(results))
    return jsonify(temps=temps)
