import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import pandas as pd

# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():

    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )

@app.route("/api/v1.0/precipitation")
def rainfall():
#Convert the query results to a Dictionary using `date` as the key and `tobs` as the value
#Return the JSON representation of your dictionary.

#Returns temps and dates for station 7 between 8/23/2016 and 8/23/2017.
    SQL = '''SELECT     m.date, m.tobs
             FROM       Measurement m INNER JOIN Station s
             ON         m.station = s.station
             WHERE      m.date BETWEEN '2016-08-23' AND '8/23/2017'
             AND        s.id = 7'''

    date_tobs = pd.read_sql_query(SQL, engine)

    date_tobs = dict(zip(date_tobs.date, date_tobs.tobs))

    return (
        jsonify(date_tobs)
    )

@app.route("/api/v1.0/stations")
def stations():
#Return a JSON list of stations from the dataset.

    SQL = '''SELECT     s.Station, s.Name
             FROM       Station s'''

    stationlist = pd.read_sql_query(SQL, engine)

    return (
        stationlist.to_json(orient='index')
    )

@app.route("/api/v1.0/tobs")
def tobs():
#query for the dates and temperature observations from a year from the last data point.
#Return a JSON list of Temperature Observations (tobs) for the previous year (8/23/2016 to 8/23/2017)
#across all stations

    SQL = '''SELECT     m.tobs
             FROM       Measurement m
             WHERE      m.date BETWEEN '2016-08-23' AND '2017-08-23'
             '''

    tobs_df = pd.read_sql_query(SQL, engine)

    return (
        tobs_df.to_json(orient='index')
    )

@app.route("/api/v1.0/<start_date>")
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

def startonly(start_date):

    tripstart = session.query(Measurement.date,
                         func.min(Measurement.tobs).label("TMIN"), 
                         func.avg(Measurement.tobs).label("TAVG"), 
                         func.max(Measurement.tobs).label("TMAX")).\
                         filter(Measurement.date >= start_date).\
                         group_by(Measurement.date).\
                         order_by(Measurement.date).all()

    return (
        jsonify(tripstart)
    )


@app.route("/api/v1.0/<start_date>/<end_date>")
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

def startandend(start_date, end_date):

    tripstartandend = session.query(Measurement.date,
                         func.min(Measurement.tobs).label("TMIN"), 
                         func.avg(Measurement.tobs).label("TAVG"), 
                         func.max(Measurement.tobs).label("TMAX")).\
                         filter(Measurement.date >= start_date).\
                         filter(Measurement.date <= end_date).\
                         group_by(Measurement.date).\
                         order_by(Measurement.date).all()

    return (
        jsonify(tripstartandend)
    )


if __name__ == '__main__':
    app.run(debug=True)
