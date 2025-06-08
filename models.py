from app import db
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import LONGBLOB
from werkzeug.security import generate_password_hash, check_password_hash

class Categories(db.Model):
    __tablename__ = 'Categories'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100),unique=True )

class Items(db.Model):
    __tablename__ = 'Items'
    item_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    category_id = db.Column(sa.ForeignKey(Categories.category_id))
    item_description = db.Column(db.Text)
    item_condition = db.Column(sa.Enum('Brand New', 'Used - Like New', 'Used - Good', 'Used - Acceptable', name='item_condition_enum',
        validate_strings=True,
        native_enum=False))
    price = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seller_id = db.Column(sa.ForeignKey('Users.id'))
    is_sold = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)

class ItemImages(db.Model):
    __tablename__ = 'ItemImages'
    image_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(sa.ForeignKey(Items.item_id), index=True)
    image_data = db.Column(LONGBLOB)
    mime_type = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    __tablename__ = 'Messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(sa.ForeignKey(User.id), nullable=False)
    receiver_id = db.Column(sa.ForeignKey(User.id), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    item_id = db.Column(sa.ForeignKey(Items.item_id), nullable=True)
    is_read = db.Column(db.Boolean, default=False)


class SavedItems(db.Model):
    __tablename__ = 'SavedItems'
    user_id = db.Column(sa.ForeignKey(User.id), primary_key=True)
    item_id = db.Column(sa.ForeignKey(Items.item_id), primary_key=True)