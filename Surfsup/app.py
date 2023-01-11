##########################
# Import Dependencies
##########################

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
from flask import Flask, jsonify

#######################
# Database Setup
#######################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()

# reflecting the table
base.prepare(autoload_with=engine)

#saving references to each table
Station = base.classes.station
Measurement = base.classes.measurement

# creating the session from python to the database
session=Session(engine)

########################
# Flask Setup
########################

app = Flask(__name__) 


#########################
# Flask Routes
#########################

@app.route("/")
def welcome():
    return (
        f"Weclome to the Hawaiian climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temps/start/end<br/>"
        f"<p> replace 'start' and 'end' with a date (YYYY-MM-DD).</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # creating a session
    session = Session(engine)

    # Query date and prcp from measurements table
    date_prcp = session.query(Measurement.date, Measurement.prcp).all()

    session.close()
    
    # dictionary to hold date and precipitation scores
    precip_dict = {date: pr for date, pr in precipitation}
    
    # returning jsonified dictionary
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    # create query for all stations
    stations_results = session.query(Station.station).all()

    session.close()

    # list of stations results
    stations = list(np.ravel(stations_results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def monthly_temp():

    # calculating date one year ago from most recent date in database
    last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    # querying for tobs of specific station
    tobs_year = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= last_year).all()
    
    session.close()

    temps = list(np.ravel(tobs_year))

    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temps/<start>/<end>")
def stats(start=None, end=None):
    
    # gathering min, avg, and max of tobs
    anaylze = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
       
        # start date 
        start = dt.datetime.strptime(start, "%Y-%m-%d")
        
        # query to gather min, avg, max of tobs
        results = session.query(*anaylze).\
            filter(Measurement.date >= start).all()
        
        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)
    
    # start/end in yyyy-mm-dd format 
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    end = dt.datetime.strptime(end, "%Y-%m-%d")

    # gather analysis for a specific date
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()

    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run()