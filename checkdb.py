#! bin/python


from pony.orm import *
from model import *
from helpers import *
from config import *

db.bind(**app.config['PONY'])


db.generate_mapping(create_tables=True)



if __name__ == '__main__':
    with db_session:
        print("\n\nAdmin")
        Admin.select().show()
        print("\n\nDirectory")
        Directory.select().show()
        print("\n\nDirectoryVersion")
        DirectoryVersion.select().show()
        print("\n\nDirectoryItem")
        DirectoryItem.select().show()
        print("\n\nSession")
        Session.select().show()
