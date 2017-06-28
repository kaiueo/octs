# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt

from flask_login import UserMixin

from octs.database import Column, Model, SurrogatePK, db, reference_col, relationship
from octs.extensions import bcrypt

class Permission:
    ADMIN = 0
    TEACHER = 1
    STUDENT = 2

class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    user = relationship('User', backref='role')
    permission = Column(db.Integer)

    def __init__(self, name, permission, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)
        self.permission = permission

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Role({name})>'.format(name=self.name)
    @staticmethod
    def insert_roles():
        roles = {
            'admin': Permission.ADMIN,
            'teacher': Permission.TEACHER,
            'student': Permission.STUDENT
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r, permission=roles[r])
            db.session.add(role)
        db.session.commit()

course_user_relation = db.Table('course_user_relation',
                                db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                                db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
                                )

class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""

    __tablename__ = 'users'
    user_id = Column(db.String(100), default='11111111', nullable=False)
    username = Column(db.String(80), unique=True, nullable=False)
    gender = Column(db.Boolean(), default=False, nullable=False)
    #: The hashed password
    password = Column(db.Binary(128), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(30), nullable=True)
    roleString = Column(db.String(30), nullable=True)
    role_id = reference_col('roles', nullable=False)
    in_team = Column(db.Boolean, nullable=False, default=False)

    def __init__(self, username, permission, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, username=username, **kwargs)
        self.role = Role.query.filter_by(permission=permission).first()
        self.roleString = self.role.name
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    @staticmethod
    def insert_users():
        for i in range(5):
            user = User.query.filter_by(username="student{0}".format(i)).first()
            if user is None:
                user = User("student{0}".format(i), Permission.STUDENT, '111')
                user.name = '学生{0}'.format(i)
                user.gender = False
                if i == 3:
                    user.gender = True
                user.user_id = '{0}{0}{0}{0}{0}{0}{0}{0}'.format(i)
            db.session.add(user)

        for i in range(5):
            user = User.query.filter_by(username="teacher{0}".format(i)).first()
            if user is None:
                user = User("teacher{0}".format(i), Permission.TEACHER, '111')
                user.name = '教师{0}'.format(i)
                user.gender = False
                if i == 3:
                    user.gender = True
                user.user_id = '{0}{0}{0}{0}{0}{0}{0}{0}'.format(i)
            db.session.add(user)

        user = User("admin", Permission.ADMIN, '111')
        user.name = "admin"
        user.user_id = '00000000'
        user.gender = False
        db.session.add(user)
        db.session.commit()




    @property
    def full_name(self):
        """Full user name."""
        return '{0}'.format(self.name)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({username!r})>'.format(username=self.username)


class Term(SurrogatePK, Model):
    __tablename__ = 'terms'
    name = Column(db.String(256), unique=True)
    start_time = Column(db.Date, nullable=False, default=dt.date.today)
    end_time = Column(db.Date, nullable=False, default=dt.date.today)
    week_number = Column(db.Integer, nullable=False, default=1)
    courses = relationship('Course',  backref='term', lazy='dynamic')
    def __init__(self, name, week_number, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)
        self.week_number = week_number



class Course(SurrogatePK, Model):

    __tablename__ = 'courses'
    name = Column(db.String(256))
    credit = Column(db.Integer, nullable=False, default=1)
    start_time = Column(db.Date, nullable=False, default=dt.date.today)
    location = Column(db.String(256))
    course_introduction = Column(db.String())
    course_outline = Column(db.String())
    term_id = reference_col('terms')
    users = relationship('User', secondary=course_user_relation, backref='courses', lazy='dynamic')

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    @staticmethod
    def insert_courses():
        term = Term('2017 夏', 2)
        course = Course('软件开发实践')
        course.term = term
        for i in range(5):
            user = User.query.filter_by(username='student{0}'.format(i)).first()
            course.users.append(user)
        user = User.query.filter_by(username='teacher1').first()
        user.courses.append(course)

        user = User.query.filter_by(username='teacher2').first()
        user.courses.append(course)

        db.session.add(term)
        db.session.add(course)
        db.session.commit()



class TeamUserRelation(Model):
    __tablename__ = 'team_user_relation'
    user_id = Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    team_id = Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)
    is_master = Column(db.Boolean, default=False)
    is_accepted = Column(db.Boolean, default=False)
    user = relationship('User', backref='teams')
    team = relationship('Team', backref='users')


class Team(SurrogatePK, Model):
    __tablename__ = 'teams'
    name = Column(db.String(1000))
    status = Column(db.Integer)

class Task(SurrogatePK, Model):
    __tablename__ = 'tasks'
    name = Column(db.String(1000))
    start_time = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    end_time = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    teacher = Column(db.String(1000), nullable=False, default='x老师')

class Message(SurrogatePK, Model):
    from_id = Column(db.Integer, nullable=False)
    to_id = Column(db.Integer, nullable=False)
    title = Column(db.String(), default='通知')
    message = Column(db.String())
    has_read = Column(db.Boolean, nullable=False, default=False)
    create_time = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, from_id, to_id, **kwargs):
        db.Model.__init__(self, **kwargs)
        self.from_id = from_id
        self.to_id = to_id
        self.has_read = False

    @staticmethod
    def sendMessage(from_id, to_id, message, title='通知'):
        m = Message(from_id, to_id)
        m.title = title
        m.message = message
        db.session.add(m)
        db.session.commit()





