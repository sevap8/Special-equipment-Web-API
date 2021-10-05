## Python web api application.
#### Part of the web api application, performing CRUD operations on one of the system entities, in the example it is implemented:
##### • Entity model "Device" - models.py
##### • Serialized models to create, display, modify - serializers.py
##### • CRUD operations for the "Device" entity - resources.py
##### • URL - urls.py
_____________________________________________________________________

##### -The application has implemented four requests:
#####     POST - entity creation request "device";
#####     GET - getting a list of entities "device";
#####     GET_Id - getting an entity "device" by id;
#####     PUT - entity "device" editing by id;
#####     PUT/DELETE - transfer to inactive (delete).
