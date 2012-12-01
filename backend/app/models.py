from app import db

class Toilet(db.Model):
	toilet_id = db.Column(db.BigInteger, primary_key=True)
	toilet_name = db.Column(db.String(50))
	toilet_lat = db.Column(db.String(50))
	toilet_long = db.Column(db.String(50))
	toilet_address = db.Column(db.String(100))
	toilet_current_rating = db.Column(db.Float)
	toilet_type = db.Column(db.Integer)
	added_on = db.Column(db.DateTime)
	user_id = db.Column(db.BigInteger)
	facility = db.relationship('Facility', backref='toilet', lazy='dynamic')
	image = db.relationship('Image', backref='toilet', lazy='dynamic')

	# data transfer object to form JSON
	def dto(self):
		return dict(
				toilet_id = self.toilet_id,
				toilet_name = self.toilet_name,
				toilet_lat = self.toilet_lat,
				toilet_long = self.toilet_long,
				toilet_address = self.toilet_address,
				toilet_current_rating = self.toilet_current_rating,
				toilet_type = self.toilet_type,
				added_on = self.added_on.isoformat(),
				user_id = self.user_id)

class User(db.Model):
	user_id = db.Column(db.BigInteger, primary_key=True)
	first_name = db.Column(db.String(50))
	last_name = db.Column(db.String(50))
	email = db.Column(db.String(50))
	password = db.Column(db.String(50))
	registered_on = db.Column(db.DateTime)

	# data transfer object to form JSON
	def dto(self):
		return dict(
				user_id = self.user_id,
				first_name = self.first_name,
				last_name = self.last_name,
				email = self.email,
				password = self.password,
				registered_on = self.registered_on.isoformat())

class Facility(db.Model):
	facility_id = db.Column(db.BigInteger, primary_key=True)
	toilet_id = db.Column(db.BigInteger, db.ForeignKey('toilet.toilet_id'))
	shower = db.Column(db.Integer)
	soap = db.Column(db.Integer)
	toilet_paper = db.Column(db.Integer)
	hand_drier = db.Column(db.Integer)
	wash_basin = db.Column(db.Integer)

	# data transfer object to form JSON
	def dto(self):
		return dict(
				facility_id = self.facility_id,
				toilet_id = self.toilet_id,
				shower = self.shower,
				soap = self.soap,
				toilet_paper = self.toilet_paper,
				hand_drier = self.hand_drier,
				wash_basin = self.wash_basin)

class Rating(db.Model):
	rating_id = db.Column(db.BigInteger, primary_key=True)
	toilet_id = db.Column(db.BigInteger)
	user_id = db.Column(db.BigInteger)
	overall_rating = db.Column(db.Float)
	rated_on = db.Column(db.DateTime)

	# data transfer object to form JSON
	def dto(self):
		return dict(
				rating_id = self.rating_id,
				toilet_id = self.toilet_id,
				user_id = self.user_id,
				overall_rating = self.overall_rating,
				rated_on = self.rated_on)

class Image(db.Model):
	image_id = db.Column(db.BigInteger, primary_key=True)
	toilet_id = db.Column(db.BigInteger, db.ForeignKey('toilet.toilet_id'))
	user_id = db.Column(db.BigInteger)
	added_on = db.Column(db.DateTime)

	# data transfer object to form JSON
	def dto(self):
		return dict(
				image_id = self.image_id,
				toilet_id = self.toilet_id,
				user_id = self.user_id,
				added_on = self.added_on)
