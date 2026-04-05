from flask import request, jsonify, send_file, session, redirect
from services import create_user, get_all_users, get_user_by_id, delete_user, update_user
from models import Admin, db
from flask_mail import Message
import string
import random

def register_routes(app, mail):
    @app.route('/')
    def index():
        if not session.get('admin_id'):
            return redirect('/login')
        return send_file('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            data = request.get_json(silent=True) or request.form
            username = data.get('username')
            password = data.get('password')
            
            admin = Admin.query.filter_by(username=username).first()
            if admin and admin.check_password(password):
                session['admin_id'] = admin.id
                return jsonify({'message': 'Logged in successfully'}), 200
            else:
                return jsonify({'error': 'Invalid username or password'}), 401
                
        return send_file('login.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            data = request.get_json(silent=True) or request.form
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password or not data.get('email'):
                return jsonify({'error': 'Username, email and password required'}), 400
                
            email = data.get('email')
                
            if Admin.query.filter_by(username=username).first():
                return jsonify({'error': 'Username already exists'}), 400
            if Admin.query.filter_by(email=email).first():
                return jsonify({'error': 'Email already exists'}), 400
                
            admin = Admin(username=username, email=email)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            
            try:
                msg = Message("Welcome to User Management System", recipients=[email])
                msg.body = f"Hello {username},\n\nYour admin account has been created successfully!"
                mail.send(msg)
            except Exception as e:
                print(f"Failed to send email: {e}")
            
            return jsonify({'message': 'Account created successfully'}), 201

        return send_file('signup.html')

    @app.route('/logout', methods=['GET', 'POST'])
    def logout():
        session.pop('admin_id', None)
        return jsonify({'message': 'Logged out successfully'}), 200

    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        if request.method == 'POST':
            data = request.get_json(silent=True) or request.form
            email = data.get('email')
            
            if not email:
                 return jsonify({'error': 'Email is required'}), 400
                 
            admin = Admin.query.filter_by(email=email).first()
            if admin:
                try:
                    msg = Message("Password Recovery", recipients=[email])
                    msg.body = f"Hello {admin.username},\n\nAs requested, your saved password is: {admin.password}\n\nPlease keep it safe."
                    mail.send(msg)
                    return jsonify({'message': 'Password recovery successful. Check your email.'}), 200
                except Exception as e:
                    print(f"Failed to send email: {e}")
                    # Fallback for local testing when SMTP is not configured
                    return jsonify({'message': f'Email sending failed. Your saved password is: {admin.password}'}), 200
            else:
                return jsonify({'error': 'Account not found with that email.'}), 404
                
        return send_file('forgot_password.html')

    @app.route('/users', methods=['POST'])
    def add_user():
        # Accept JSON requests (preferred) or form-encoded payloads when Content-Type is missing
        data = request.get_json(silent=True) or request.form

        if not data:
            return jsonify({'error': 'Request body must be JSON or form-encoded'}), 400

        username = data.get('username')
        email = data.get('email')

        if not username or not email:
            return jsonify({'error': 'Username and email are required'}), 400

        new_user = create_user(username, email)
        
        try:
            msg = Message("You have been added!", recipients=[email])
            msg.body = f"Hello {username},\n\nYou have been added to the system by an administrator."
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")
            
        return jsonify({
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email
        }), 201

    @app.route('/users', methods=['GET'])
    def list_users():
        users = get_all_users()
        return jsonify([u.to_dict() for u in users]), 200
    

    
    @app.route('/users/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        user = get_user_by_id(user_id)
        if user:
            return jsonify(user.to_dict()), 200
        else:
            return jsonify({'error': 'User not found'}), 404
        
        
    @app.route('/users/<int:user_id>', methods=['DELETE'])
    def delete_user_route(user_id):
        success = delete_user(user_id)
        if success:
            return jsonify({'message': 'User deleted successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
       

    @app.route('/users/<int:user_id>', methods=['PUT'])
    def update_user_route(user_id):
        data = request.get_json(silent=True) or request.form
        if not data:
            return jsonify({'error': 'Request body must be JSON or form-encoded'}), 400
            
        username = data.get('username')
        email = data.get('email')
        
        user = update_user(user_id, username=username, email=email)
        if user:
            return jsonify(user.to_dict()), 200
        else:
            return jsonify({'error': 'User not found'}), 404