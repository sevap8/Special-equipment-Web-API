from directory.resources import (api, DeviceListCreate, DeviceDetail)
                                     
# devices
api.add_resource(DeviceListCreate, '/devices')
api.add_resource(DeviceDetail, '/devices/<string:dev_id>')

