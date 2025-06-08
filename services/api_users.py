from app import db
from models import User
from werkzeug.security import generate_password_hash
from flask import session

# Registering new user.
def register_user(name, email, password):
    try:
        if not name or not email or not password:
            return False, 'Missing required fields'

        if not email.lower().endswith('@sfsu.edu'):
            return False, 'Email must be an @sfsu.edu address'

        if User.query.filter_by(email=email).first():
            return False, 'Email already registered'

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return True, 'User registered successfully'
    except Exception as e:
        return False, f'Registration failed: {str(e)}'

def login_user(email, password):
    try:
        if not email or not password:
            return False, 'Missing required fields'


        user = User.query.filter_by(email=email).first()

        if not user:
            return False, 'invalid email'

        #print("Password hash:", user.password_hash)
        #print("Check result:", user.check_password(password))

        if not user.check_password(password):
            return False, 'Invalid password'

        session['user_id'] = user.id

        return True, 'Logging in user'
    except Exception as e:
        return False, f'login failed: {str(e)}'