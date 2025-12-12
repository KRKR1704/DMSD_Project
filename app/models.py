from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class LabMember(db.Model):
    __tablename__ = 'LabMember'
    member_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    member_type = db.Column(db.String, nullable=False)
    join_date = db.Column(db.Date, nullable=False)

class Faculty(db.Model):
    __tablename__ = 'Faculty'
    member_id = db.Column(db.String, db.ForeignKey('LabMember.member_id'), primary_key=True)
    department = db.Column(db.String)
    affiliation = db.Column(db.String)
    title = db.Column(db.String)
    # biography column removed to match DB schema

class Student(db.Model):
    __tablename__ = 'Student'
    member_id = db.Column(db.String, db.ForeignKey('LabMember.member_id'), primary_key=True)
    student_number = db.Column(db.String, unique=True)
    academic_level = db.Column(db.String)
    major = db.Column(db.String)
    affiliation = db.Column(db.String)

class Collaborator(db.Model):
    __tablename__ = 'Collaborator'
    member_id = db.Column(db.String, db.ForeignKey('LabMember.member_id'), primary_key=True)
    organization = db.Column(db.String)
    contact_info = db.Column(db.String)
    biography = db.Column(db.Text)

class Project(db.Model):
    __tablename__ = 'Project'
    project_id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    expected_duration = db.Column(db.Integer)
    status = db.Column(db.String, nullable=False)
    leader_id = db.Column(db.String, db.ForeignKey('Faculty.member_id'), nullable=False)

class GrantFund(db.Model):
    __tablename__ = 'GrantFund'
    grant_id = db.Column(db.String, primary_key=True)
    source = db.Column(db.String)
    budget = db.Column(db.Float)
    start_date = db.Column(db.Date)
    duration = db.Column(db.Integer)

class ProjectGrant(db.Model):
    __tablename__ = 'ProjectGrant'
    project_id = db.Column(db.String, db.ForeignKey('Project.project_id'), primary_key=True)
    grant_id = db.Column(db.String, db.ForeignKey('GrantFund.grant_id'), primary_key=True)
    amount_allocated = db.Column(db.Float)

class WorksOn(db.Model):
    __tablename__ = 'WorksOn'
    member_id = db.Column(db.String, db.ForeignKey('LabMember.member_id'), primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('Project.project_id'), primary_key=True)
    role = db.Column(db.String)
    weekly_hours = db.Column(db.Float)

class Equipment(db.Model):
    __tablename__ = 'Equipment'
    equip_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String)
    purchase_date = db.Column(db.Date)
    status = db.Column(db.String)
    location = db.Column(db.String)
    notes = db.Column(db.Text)

class EquipmentUse(db.Model):
    __tablename__ = 'EquipmentUse'
    use_id = db.Column(db.String, primary_key=True)
    equip_id = db.Column(db.String, db.ForeignKey('Equipment.equip_id'))
    member_id = db.Column(db.String, db.ForeignKey('LabMember.member_id'))
    use_start = db.Column(db.DateTime)
    use_end = db.Column(db.DateTime)
    purpose = db.Column(db.String)

class Publication(db.Model):
    __tablename__ = 'Publication'
    pub_id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    pub_date = db.Column(db.Date)
    venue = db.Column(db.String)
    doi = db.Column(db.String)
    status = db.Column(db.String)

class Authorship(db.Model):
    __tablename__ = 'Authorship'
    pub_id = db.Column(db.String, db.ForeignKey('Publication.pub_id'), primary_key=True)
    member_id = db.Column(db.String, db.ForeignKey('LabMember.member_id'), primary_key=True)
    author_order = db.Column(db.Integer)
    author_role = db.Column(db.String)

class Mentorship(db.Model):
    __tablename__ = 'Mentorship'
    mentor_id = db.Column(db.String, db.ForeignKey('LabMember.member_id'), primary_key=True)
    mentee_id = db.Column(db.String, db.ForeignKey('LabMember.member_id'), primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # relationships for convenience
    mentor = db.relationship('LabMember', foreign_keys=[mentor_id], backref='mentees')
    mentee = db.relationship('LabMember', foreign_keys=[mentee_id], backref='mentors')
