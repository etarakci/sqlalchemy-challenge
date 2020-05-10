# Import Flask
from flask import Flask, jsonify

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
import numpy as np
import pandas as pd

# set up database
engine = create_engine('sqlite:///Resources/hawaii.sqlite')
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to the tables
Measurement = Base.classes.measurements
Station = Base.classes.stations
# Create session from Python to the DB
session = Session(engine)

first_date = '2016-08-23'
last_date = '2017-08-23'
most_active_station = 'USC00519281'

# Create an app
app = Flask(__name__)

# Define static routes
@app.route("/")
def home():
    return (
        f"Welcome Hawaii's Climate Data<br/>"
        f"Available Routes:<br/>"
        f"Precipitation data between {first_date} and {last_date}: /api/v1.0/precipitation<br/>"
        f"Stations in Dataset: /api/v1.0/stations<br/>"
        f"Temperature observations from the most active station ({most_active_station}) \n between {first_date} and {last_date}: /api/v1.0/tobs<br/>"
        f"Temperature observations starting at <start>* date: /api/v1.0/<start><br/>"
        f"Temperature observations starting at <start>* date and ending at <end>* date: /api/v1.0/<start>/<end><br/>"
        f"* please format YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Convert the query results to a dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.
    
    prcp_result = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= first_date).all()
    session.close()

    prcp_dict = {}
    for p in prcp_result:
        prcp_dict[p[0]] = p[1]
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset
    station_result = session.query(func.distinct(Station.station,Station.name)).all()
    session.close()
    return jsonify(list(np.ravel(station_result)))

@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations of the most active station for the last year of data.
    # Return a JSON list of temperature observations (TOBS) for the previous year.
    tobs_result = session.query(Measurement.date,Measurement.tobs).filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= first_date).all()
    session.close()
    return jsonify(list(np.ravel(tobs_result)))

@app.route("/api/v1.0/<start>")
def start(start):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
    # for a given start or start-end range.   
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    start_tobs_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs))\
        .filter(Measurement.date >= start).all()
    session.close()
    return jsonify(start_tobs_results)

@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates 
    # between the start and end date inclusive
    start_end_tobs_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs))\
        .filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    return jsonify(start_end_tobs_results)

# Define main behavior
if __name__ == "__main__":
    app.run(debug=True)