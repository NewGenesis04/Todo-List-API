from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    tasks = db.relationship('Task', backref='user', lazy=True,
                            cascade='all, delete-orphan', order_by='Task.id')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return str(self.uid)

    def to_dict(self):
        return {
            'uid': self.uid,
            'name': self.name,
            'email': self.email
        }


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='pending')
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'user_id': self.user_id
        }
