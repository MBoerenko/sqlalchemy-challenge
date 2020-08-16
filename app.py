#Import dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

####################################################
# Flask Setup
####################################################
app = Flask(__name__)


####################################################
# Flask Routes - List all routes that are available
####################################################

@app.route("/")
def welcome():
    """List all available api routes for Hawaii climate data."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start date<br/>"
        f"/api/v1.0/start date / end date<end>"
    )

####################################################
#/api/v1.0/precipitation
####################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation"""
    # Query all preceipitation values for the last year
    prcp = (session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23')
         .order_by(Measurement.date).all())

    #Convert the query results to a dictionary using date 
    # as the key and prcp as the value.
    all_prcp = list(np.ravel(prcp))

    #Return the JSON representation of your dictionary.
    return jsonify(all_prcp)

####################################################
#/api/v1.0/stations
####################################################
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query all stations
    station_list = (session.query(Measurement.station).group_by(Measurement.station).all())

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station_list))

    #Return the JSON representation of your dictionary.
    return jsonify(all_stations)

####################################################
#/api/v1.0/tobs
####################################################
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperatures"""
    # Query the dates and temperature observations of the most 
    # active station for the last year of data.
    temp = session.query(Measurement.station, Measurement.tobs, Measurement.date).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= '2016-08-23').order_by(Measurement.tobs).all()

    # Convert list of tuples into normal list
    year_of_temps = list(np.ravel(temp))

    #Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(year_of_temps)

####################################################
#/api/v1.0/<start>
#/api/v1.0/<start>/<end>
####################################################
@app.route("/api/v1.0/<start>", defaults = {'end':None})
@app.route("/api/v1.0/<start>/<end>")
def statistics(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Return a JSON list of the minimum temperature, the average temperature, and the max 
    # temperature for a given start or start-end range.
    #When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater 
    # than and equal to the start date.
    #When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates 
    # between the start and end date inclusive.
    query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
    query = query.filter(Measurement.date >= start)

    if end is not None:
        query = query.filter(Measurement.date <= end)

    temp_dates = query.all()

    #Clean up return
    (tmin, tavg, tmax) = temp_dates[0]

     # Close the session
    session.close()

    return jsonify({'Minimum Temp' : tmin, 'Average Temp' : tavg, 'Maximum Temp' : tmax})

if __name__ == '__main__':
    app.run(debug=True)
