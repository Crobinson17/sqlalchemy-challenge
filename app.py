from flask import Flask, jsonify
import numpy as np
import pandas as pd
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)

Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def intro():
    """List all apis"""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>")  
    
@app.route("/api/v1.0/precipitation")    
def precipitation():
    # Calculate the date 1 year ago from last date in database
    last_yr = dt.date(2017,8,23) - dt.timedelta(days = 365)
    last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # Query for the date
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > last_yr).order_by(Measurement.date).all()


    precipitation_data = []
    for i in precipitation:
        data = {}
        data['date'] = precipitation[0]
        data['precipitation'] = precipitation[1]
        precipitation_data.append(data)
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
#Return a JSON list of stations from the dataset.
    results = session.query(Station.station).all()
    stations= list(np.ravel(results))
    return jsonify(stations)
    
    @app.route("/api/v1.0/tobs")
    def tobs():
        """Return the temperature observations (tobs) for previous year."""
    # Calculate the date 1 year ago from last date in database
    last_yr = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query 
    results = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= last_yr).all()

    # Unravel results into a 1D array and convert to a list
    temp_observations = list(np.ravel(results))

    # Return the results
    return jsonify(temp_observations)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

 # The select statement
    select = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*select).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temp_observations = list(np.ravel(results))
        return jsonify(temp_observations)

    # start and stop
    results = session.query(*select).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temp_observations = list(np.ravel(results))
    return jsonify(temp_observations)

if __name__ == '__main__':
    app.run()
