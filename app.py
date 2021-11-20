import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)


@app.route("/")
def home():
    print("Server accessed the Home route")
    return("Welcome to my Home page<br/>"
        f"<br>"
        f"Available Routes:<br/>"
        f"<br>"
        f"Precipitation Data: /api/v1.0/precipitation<br/>"
        f"Station Data: /api/v1.0/stations<br/>"
        f"Temperature Data: /api/v1.0/tobs<br/>"
        f"Search by Start Date: /api/v1.0/YYYY-MM-DD<br/>"
        f"Search Date Range: /api/v1.0/YYYY-MM-DD/YYYY-MM-DD")


@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    print("Server accessed Precipitation route")

    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    yearlyPrecip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).\
    order_by(Measurement.date.asc()).all()

    session.close()

    welcome = ("Welcome to the Precipitation page")
    rain = list(np.ravel(yearlyPrecip))

    return welcome, jsonify(rain)


@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    print("Server accessed Stations route")

    stationsQuery = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    session.close()

    stations = list(np.ravel(stationsQuery))

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    print("Server accessed Tobs route")

    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    mostActiveStation = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date > year_ago).\
    order_by(Measurement.date).all()

    session.close()

    active = list(np.ravel(mostActiveStation))

    return jsonify(active)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start(start = None, end = None):

    session = Session(engine)

    sel = [func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]

    if not end:
        station_averages = session.query(*sel).\
        filter(Measurement.date >= start).all()
    else:
        station_averages = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    dates = list(np.ravel(station_averages))    
    
    print("Server accessed Start/End route")

    session.close()

    return jsonify(dates)


if __name__ == "__main__":
    app.run(debug=True)

