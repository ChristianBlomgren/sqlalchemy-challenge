# Import the dependencies.
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()
# reflect the tables
base.prepare(autoload_with=engine)

# Save references to each table
measurement = base.classes.measurement
station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

#Home Page Set Up
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

#Pulling last year of precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)
    
    results = session.query(measurement.station, measurement.date, measurement.prcp) \
              .filter(measurement.date >= '2016-08-23') \
              .order_by(measurement.date).all()
              
    session.close()
    
    precipitation_data = list(np.ravel(results))
    
    return jsonify(precipitation_data)
 
#List of stations   
@app.route("/api/v1.0/stations")
def station_list():
   
    session = Session(engine)

    results = session.query(station.station).all()
              

    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

#Pulling last year of temperature data from the most popular station
@app.route("/api/v1.0/tobs")
def most_active_station_tobs():
    
    session = Session(engine)
    
    station_activity = session.query(measurement.station, func.count(measurement.station)) \
                       .group_by(measurement.station) \
                       .order_by(func.count(measurement.station).desc())
    
    most_active_station_id = station_activity.first()[0]
    
    results = session.query(measurement.station, measurement.date, measurement.tobs) \
              .filter(measurement.station == most_active_station_id) \
              .filter(measurement.date >= '2016-08-23').all()
    
    session.close()
    
    most_active_station_tobs = list(np.ravel(results))
    
    return jsonify(most_active_station_tobs)

#Taking date that is input and returning a temperature analysis  
@app.route("/api/v1.0/start")
def calculate_temperatures_start():
   #Set up a request for a specific start date
   #How to search: /api/v1.0/start?start_date=year-month-day
   start_date = request.args.get('start_date')
   
   session=Session(engine)
   
   #creating a query to use in next two functions
   query = session.query(func.min(measurement.tobs).label('TMIN'),
                         func.avg(measurement.tobs).label('TAVG'),
                         func.max(measurement.tobs).label('TMAX'))
   
   #Pull data from all dates after specified start date
   if start_date:
       result = query.filter(measurement.date >= start_date).all()

   # Convert the result to a list of dictionaries
   result_list = []
   for row in result:
       result_list.append({
           'TMIN': row.TMIN,
           'TAVG': row.TAVG,
           'TMAX': row.TMAX
       })

   return result_list

@app.route("/api/v1.0/start/end")
def calculate_temperatures_start_end():
    #Set up request(s) for specific start and end dates
    #How to search: /api/v1.0/start/end?start_date=year-month-day&end_date=year-month-day
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    session=Session(engine)
    
    #creating a query to use in next two functions
    query = session.query(func.min(measurement.tobs).label('TMIN'),
                          func.avg(measurement.tobs).label('TAVG'),
                          func.max(measurement.tobs).label('TMAX'))
    
    #Pull data from all dates within the specified range
    if end_date:
        result = query.filter(measurement.date.between(start_date, end_date)).all()
    else:
        result = query.filter(measurement.date >= start_date).all()

    # Convert the result to a list of dictionaries
    result_list = []
    for row in result:
        result_list.append({
            'TMIN': row.TMIN,
            'TAVG': row.TAVG,
            'TMAX': row.TMAX
        })

    return result_list

if __name__ == '__main__':
    app.run(debug=True)