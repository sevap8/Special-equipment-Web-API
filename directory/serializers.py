from re import S
from flask_restx import Model, fields
from app.custom.utils import NestedOrNone
from app.department.serializers import department_serializer


device_serializer_create = Model('Device_create', {
    "name": fields.String,
    "device_type": fields.String,
    "fabrique_number": fields.String,
    "passport_number": fields.String,
    "manufactured_date": fields.DateTime,
    "zri_count": fields.Integer,
    'department': fields.String(attribute='department.id'),
    "is_active": fields.Boolean
})

device_serializer_list = Model('Device_list', {
    "pk": fields.String(attribute='id'),
    "name": fields.String,
    "device_type": fields.String,
    "fabrique_number": fields.String,
    "passport_number": fields.String,
    "manufactured_date": fields.DateTime,
    "zri_count": fields.Integer,
    'department': NestedOrNone(department_serializer),
    "is_active": fields.Boolean
})

device_serializer_content = Model('Device_list_content', {
    "content": fields.Nested(device_serializer_list),
    "total_pages": fields.Integer,
    "total_items": fields.Integer
})