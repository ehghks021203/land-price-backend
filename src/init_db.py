from database import make_database, create_connection, USER_NAME, USER_PW, DATABASE_NAME
from database.create_tables import *

if __name__ == '__main__':
  # create user & create database & grant privileges
  make_database.make()
  print('localhost', USER_NAME, USER_PW, DATABASE_NAME)
  
  # create tables
  connection = create_connection('localhost', USER_NAME, USER_PW, DATABASE_NAME)
  create_user(connection)
  create_land_info(connection)
  create_land_report(connection)
  create_listing(connection)
  create_trade_history(connection)
  create_region_coordinate(connection)
  create_geometry_data(connection)
  create_user_favorite_land(connection)
  connection.close()
  print('Database initialize.')
