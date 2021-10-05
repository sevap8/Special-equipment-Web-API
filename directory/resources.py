
from datetime import datetime, timezone

from flask_restx import reqparse, Resource, inputs
from sqlalchemy import or_, func
from sqlalchemy_fsm.exc import InvalidSourceStateError
from werkzeug.exceptions import BadRequest

from app import db
from app.custom.security_decorators import (directory_manage_required)
from directory.resources import api
from directory.models import Device
from directory.serializers import (device_serializer_list, device_serializer_content, device_serializer_create)

from app.department.models import Department


api.models[device_serializer_content.name] = device_serializer_content
api.models[device_serializer_list.name] = device_serializer_list
api.models[device_serializer_create.name] = device_serializer_create

class DeviceListCreate(Resource):
    
    @directory_manage_required
    @api.doc(
        params={'ordering': 'name | -name',
                'show_inactive': 'true',
                'search': 'name',
                'offset': '', 'limit': ''},
        description="List Installation Apparatus")
    @api.marshal_list_with(device_serializer_content, mask='')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ordering', type=str, location='args')
        parser.add_argument('search', type=str, location='args')
        parser.add_argument('offset', type=str)
        parser.add_argument('limit', type=str)
        parser.add_argument('show_inactive', type=inputs.boolean)
        data = parser.parse_args()

        dev_query = Device.query
        if not data['show_inactive']:
            dev_query = dev_query.filter_by(is_active=True)

        if data['ordering'] is not None:
            if data['ordering'] == 'name':
                dev_query = dev_query.order_by(
                    Device.name.asc())
            elif data['ordering'] == '-name':
                dev_query = dev_query.order_by(
                    Device.name.desc())
        if data['search']:
            tmp_subquery = []
            for word in data['search'].split():
                tmp_subquery.append(func.lower(Device.name).contains(f"{word.lower()}"))
            dev_query = dev_query.filter(or_(*tmp_subquery))
        if data['offset'] and data['limit']:
            dev_query = dev_query.paginate(page=int(data['offset']), per_page=int(data['limit']))
            return {
                       "content": dev_query.items,
                       "total_pages": dev_query.pages,
                       "total_items": dev_query.total
                   }, 200
        else:
            return {
                       "content": dev_query.all()
                   }, 200

    @directory_manage_required
    @api.expect(device_serializer_create, validate=True)
    @api.doc(description="Creating Installation Apparatus")
    @api.marshal_list_with(device_serializer_list, mask='')
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, help='This field cannot be blank', required=True)
        parser.add_argument('device_type', type=str, help='This field cannot be blank', required=True)
        parser.add_argument('fabrique_number', type=str, help='This field cannot be blank', required=True)
        parser.add_argument('passport_number', type=str, help='This field cannot be blank', required=True)
        parser.add_argument('manufactured_date', type=inputs.datetime_from_iso8601, help='This field cannot be blank', required=True)
        parser.add_argument('zri_count', type=int, help='This field cannot be blank', required=True)
        parser.add_argument('department', type=str, help='This field cannot be blank', required=True)
        data = parser.parse_args()

        dev_name = data['name'].strip()
        if not 0 < len(dev_name) < 65:
            raise BadRequest('The name must be no more than 64 characters')
        dev_type = data['device_type'].strip()
        if not 0 < len(dev_type) < 65:
            raise BadRequest('The type must be no more than 64 characters')
        dev_fnumber = data['fabrique_number'].strip()
        if not 0 < len(dev_fnumber) < 65:
            raise BadRequest('The fabrique number must be no more than 64 characters')
        dev_pnumber = data['passport_number'].strip()
        if not 0 < len(dev_pnumber) < 65:
            raise BadRequest('The passport number must be no more than 64 characters')
        if data['manufactured_date'].date() > datetime.now(timezone.utc).date():
            raise BadRequest('Date cannot be in the future')
        if not 0 < data['zri_count'] < 100:
            raise BadRequest('The number of ZRI in the device must be greater than zero and less than 100')
        department = Department.query.get(data['department'])
        if not department:
            raise BadRequest("Department not found")        

        new_device = Device(
            name=dev_name,
            device_type=dev_type,
            fabrique_number=dev_fnumber,
            passport_number=dev_pnumber,
            manufactured_date=data['manufactured_date'],
            zri_count=data['zri_count'],
            department_id=department.id,
        )
        try:
            db.session.add(new_device)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            if 'unique' in e.args[0]:
                raise BadRequest('An installation device with the same serial number already exists')
            else:
                raise BadRequest('Action is impossible')
        return new_device, 201
    
       
class DeviceDetail(Resource):

    @directory_manage_required
    @api.doc('Card - Installation apparatus')
    @api.marshal_list_with(device_serializer_list, mask='')
    def get(self, dev_id):
        
        dev_query = Device.query.get(dev_id)
        if not dev_query:
            raise BadRequest('Installation device not found')
        return dev_query, 200
 
    @directory_manage_required
    @api.expect(device_serializer_create, validate=True)
    @api.doc(description="Editing the Installation Device")
    @api.marshal_list_with(device_serializer_list, mask='')
    def put(self, dev_id):     
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, help='This field cannot be blank', required=True)
        parser.add_argument('device_type', type=str, help='This field cannot be blank', required=True)
        parser.add_argument('fabrique_number', type=str, help='This field cannot be blank', required=True)
        parser.add_argument('passport_number', type=str, help='This field cannot be blank', required=True)
        parser.add_argument('manufactured_date', type=inputs.datetime_from_iso8601, help='This field cannot be blank', required=True)
        parser.add_argument('zri_count', type=int, help='This field cannot be blank', required=True)
        parser.add_argument('is_active', type=inputs.boolean, required=False)
        data = parser.parse_args()

        dev_query = Device.query.get(dev_id)
        if not dev_query:
            raise BadRequest('Installation device not found')

        if data['is_active'] is not None and data['is_active'] == False:
            dev_query.remove()
            return dev_query
        
        dev_name = data['name'].strip()
        if not 0 < len(dev_name) < 65:
            raise BadRequest('The name must be no more than 64 characters')
        dev_type = data['device_type'].strip()
        if not 0 < len(dev_type) < 65:
            raise BadRequest('The type must be no more than 64 characters')
        dev_fnumber = data['fabrique_number'].strip()
        if not 0 < len(dev_fnumber) < 65:
            raise BadRequest('The fabrique number must be no more than 64 characters')
        dev_pnumber = data['passport_number'].strip()
        if not 0 < len(dev_pnumber) < 65:
            raise BadRequest('The passport number must be no more than 64 characters')
        if data['manufactured_date'].date() > datetime.now(timezone.utc).date():
            raise BadRequest('Date cannot be in the future')
        if not 0 < data['zri_count'] < 100:
            raise BadRequest('The number of ZRI in the device must be greater than zero and less than 100')

        loaded = dev_query.record.all()
        device_zri_count = sum([rv_l.amount for rv_l in loaded]) if loaded else 0
        
        if data['zri_count'] < device_zri_count:
            raise BadRequest(f'An unacceptable value "Number of SIR in the device, pcs." Is specified. At the moment, the device contains: {device_zri_count}')

        if data['is_active']:
            dev_query.is_active = data['is_active']
        dev_query.name = dev_name
        dev_query.device_type = dev_type
        dev_query.fabrique_number = dev_fnumber
        dev_query.passport_number = dev_pnumber
        dev_query.manufactured_date = data['manufactured_date']
        dev_query.zri_count = data['zri_count']
        
        try:
            db.session.add(dev_query)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()     
            if 'unique' in e.args[0]:
                raise BadRequest('An installation device with the same serial number already exists')
            else:
                raise BadRequest('Action is impossible')
        return (dev_query, 200)