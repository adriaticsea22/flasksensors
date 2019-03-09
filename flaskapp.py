# flaskapp.py
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlab.figure import Figure
import io
from flask import Flask, render_template, send_file, make_response, request
import datetime
import os
import dateutil.parser
import requests
from config import API_KEY, MAC_ADDRESS
import pytz
import sqlite3
from appDhtWebHist import getLastData, getHistData, maxRowsTable

app = Flask(__name__)

if not os.path.isfile('data.db'):
	conn = sqlite3.connect('data.db')
	c = conn.cursor()
	c.execute("""CREATE TABLE data (
		Id INTEGER PRIMARY KEY AUTOINCREMENT,
		API_key text,
		date_time text,
		mac text,
		field text,
		data real
		)""")
	conn.commit()
	conn.close()
# def getLastData():
# 	for row in curs.execute("SELECT date_time, data, MAX(rowid) FROM data WHERE field='temp'"):
# 		time = dateutil.parser.parse(row[0])
# 		time_pst1=time.astimezone(pytz.timezone('US/Eastern'))
# 		time_stamp1 = t_pst1.strftime('%I:%M:%S %p %b %d, %Y')
# 		temp = str(round((float(row[1]) * 1.8) + 32))
# 	for row in curs.execute("SELECT date_time, data, MAX(rowid) FROM data WHERE field='hum'"):
# 		time = dateutil.parser.parse(row[0])
# 		time_pst2=time.astimezone(pytz.timezone('US/Eastern'))
# 		time_stamp2 = t_pst2.strftime('%I:%M:%S %p %b %d, %Y')
# 		hum = str(round((float(row[1]) * 1.8) + 32))
# 	return time_stamp1, temp, hum

@app.route("/update/API_key=<api_key>/mac=<mac>/field=<field>/data=<data>", methods=['GET'])
def write_data_point(api_key, mac, field, data):
	if (api_key == API_KEY and mac == MAC_ADDRESS):
		conn = sqlite3.connect('data.db')
		c = conn.cursor()
		t = datetime.datetime.now(tz=pytz.utc)
		date_time_str = t.isoformat()
		c.execute("INSERT INTO data VALUES(:Id, :API_key, :date_time, :mac, :field, :data)",
			{'Id': None, 'API_key': api_key, 'date_time': date_time_str, 'mac': mac, 'field': field, 'data': round(float(data), 4)})
		conn.commit()
		c.close()
		conn.close()
		return render_template("showrecent.html", data=data, time_stamp=date_time_str)
	else:
		return render_template("403.html")

@app.route('/plot/temp')
def plot_temp():
	times, temps, hums = getHistData(numSamples)
	ys = temps
	fig = Figure()
	axis = fig.add_subplot(1,1,1)
	axis.set_title("Temperature [°C]")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

@app.route('/plot/hum')
def plot_hum():
	times, temps, hums = getHistData(numSamples)
	ys = hums
	fig = Figure()
	axis = fig.add_subplot(1,1,1)
	axis.set_title("Humidity [%]")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

#def update(api_key, mac, field, data):
#	return render_template("update.html", data=data)

#@app.route("/gage/")
#def gage():
#	conn = sqlite3.connect('data.db')
#	c = conn.cursor()
#	c.execute("SELECT data, date_time, MAX(rowid) FROM data WHERE field=?", ('1',))
#	row1 = c.fetchone()
#	c.execute("SELECT data, date_time, MAX(rowid) FROM data WHERE field=?", ('2',))
#	row2 = c.fetchone()
#	c.close()
#	conn.close()
#	data1 = str(round((float(row1[0]) * 1.8) + 32))
#	data2 = str(round((float(row2[0]) * 1.8) + 32))
 #       time_str1 = row1[1]
  #      t1 = dateutil.parser.parse(time_str1)
   #     t_pst1 = t1.astimezone(pytz.timezone('US/Eastern'))
#    time_stamp1 = t_pst1.strftime('%I:%M:%S %p %b %d, %Y')
#        time_str2 = row2[1]
#        t2 = dateutil.parser.parse(time_str2)
#        t_pst2 = t2.astimezone(pytz.timezone('US/Eastern'))
#        time_stamp2 = t_pst2.strftime('%I:%M:%S %p %b %d, %Y')
 #      temp_c_in = 20
 #      temp_f = str(round(((9.0 / 5.0) * float(temp_c_in) + 32), 1)) + ' F'
#	return render_template("index_gage.html", data1=data1, time_stamp1=time_stamp1, data2=data2, time_stamp2=time_stamp2)
@app.route("/")
def index():
	conn = sqlite3.connect('data.db')
	c = conn.cursor()
	c.execute("SELECT data, date_time, MAX(rowid) FROM data WHERE field='temp'")
	row1 = c.fetchone()
	c.execute("SELECT data, date_time, MAX(rowid) FROM data WHERE field='hum'")
	row2 = c.fetchone()
	c.close()
	conn.close()
	data1 = str(round((float(row1[0]) * 1.8) + 32))
	data2 = str(round((float(row2[0]) * 1.8) + 32))
	time_str1 = row1[1]
	t1 = dateutil.parser.parse(time_str1)
	t_pst1 = t1.astimezone(pytz.timezone('US/Eastern'))
	time_stamp1 = t_pst1.strftime('%I:%M:%S %p %b %d, %Y')
	time_str2 = row2[1]
	t2 = dateutil.parser.parse(time_str2)
	t_pst2 = t2.astimezone(pytz.timezone('US/Eastern'))
	time_stamp2 = t_pst2.strftime('%I:%M:%S %p %b %d, %Y')
#	temp_c_in = 20
#	temp_f = str(round(((9.0 / 5.0) * float(temp_c_in) + 32), 1)) + ' F'
	return render_template("index_gage.html", data1=data1, time_stamp1=time_stamp1, data2=data2, time_stamp2=time_stamp2)
# Retrieve LAST data from database


if __name__ == "__main__":
	app.run(host='0.0.0.0')
