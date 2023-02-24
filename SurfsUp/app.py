#1. Import Dependencies
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
#Set up Python SQL toolkit
engine = create_engine("sqlite:///hawaii.sqlite")
session = Session(engine)
Base = automap_base()
Base.prepare(autoload_with=engine)
Measurement = Base.classes.measurement
Station = Base.classes.station

#2. Create an app
app = Flask(__name__)

# 3. Define what to do when a user navigates to the Welcome page
@app.route("/")
def Welcome():
#display various available routes
    return (
         f"Welcome to my 'Climate App Home' page! <br/>"
         f"Available Routes: <br/>"
         f"/api/v1.0/precipitation <br/>"
         f"/api/v1.0/stations <br/>"
         f"/api/v1.0/tobs <br/>"
         f"/api/v1.0/temp/<start>/<end> <br/>"
    )

# 4. Define what to do when a user navigates to the /precipitation route
@app.route("/api/v1.0/precipitation")
def precip():
    #Get precipitation data for 12 months
    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    precip_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > previous_year).all()
    #transform into dictionary
    precip = {date: prcp for date, prcp in precip_data}
    session.close()
    return jsonify(precip)

# 5. Define what to do when a user hits the /stations route
#    Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations_list = list(np.ravel(session.query(Station.station).all()))
    session.close()
    return jsonify(stations_list)
#      
# 6. Define what to do when a user hits the /monthly temp route
# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def monthly_temp():
     station_data = session.query(Measurement.station,Measurement.date, Measurement.prcp, Measurement.tobs)
     station_data_df = pd.DataFrame(station_data, columns=['station','date','prcp','tobs'])
     most_active = list(np.ravel(station_data_df.loc[(station_data_df['station']=='USC00519281')]))
     session.close()
     return jsonify(most_active)

#7 Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/temp/<start>/<end>")
def Temps(start, end):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    temp_data = session.query(func.min(Measurement.tobs),\
                              func.max(Measurement.tobs), \
                              func.avg(Measurement.tobs)) \
                        .filter(Measurement.date.between(start_date, end_date)) \
                        .all()
    temp_list = list(np.ravel(temp_data))
    session.close()
    return jsonify(temp_list)

if __name__ == "__main__":
    app.run(debug=True)








