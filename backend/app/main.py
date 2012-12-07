# do not change or move the following lines if you still want to use the box.py auto generator
from app import app, db
from models import Toilet, User, Facility, Rating, Image

# you can freely change the lines below
from flask import render_template
from flask import json
from flask import session
from flask import url_for
from flask import redirect
from flask import request
from flask import abort
from flask import Response
from config import SQLALCHEMY_DATABASE_URI
from subprocess import call
import sqlalchemy
import logging
import datetime
import hashlib
import math
import os
# define global variables here

basedir = os.path.abspath(os.path.dirname(__file__))
base_url = 'http://192.168.2.1:5000/'
upload_folder = os.path.join(basedir, 'static/img/tmp/')

# define functions here
def distance(point1, point2):
	lat1, lon1, lat2, lon2 = map(math.radians, [float(point1[0]), float(point1[1]), float(point2[0]), float(point2[1])])
	dlat = lat2 - lat1
	dlon = lon2 - lon1
	a = (math.sin(dlat/2)**2) + (math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
	c = 2 * math.asin(math.sqrt(a))
	km = 6371 * c
	return km

def multikeysort(items, columns):
    from operator import itemgetter
    comparers = [ ((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in columns]  
    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0
    return sorted(items, cmp=comparer)

def update_overall_rating(toilet_id,avg):
	the_toilet = Toilet.query.filter(Toilet.toilet_id==toilet_id).one()
	the_toilet.toilet_current_rating = avg
	db.session.add(the_toilet)
	db.session.commit()
# home root controller
@app.route('/')
def index():
	# define your controller here
	return render_template('index.html')

########### toilet data model controllers area ###########
@app.route('/search/<latlong_string>')
def search_toilet(latlong_string):
	toilets = []
	latlong = latlong_string.split(',')
	toilet_list = Toilet.query.all()
	logging.error(repr(latlong)+' '+str(len(toilet_list)))
	for i,toilet in enumerate(toilet_list):
		toilet_detail = {}
		db_pair = []
		db_pair.append(toilet.toilet_lat)
		db_pair.append(toilet.toilet_long)
		delta = distance(latlong,db_pair)
		logging.error(str(i)+' '+repr(db_pair))
		if delta <= 1:
			toilet_detail['toilet_id'] = toilet.toilet_id
			toilet_detail['toilet_name'] = toilet.toilet_name
			toilet_detail['toilet_lat'] = toilet.toilet_lat
			toilet_detail['toilet_long'] = toilet.toilet_long
			toilet_detail['toilet_address'] = toilet.toilet_address
			toilet_detail['toilet_current_rating'] = toilet.toilet_current_rating
			toilet_detail['toilet_type'] = toilet.toilet_type
			toilet_detail['added_on'] = toilet.added_on.isoformat()
			toilet_detail['user_id'] = toilet.user_id
			toilet_detail['distance'] = int(math.floor(delta*100))
			toilets.append(toilet_detail)
	toilets = multikeysort(toilets, ['distance', '-toilet_current_rating'])
	result = json.dumps(dict(toilets=toilets))
	return result

@app.route('/tmpsearch/<latlong_string>')
def temp_search_toilet(latlong_string):
	toilets = []
	latlong = latlong_string.split(',')
	lat_top_limit = float(latlong[0]) + 0.014564
	lat_low_limit = float(latlong[0]) - 0.167469
	long_top_limit = float(latlong[1]) + 0.014483
	long_low_limit = float(latlong[1]) - 0.014483
	logging.error('#######')
	toilet_list = Toilet.query.filter(Toilet.toilet_lat <= lat_top_limit, Toilet.toilet_lat >= lat_low_limit, Toilet.toilet_long <= long_top_limit, Toilet.toilet_long >= long_low_limit ).all()
	for i, toilet in enumerate(toilet_list):
		toilet_detail = {}
		db_pair = [toilet.toilet_lat,toilet.toilet_long]
		logging.error(db_pair)
		logging.error(latlong)
		delta = distance(latlong,db_pair)
		logging.error(delta)
		toilet_detail['toilet_id'] = toilet.toilet_id
		toilet_detail['toilet_name'] = toilet.toilet_name
		toilet_detail['toilet_lat'] = toilet.toilet_lat
		toilet_detail['toilet_long'] = toilet.toilet_long
		toilet_detail['toilet_address'] = toilet.toilet_address
		toilet_detail['toilet_current_rating'] = toilet.toilet_current_rating
		toilet_detail['toilet_type'] = toilet.toilet_type
		toilet_detail['added_on'] = toilet.added_on.isoformat()
		toilet_detail['user_id'] = toilet.user_id
		toilet_detail['distance'] = int(math.floor(delta*100))
		toilets.append(toilet_detail)
	toilets = multikeysort(toilets, ['distance', '-toilet_current_rating'])
	result = json.dumps(dict(toilets=toilets))
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

def get_single_toilet(inputid):
	base_url = request.url_root
	single_toilet = Toilet.query.filter(Toilet.toilet_id == inputid).first()
	if single_toilet:
		toilet = single_toilet.dto()
		facility_list = single_toilet.facility.first()
		if facility_list:
			facility = facility_list.dto()
		else:
			facility = None
		image_list = single_toilet.image.first()
		if image_list:
			full_image = base_url + 'static/img/large/' + str(image_list.image_id) + '.jpg'
			thumb_image = base_url + 'static/img/thumb/' + str(image_list.image_id) + '.jpg'
		else:
			full_image = base_url + 'static/img/large/1.jpg'
			thumb_image = base_url + 'static/img/thumb/1.jpg'
			# image = None
		total_rate = Rating.query.filter(Rating.toilet_id == inputid).all()
		totnum  = len(total_rate)
	else:
		toilet = None
		facility = None
	result = dict(toilet=toilet,facility=facility,total_vote=totnum,full_image=full_image,thumb_image=thumb_image)
	return result
    
@app.route('/toilet/<inputid>.json')
def get_single_toilet_json(inputid):
	result = json.dumps(get_single_toilet(inputid))
	return result
    
@app.route('/toilet/<inputid>')
def view_single_toilet(inputid):
    toilet_data = get_single_toilet(inputid)
    return render_template('toilet_view.html',toilet_item = toilet_data)

@app.route('/toilet/add/')
def toilet_add_controller():
	#this is the controller to add new model entries
	return render_template('toilet_add.html')

@app.route('/toilet/create/<toilet_name>/<toilet_lat>/<toilet_long>/<toilet_address>/<toilet_current_rating>/<toilet_type>/<user_id>',methods=['POST','GET'])
def toilet_create_data_controller(toilet_name,toilet_lat,toilet_long,toilet_address,toilet_current_rating,toilet_type,user_id):
	toilet_name = toilet_name.replace('+',' ')
	toilet_address = toilet_address.replace('+',' ')
	new_toilet = Toilet(
									toilet_name = toilet_name,
									toilet_lat = toilet_lat,
									toilet_long = toilet_long,
									toilet_address = toilet_address,
									toilet_current_rating = toilet_current_rating,
									toilet_type = toilet_type,
									added_on = datetime.datetime.now(),
									user_id = user_id
								)

	db.session.add(new_toilet)
	db.session.commit()

	return str(new_toilet.toilet_id)

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
	toilet_type = request.values.get('toilet_type')
	added_on = request.values.get('added_on')
	user_id = request.values.get('user_id')
	toilet_item = Toilet.query.filter(Toilet.toilet_id == id).first()
	toilet_item.toilet_name = toilet_name
	toilet_item.toilet_lat = toilet_lat
	toilet_item.toilet_long = toilet_long
	toilet_item.toilet_address = toilet_address
	toilet_item.toilet_current_rating = toilet_current_rating
	toilet_item.toilet_type = toilet_type
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

@app.route('/user/<inputid>.json')
def get_single_user(inputid):
	single_user = User.query.filter(User.user_id == inputid).first()
	result = json.dumps(single_user.dto())

	return result

@app.route('/user/<inputid>')
def get_user_detail(inputid):
	single_user = User.query.filter(User.user_id == inputid).first()
	result = single_user.dto()

	return render_template('user_view.html', user_data=result)

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



########### rating data model controllers area ###########

@app.route('/data/rating/')
def data_rating():
	# this is the controller for JSON data access
	rating_list = Rating.query.all()

	if rating_list:
		json_result = json.dumps([rating.dto() for rating in rating_list])
	else:
		json_result = json.dumps(dict(rating=None))

	return json_result

@app.route('/rating/')
def rating_view_controller():
	#this is the controller to view all data in the model
	rating_list = Rating.query.all()

	if rating_list:
		rating_entries = [rating.dto() for rating in rating_list]
	else:
		rating_entries = None

	return render_template('rating.html',rating_entries = rating_entries)



@app.route('/rating/create/<toilet_id>/<user_id>/<overall_rating>', methods=['POST','GET','PUT'])
def rating_create_data_controller(toilet_id,user_id,overall_rating):
	# this is the rating data create handler
	# toilet_id = request.values.get('toilet_id')
	# user_id = request.values.get('user_id')
	# overall_rating = request.values.get('overall_rating')
	
	new_rating = Rating(
									toilet_id = toilet_id,
									user_id = user_id,
									overall_rating = overall_rating,
									rated_on = datetime.datetime.now()
								)

	db.session.add(new_rating)
	db.session.commit()

	avg = db.session.query(sqlalchemy.func.avg(Rating.overall_rating).label('average')).filter(Rating.toilet_id == toilet_id).first()
	update_overall_rating(toilet_id,avg[0])
	result = str(avg[0])
	return result

@app.route('/rating/latest/<toilet_id>/<number_of_ratings>',methods=['POST','GET'])
def get_latest_amount_of_toilet_ratings(toilet_id,number_of_ratings):
	rating_list = Rating.query.filter(Rating.toilet_id == toilet_id).order_by(sqlalchemy.desc(Rating.rated_on)).limit(number_of_ratings)
	json_result = json.dumps([rating.dto() for rating in rating_list])
	return json_result

########### image data model controllers area ###########

@app.route('/data/image/')
def data_image():
	# this is the controller for JSON data access
	image_list = Image.query.all()

	if image_list:
		json_result = json.dumps([image.dto() for image in image_list])
	else:
		json_result = None

	return json_result

@app.route('/image/')
def image_view_controller():
	#this is the controller to view all data in the model
	image_list = Image.query.all()

	if image_list:
		image_entries = [image.dto() for image in image_list]
	else:
		image_entries = None

	return render_template('image.html',image_entries = image_entries)

@app.route('/image/add/')
def image_add_controller():
	#this is the controller to add new model entries
	return render_template('image_add.html')

@app.route('/image/create/',methods=['POST','GET'])
def image_create_data_controller():
	# this is the image data create handler
	toilet_id = request.values.get('toilet_id')
	user_id = request.values.get('user_id')
	file = request.files.get('file').read()
	if file:
		open(upload_folder+toilet_id+'.jpg','wb').write(file)

		new_image = Image(
						toilet_id = toilet_id,
						user_id = user_id,
						added_on = datetime.datetime.now()
					)
		db.session.add(new_image)
		db.session.commit()
		call(['python', 'thumb_create.py',toilet_id])
		return 'data input successful <a href="/image/">back to Entries</a>'
	else:
		return 'upload failed'

@app.route('/image/edit/<id>')
def image_edit_controller(id):
	#this is the controller to edit model entries
	image_item = Image.query.filter(Image.id == id).first()
	return render_template('image_edit.html', image_item = image_item)

@app.route('/image/update/<id>',methods=['POST','GET'])
def image_update_data_controller(id):
	# this is the image data update handler
	toilet_id = request.values.get('toilet_id')
	user_id = request.values.get('user_id')
	added_on = request.values.get('added_on')
	image_item = Image.query.filter(Image.image_id == id).first()
	image_item.toilet_id = toilet_id
	image_item.user_id = user_id
	image_item.added_on = added_on

	db.session.add(image_item)
	db.session.commit()

	return 'data update successful <a href="/image/">back to Entries</a>'

@app.route('/image/delete/<id>')
def image_delete_controller(id):
	#this is the controller to delete model entries
	image_item = Image.query.filter(Image.image_id == id).first()

	db.session.delete(image_item)
	db.session.commit()

	return 'data deletion successful <a href="/image/">back to Entries</a>'


@app.route('/rating/add/')
def rating_add_controller():
	#this is the controller to add new model entries
	return render_template('rating_add.html')

@app.route('/dashboard/')
def dashboard_controller():
	average_toilet_rating = db.session.query(sqlalchemy.func.avg(Rating.overall_rating).label('average')).first()
	logging.error(average_toilet_rating)
	total_toilet_amount = db.session.query(sqlalchemy.func.count(Toilet.toilet_id).label('total_toilet')).first()
	max_toilet_rating = db.session.query(sqlalchemy.func.max(Rating.overall_rating).label('max')).first()
	min_toilet_rating = db.session.query(sqlalchemy.func.min(Rating.overall_rating).label('max')).first()
	total_users = db.session.query(sqlalchemy.func.count(User.user_id).label('total_user')).first()
	total_rating = db.session.query(sqlalchemy.func.count(Rating.rating_id).label('total_rating')).first()
	toilet_list = Toilet.query.all()
	#this is the controller to display aggregated data
	statistics = dict(toilet_avg=average_toilet_rating[0],toilet_total=total_toilet_amount[0],max_rating=max_toilet_rating[0],min_rating = min_toilet_rating[0],total_user=total_users[0],total_rating = total_rating[0])
	toilets=[toilet.dto() for toilet in toilet_list]
	return render_template('dashboard.html',statistics=statistics,toilets=toilets)

@app.route('/migrate/temp')
def migrate_temp():
	all_toilet = Toilet.query.all()
	for toilet in all_toilet:
		toilet.old_toilet_lat = toilet.toilet_old_lat
		toilet.old_toilet_long = toilet.toilet_old_long
		db.session.add(toilet)
	db.session.commit()
	return 'process_done'

@app.route('/migrate/temp2')
def migrate_temp():
	all_toilet = Toilet.query.all()
	for toilet in all_toilet:
		toilet.toilet_lat = float(toilet.old_toilet_lat)
		toilet.toilet_long = float(toilet.old_toilet_long)
		db.session.add(toilet)
	db.session.commit()
	return 'finalization_done'
