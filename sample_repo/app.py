# sample_repo/app.py
from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User

app = Flask(__name__)

# In-memory SQLite for simplicity, replace with a real DB URL in production
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_db_session():
    return Session()

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    session = get_db_session()
    new_user = User(name=data['name'], email=data['email'])
    session.add(new_user)
    session.commit()
    return jsonify({"id": new_user.id, "name": new_user.name}), 201

# Buggy function: Lacks error handling and proper session management
def process_order(user_id, order_details):
    session = get_db_session()
    user = session.query(User).filter_by(id=user_id).one()
    
    # This will fail if order_details is None or not a dict
    if order_details['amount'] > 0:
        print(f"Processing order for {user.name}")
        # Missing transaction logic
    session.close()