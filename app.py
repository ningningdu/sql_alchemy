import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    # Query precipation 
    # Calculate the date 1 year ago from the last data point in the database
    last_day = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_day_dt = dt.datetime.strptime(last_day[0], '%Y-%m-%d')
    year_ago= last_day_dt - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    query = session.query(measurement.date,measurement.prcp).filter(measurement.date>year_ago)
    session.close()
    # Convert to dict
    prcp_dict = dict(query.all())

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations_query= session.query(measurement.station).distinct(measurement.station).all()
    session.close()
    # Convert to dict
    stations= list(np.ravel(stations_query))

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # # Calculate the date 1 year ago from the last data point in the database
    last_day = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_day_dt = dt.datetime.strptime(last_day[0], '%Y-%m-%d')
    year_ago= last_day_dt - dt.timedelta(days=365)
    # find out which station is most active
    from sqlalchemy import desc

    number_of_station_query = (
        session.query(measurement.station, func.count(measurement.tobs).label("station_count"))
        .group_by(measurement.station)
        .order_by(desc("station_count"))
    )

    stations_results = number_of_station_query.all()
    # Query the dates and temperature observations of the most active station for the last year of data.
    query_temp_active_station = (session.query(measurement.date,measurement.tobs)
             .filter(measurement.station==stations_results[0][0])
             .filter(measurement.date>year_ago)
            )
    session.close()
    # Convert to dict
    tobs_dict = dict(query_temp_active_station.all())

    return jsonify(tobs_dict)


@app.route("/api/v1.0/<start>")
def SearchStart(start):
    session = Session(engine)
    

    dates = session.query(measurement.date).all()
    # first=min(np.ravel(dates))
    # last = max(np.ravel(dates))
    # if (start>=first) and (start<=last):
    query_temp= (
    session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs))
    .filter(measurement.date >= start)
            )
    temp_results = query_temp.all()
    temp_results = list(np.ravel(temp_results))

    return jsonify(temp_results)
    # else:
    #         return jsonify({"error": f"Start Date {start} not found."}), 404

    session.close()


@app.route("/api/v1.0/<start>/<end>")
def SearchDateRange(start,end):
    session = Session(engine)
    

    dates = session.query(measurement.date).all()
    # first=min(np.ravel(dates))
    # last = max(np.ravel(dates))
    # if (start>=first) and (start<=last):        
    query_temp= (
    session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs))
    .filter(measurement.date >= start)
    .filter(measurement.date <= end)
            )
    temp_results = query_temp.all()
    temp_results = list(np.ravel(temp_results))

    return jsonify(temp_results)
   # else:
   #         return jsonify({"error": f"Start Date {start} or end date {end} not found."}), 404

    session.close()

    

if __name__ == '__main__':
    app.run(debug=True)
