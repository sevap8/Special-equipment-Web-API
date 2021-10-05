import uuid

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref

from app import db
from app.custom.models import ExtendedMethod

from config import RV_S


class Device(db.Model, ExtendedMethod):
    """
    Installation devices
    """

    __tablename__ = 'devices'
    __table_args__ = {'schema': RV_S}

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    name = db.Column(
        db.String(64),
        doc="name",
        nullable=False,
    )
    device_type = db.Column(
        db.String(64),
        doc="device type",
        nullable=False,
    )
    fabrique_number = db.Column(
        db.String(64),
        doc="fabrique number",
        nullable=False,
        unique=True
    )
    passport_number = db.Column(
        db.String(64),
        doc="passport number",
        nullable=False,
    )
    manufactured_date = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        doc="date created"
    )
    zri_count = db.Column(
        db.Integer,
        nullable=True,
        doc="zri count"
    )
    department_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('department.id'),
        nullable=False
    )
    department = db.relationship(
        'Department',
        backref=backref("rv_device", lazy='dynamic'),
        doc="Department"
    )