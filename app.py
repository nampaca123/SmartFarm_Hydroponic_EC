from flask import Flask, jsonify, request, render_template
from flask import redirect
from flask import url_for
from flask import session
import os
app = Flask(__name__)
app.secret_key = os.urandom(24)


# Define endpoints
@app.route('/')
def home():
    return render_template('index.html')#, datas=result)

@app.route('/login')
def login():
    return render_template('page-login.html')

@app.route('/profile')
def profile():
    return render_template('page-profile.html')
'''
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((user for user in users if user['id'] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

@app.route('/user', methods=['POST'])
def add_user():
    new_user = request.get_json()
    users.append(new_user)
    return jsonify(new_user), 201

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    update_data = request.get_json()
    user = next((user for user in users if user['id'] == user_id), None)
    if user:
        user.update(update_data)
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    users = [user for user in users if user['id'] != user_id]
    return jsonify({'message': 'User deleted'})
    '''

# Entry point to run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
