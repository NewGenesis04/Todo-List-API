from flask import jsonify, request, flash, session, url_for, redirect
from flask_login import login_user, logout_user, current_user, login_required
from models import User, Task
import json


def register_routes(app, db):
    @app.route('/login', methods=['POST'])
    def login():
        body = request.get_json()
        email = body.get('email')
        password = body.get('password')
        try:
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                return jsonify({'authenticated': True}),  200
            return jsonify({'authenticated': False}), 401

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/logout', methods=['POST'])
    def logout():
        try:
            user = current_user.to_dict()
            logout_user()
            return jsonify({'message': 'Logged out successfully', 'user': user}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/signup', methods=['POST'])
    def signup():
        body = request.get_json()
        name = body.get('name')
        email = body.get('email')
        password = body.get('password')

        try:
            if not name or not email or not password:
                return jsonify({'error': 'All Credentials are required'}), 400

            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'Email already exists!'}), 409

            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return jsonify({'success': True, 'user': user.to_dict()}), 201

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/profile', methods=['GET'])
    @login_required
    def get_profile():
        try:
            return jsonify({'user': current_user.to_dict()}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/profile/', methods=['PUT'])
    @login_required
    def update_profile():
        try:
            body = request.get_json()
            name = body.get('name')
            email = body.get('email')
            password = body.get('password')

            if name:
                current_user.name = name
            if email:
                current_user.email = email
            if password:
                current_user.set_password(password)

            db.session.commit()
            return jsonify({'message': 'Profile updated successfully', "user": current_user.to_dict()}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route('/tasks', methods=['POST'])
    @login_required
    def create_task():
        try:
            body = request.get_json()
            title = body.get('title')
            description = body.get('description')

            if not title or not description:
                return jsonify({"error": "Title and description are required"}), 400

            task = Task(title=title, description=description,
                        user_id=current_user.uid)

            db.session.add(task)
            db.session.commit()

            return jsonify({'message': 'Task created succesfully', 'task': task.to_dict()}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route('/tasks', methods=['GET'])
    @login_required
    def get_tasks():
        try:
            tasks = current_user.tasks
            return jsonify({'tasks': [task.to_dict() for task in tasks]}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/tasks/<int:id>', methods=['GET'])
    @login_required
    def get_task_by_id(id: int):
        try:
            task = Task.query.filter_by(
                id=id, user_id=current_user.uid).first()
            if not task:
                return jsonify({"error": "Task not found or not authorized"}), 404

            return jsonify({'task': task.to_dict()}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/tasks/<int:id>', methods=['PUT'])
    @login_required
    def update_task_by_id(id: int):
        try:
            task = Task.query.filter_by(
                id=id, user_id=current_user.uid).first()
            if not task:
                return jsonify({"error": "Task not found or not authorized"}), 404

            body = request.get_json()
            title = body.get('title')
            description = body.get('description')

            if title:
                task.title = title
            if description:
                task.description = description

            db.session.commit()
            return jsonify({"message": "Task updated", "task": task.to_dict()}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route('/tasks/<int:id>', methods=['DELETE'])
    @login_required
    def delete_task_by_id(id: int):
        try:
            task = Task.query.filter_by(
                id=id, user_id=current_user.uid).first()
            if not task:
                return jsonify({"error": "Task not found or not authorized"}), 404

            db.session.delete(task)
            db.session.commit()
            return jsonify({"message": "Task deleted", "task": task.to_dict()}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route('/tasks/<int:id>/complete', methods=['PUT'])
    @login_required
    def complete(id: int):
        try:
            task = Task.query.filter_by(
                id=id, user_id=current_user.uid).first()

            if not task:
                return jsonify({"error": "Task not found or not authorized"}), 404

            task.status = "complete"
            db.session.commit()
            return jsonify({"message": "Task marked as complete", "task": task.to_dict()}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route('/tasks/completed', methods=['GET'])
    @login_required
    def get_completed():
        try:
            tasks = Task.query.filter(
                Task.status == 'complete', Task.user_id == current_user.uid).all()
            return jsonify({'tasks': [task.to_dict() for task in tasks]}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
