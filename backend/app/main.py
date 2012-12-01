# do not change or move the following lines if you still want to use the box.py auto generator
from app import app, db
from models import Toilet, User, Facility

# you can freely change the lines below
from flask import render_template
from flask import json
from flask import session
from flask import url_for
from flask import redirect
from flask import request
from flask import abort
from flask import Response
import logging
import datetime
import hashlib
import math
# define global variables here

# define functions here
def distance(point1, point2):
	lat1, lon1, lat2, lon2 = map(math.radians, [float(point1[0]), float(point1[1]), float(point2[0]), float(point2[1])])
	dlat = lat2 - lat1
	dlon = lon2 - lon1
	a = (math.sin(dlat/2)**2) + (math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
	c = 2 * math.asin(math.sqrt(a))
	km = 6371 * c
	return km

# home root controller
@app.route('/')
def index():
	# define your controller here
	return render_template('index.html')


########### toilet data model controllers area ###########
@app.route('/search/<latlong_string>')
def search_toilet(latlong_string):
	#latlong_string = request.values.get('latlong')
	toilets = []
	#latlong_string = '-6.363603,106.828285'
	latlong = latlong_string.split(',')
	toilet_list = Toilet.query.all()
	for toilet in toilet_list:
		db_pair = []
		db_pair.append(toilet.toilet_lat)
		db_pair.append(toilet.toilet_long)
		delta = distance(latlong,db_pair)
		if delta <= 1:
			toilets.append(toilet)
	result = json.dumps([toilet.dto() for toilet in toilets])
	return result


@app.route('/data/toilet/')
def data_toilet():
	# this is the controller for JSON data access
	toilet_list = Toilet.query.all()

	if toilet_list:
		json_result = json.dumps([toilet.dto() for toilet in toilet_list])
	else:
		json_result = json.dumps(dict(toilet=None))

	return json_result

@app.route('/toilet/')
def toilet_view_controller():
	#this is the controller to view all data in the model
	toilet_list = Toilet.query.all()

	if toilet_list:
		toilet_entries = [toilet.dto() for toilet in toilet_list]
	else:
		toilet_entries = None

	return render_template('toilet.html',toilet_entries = toilet_entries)

@app.route('/toilet/<inputid>')
def get_single_toilet(inputid):
	single_toilet = Toilet.query.filter(Toilet.toilet_id == inputid).first()
	if single_toilet:
		toilet = single_toilet.dto()
		facility_list = single_toilet.facility.one()
		logging.error(facility_list)
		if facility_list:
			facility = facility_list.dto()
		else:
			facility = None
	else:
		toilet = None
		facility = None
	result = json.dumps(dict(toilet=toilet,facility=facility))
	return result

@app.route('/toilet/add/')
def toilet_add_controller():
	#this is the controller to add new model entries
	return render_template('toilet_add.html')

@app.route('/toilet/create/',methods=['POST','GET'])
def toilet_create_data_controller():
	# this is the toilet data create handler
	toilet_name = request.values.get('toilet_name')
	toilet_lat = request.values.get('toilet_lat')
	toilet_long = request.values.get('toilet_long')
	toilet_address = request.values.get('toilet_address')
	toilet_current_rating = request.values.get('toilet_current_rating')
	user_id = request.values.get('user_id')

	new_toilet = Toilet(
									toilet_name = toilet_name,
									toilet_lat = toilet_lat,
									toilet_long = toilet_long,
									toilet_address = toilet_address,
									toilet_current_rating = toilet_current_rating,
									added_on = datetime.datetime.now(),
									user_id = user_id
								)

	db.session.add(new_toilet)
	db.session.commit()

	return 'data input successful <a href="/toilet/">back to Entries</a>'

@app.route('/toilet/edit/<id>')
def toilet_edit_controller(id):
	#this is the controller to edit model entries
	toilet_item = Toilet.query.filter(Toilet.toilet_id == id).first()
	return render_template('toilet_edit.html', toilet_item = toilet_item)

@app.route('/toilet/update/<id>',methods=['POST','GET'])
def toilet_update_data_controller(id):
	# this is the toilet data update handler
	toilet_name = request.values.get('toilet_name')
	toilet_lat = request.values.get('toilet_lat')
	toilet_long = request.values.get('toilet_long')
	toilet_address = request.values.get('toilet_address')
	toilet_current_rating = request.values.get('toilet_current_rating')
	added_on = request.values.get('added_on')
	user_id = request.values.get('user_id')
	toilet_item = Toilet.query.filter(Toilet.toilet_id == id).first()
	toilet_item.toilet_name = toilet_name
	toilet_item.toilet_lat = toilet_lat
	toilet_item.toilet_long = toilet_long
	toilet_item.toilet_address = toilet_address
	toilet_item.toilet_current_rating = toilet_current_rating
	toilet_item.added_on = added_on
	toilet_item.user_id = user_id

	db.session.add(toilet_item)
	db.session.commit()

	return 'data update successful <a href="/toilet/">back to Entries</a>'

@app.route('/toilet/delete/<id>')
def toilet_delete_controller(id):
	#this is the controller to delete model entries
	toilet_item = Toilet.query.filter(Toilet.id == id).first()

	db.session.delete(toilet_item)
	db.session.commit()

	return 'data deletion successful <a href="/toilet/">back to Entries</a>'



########### user data model controllers area ###########

@app.route('/data/user/')
def data_user():
	# this is the controller for JSON data access
	user_list = User.query.all()

	if user_list:
		json_result = json.dumps([user.dto() for user in user_list])
	else:
		json_result = json.dumps(dict(user=None))

	return json_result

@app.route('/user/')
def user_view_controller():
	#this is the controller to view all data in the model
	user_list = User.query.all()

	if user_list:
		user_entries = [user.dto() for user in user_list]
	else:
		user_entries = None

	return render_template('user.html',user_entries = user_entries)

@app.route('/user/<inputid>')
def get_single_user(inputid):
	single_user = User.query.filter(User.user_id == inputid).first()
	result = json.dumps(single_user.dto())

	return result

@app.route('/user/add/')
def user_add_controller():
	#this is the controller to add new model entries
	return render_template('user_add.html')

@app.route('/user/create/',methods=['POST','GET'])
def user_create_data_controller():
	# this is the user data create handler
	first_name = request.values.get('first_name')
	last_name = request.values.get('last_name')
	email = request.values.get('email')
	password = request.values.get('password')
	hash_password = hashlib.md5()
	hash_password.update(password)
	new_user = User(
									first_name = first_name,
									last_name = last_name,
									email = email,
									password = hash_password.hexdigest(),
									registered_on = datetime.datetime.now()
								)

	db.session.add(new_user)
	db.session.commit()

	return 'data input successful <a href="/user/">back to Entries</a>'

@app.route('/user/edit/<id>')
def user_edit_controller(id):
	#this is the controller to edit model entries
	user_item = User.query.filter(User.user_id == id).first()
	return render_template('user_edit.html', user_item = user_item)

@app.route('/user/update/<id>',methods=['POST','GET'])
def user_update_data_controller(id):
	# this is the user data update handler
	first_name = request.values.get('first_name')
	last_name = request.values.get('last_name')
	email = request.values.get('email')
	password = request.values.get('password')
	hash_password = hashlib.md5()
	hash_password.update(password)
	user_item = User.query.filter(User.user_id == id).first()
	user_item.first_name = first_name
	user_item.last_name = last_name
	user_item.email = email
	user_item.password = hash_password


	db.session.add(user_item)
	db.session.commit()

	return 'data update successful <a href="/user/">back to Entries</a>'

@app.route('/user/delete/<id>')
def user_delete_controller(id):
	#this is the controller to delete model entries
	user_item = User.query.filter(User.id == id).first()

	db.session.delete(user_item)
	db.session.commit()

	return 'data deletion successful <a href="/user/">back to Entries</a>'


########### facility data model controllers area ###########

@app.route('/data/facility/')
def data_facility():
	# this is the controller for JSON data access
	facility_list = Facility.query.all()

	if facility_list:
		json_result = json.dumps([facility.dto() for facility in facility_list])
	else:
		json_result = json.dumps(dict(facility=None))

	return json_result

@app.route('/facility/')
def facility_view_controller():
	#this is the controller to view all data in the model
	facility_list = Facility.query.all()

	if facility_list:
		facility_entries = [facility.dto() for facility in facility_list]
	else:
		facility_entries = None

	return render_template('facility.html',facility_entries = facility_entries)

@app.route('/facility/add/')
def facility_add_controller():
	#this is the controller to add new model entries
	return render_template('facility_add.html')

@app.route('/facility/create/',methods=['POST','GET'])
def facility_create_data_controller():
	# this is the facility data create handler
	toilet_id = request.values.get('toilet_id')
	shower = request.values.get('shower')
	soap = request.values.get('soap')
	hand_drier = request.values.get('hand_drier')
	toilet_paper = request.values.get('toilet_paper')
	wash_basin = request.values.get('wash_basin')

	new_facility = Facility(
									toilet_id = toilet_id,
									shower = shower,
									soap = soap,
									hand_drier = hand_drier,
									toilet_paper = toilet_paper,
									wash_basin = wash_basin
								)

	db.session.add(new_facility)
	db.session.commit()

	return 'data input successful <a href="/facility/">back to Entries</a>'

@app.route('/facility/edit/<id>')
def facility_edit_controller(id):
	#this is the controller to edit model entries
	facility_item = Facility.query.filter(Facility.id == id).first()
	return render_template('facility_edit.html', facility_item = facility_item)

@app.route('/facility/update/<id>',methods=['POST','GET'])
def facility_update_data_controller(id):
	# this is the facility data update handler
	toilet_id = request.values.get('toilet_id')
	shower = request.values.get('shower')
	soap = request.values.get('soap')
	toilet_paper = request.values.get('toilet_paper')
	hand_drier = request.values.get('hand_drier')
	towel = request.values.get('towel')
	wash_basin = request.values.get('wash_basin')
	facility_item = Facility.query.filter(Facility.facility_id == id).first()
	facility_item.toilet_id = toilet_id
	facility_item.shower = shower
	facility_item.soap = soap
	facility_item.toilet_paper = toilet_paper
	facility_item.hand_drier = hand_drier
	facility_item.wash_basin = wash_basin

	db.session.add(facility_item)
	db.session.commit()

	return 'data update successful <a href="/facility/">back to Entries</a>'

@app.route('/facility/delete/<id>')
def facility_delete_controller(id):
	#this is the controller to delete model entries
	facility_item = Facility.query.filter(Facility.facility_id == id).first()

	db.session.delete(facility_item)
	db.session.commit()

	return 'data deletion successful <a href="/facility/">back to Entries</a>'

