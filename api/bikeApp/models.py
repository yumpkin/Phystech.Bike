import datetime
from flask_login import UserMixin
from .app import db, login_manager

""" DB Models """


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(200))
    tokens = db.Column(db.Text)
    balance = db.Column(db.Integer, default=0)
    phone_number = db.Column(db.BIGINT, default=0, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    @staticmethod
    def has_balance(balance):
        user = User.query.filter_by(balance=balance).first()
        return False if user is None else True


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class BikeOrder(db.Model):
    __tablename__ = "bike_orderings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bike_id = db.Column(db.Integer, db.ForeignKey('bike_item.id'), nullable=False)
    isFree = db.Column(db.Boolean, default=False, nullable=False)
    delay_amount = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    from_dateTime = db.Column(db.DateTime, nullable=False)
    till_dateTime = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, bike_id, isFree, delay_amount, created_at, from_dateTime, till_dateTime):
        self.user_id = user_id
        self.bike_id = bike_id
        self.isFree = isFree
        self.created_at = created_at
        self.delay_amount = delay_amount
        self.from_dateTime = from_dateTime
        self.till_dateTime = till_dateTime

    def dict(self):
        result = dict()
        result['id'] = self.id
        result['user_id'] = self.user_id
        result['bike_id'] = self.bike_id
        result['isFree'] = self.isFree
        result['delay_amount'] = self.delay_amount
        result['created_at'] = self.created_at
        result['from_dateTime'] = self.from_dateTime
        result['till_dateTime'] = self.till_dateTime
        return result

    @property
    def freeBike(self):
        return self.isFree

    @freeBike.setter
    def freeBike(self, makeFree):
        self.isFree = makeFree

    @staticmethod
    def makeBikeAvailable(bike_id):
        bike = BikeOrder.query.filter_by(bike_id=bike_id).first()
        if bike is not None:
            bike.freeBike(True)

    @staticmethod
    def checkDelay():
        delay = BikeOrder.query.filter(
            BikeOrder.till_dateTime > datetime.datetime.utcnow and BikeOrder.isFree is False).all()
        return False if delay is None else True


class Bikes(db.Model):
    __tablename__ = "bike_item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    description = db.Column(db.String(255))
    added_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_rent = db.Column(db.DateTime, nullable=False)
    bike_img = db.Column(db.String(200))

    def __init__(self, name, description, added_at, last_rent, bike_img):
        self.name = name
        self.description = description
        self.added_at = added_at
        self.last_rent = last_rent
        self.bike_img = bike_img

    def dict(self):
        result = dict()
        result['id'] = self.id
        result['name'] = self.name
        result['description'] = self.description
        result['added_at'] = self.added_at
        result['last_rent'] = self.last_rent
        result['bike_img'] = self.bike_img
        return result
