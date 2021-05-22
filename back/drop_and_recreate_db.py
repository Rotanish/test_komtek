#! bin/python


from os import urandom
from hashlib import md5

from pony.orm import *
from model import *
from helpers import *
from config import *
from routes import my_hash, password_secret

db.bind(**app.config['PONY'])

db.generate_mapping(create_tables=True)

db.drop_all_tables(with_all_data=True)

db.create_tables()


@db_session
def test_add():
    s = md5(urandom(25)).hexdigest()
    Admin(login='test',
          password_hash=my_hash(
              password_secret + 'test'.encode() + s.encode()
              ).hexdigest(),
          password_salt=s,
          reg_time=datetime.now()
          )
    d1 = Directory(name='dir_test1',
                   short_name='d1',
                   description='d1'
                   )
    d2 = Directory(name='dir_test2',
                   )
    for i in range(1000):
        Directory(name=str(i))
    flush()
    d1v1 = DirectoryVersion(directory=d1,
                            version='1',
                            date_start=date(2005, 2, 19),
                            )
    d1v2 = DirectoryVersion(directory=d1,
                            version='1.1',
                            date_start=date.today(),
                            )
    d2v1 = DirectoryVersion(directory=d2,
                            version='1',
                            date_start=date(2005, 2, 19),
                            )
    flush()
    DirectoryItem(version=d1v1,
                  code='код',
                  value='значение'
                  )
    DirectoryItem(version=d1v2,
                  code='код',
                  value='значение'
                  )
    DirectoryItem(version=d1v2,
                  code='код2',
                  value='значение2'
                  )
    for i in range(1000):
        DirectoryItem(version=d2v1,
                      code=str(i),
                      value='значение'
                      )
    flush()


if __name__ == '__main__':
    test_add()
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
