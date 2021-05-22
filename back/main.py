#! bin/python


from config import db, app
from routes import *

db.bind(**app.config['PONY'])
db.generate_mapping(create_tables=True)

application = app

if __name__ == '__main__':

    application.run(host='0.0.0.0')