import os
from mysql.connector import Error
from database import create_connection

def create_user(connection: object):
    try:
        cursor = connection.cursor()
        query = '''
        CREATE TABLE IF NOT EXISTS user (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            role INT NOT NULL DEFAULT 1,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(20) NOT NULL,
            nickname VARCHAR(20) NOT NULL,
            phone VARCHAR(20),
            phone_verified TINYINT(1) DEFAULT 0,
            profile_image_url VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''
        cursor.execute(query)
        connection.commit()
        print('User table created successfully.')
    except Error as err:
        print(f'Error: "{err}"')
    finally:
        if connection.is_connected():
            cursor.close()

def create_land_info(connection: object):
    try:
        cursor = connection.cursor()
        query = '''
        CREATE TABLE IF NOT EXISTS land_info (
            pnu VARCHAR(20) NOT NULL PRIMARY KEY,
            land_feature_stdr_year INT NOT NULL,
            official_land_price FLOAT NOT NULL,
            predict_land_price FLOAT,
            land_classification VARCHAR(10) NOT NULL,
            land_zoning VARCHAR(20) NOT NULL,
            land_use_situation VARCHAR(20) NOT NULL,
            land_register VARCHAR(10) NOT NULL,
            land_area FLOAT NOT NULL,
            land_height VARCHAR(10) NOT NULL,
            land_form VARCHAR(10) NOT NULL,
            road_side VARCHAR(10) NOT NULL,
            land_uses TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''
        cursor.execute(query)
        connection.commit()
        print('Land info table created successfully.')
    except Error as err:
        print(f'Error: "{err}"')
    finally:
        if connection.is_connected():
            cursor.close()

def create_land_report(connection: object):
    try:
        cursor = connection.cursor()
        query = '''
        CREATE TABLE IF NOT EXISTS land_report (
            report_id INT AUTO_INCREMENT PRIMARY KEY,
            pnu VARCHAR(20) NOT NULL,
            report TEXT NOT NULL,
            `like` INT NOT NULL DEFAULT 0,
            `dislike` INT NOT NULL DEFAULT 0,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pnu) REFERENCES land_info(pnu)
        );
        '''
        cursor.execute(query)
        connection.commit()
        print('Land report table created successfully.')
    except Error as err:
        print(f'Error: "{err}"')
    finally:
        if connection.is_connected():
            cursor.close()

def create_sale(connection: object):
    try:
        cursor = connection.cursor()
        query = '''
        CREATE TABLE IF NOT EXISTS sale (
            sale_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            pnu VARCHAR(20) NOT NULL,
            lat DECIMAL(17,14) NOT NULL,
            lng DECIMAL(17,14) NOT NULL,
            area FLOAT NOT NULL,
            price FLOAT NOT NULL,
            summary TEXT NOT NULL,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user(user_id),
            FOREIGN KEY (pnu) REFERENCES land_info(pnu)
        );
        '''
        cursor.execute(query)
        connection.commit()
        print('Sale table created successfully.')
    except Error as err:
        print(f'Error: "{err}"')
    finally:
        if connection.is_connected():
            cursor.close()

def create_trade_history(connection: object):
    try:
        cursor = connection.cursor()
        query = '''
        CREATE TABLE IF NOT EXISTS trade_history (
            trade_id INT AUTO_INCREMENT PRIMARY KEY,
            pnu VARCHAR(20) NOT NULL,
            land_classification VARCHAR(10) NOT NULL,
            land_zoning VARCHAR(20) NOT NULL,
            deal_year INT NOT NULL,
            deal_month INT NOT NULL,
            deal_price FLOAT NOT NULL,
            deal_area FLOAT NOT NULL,
            deal_type VARCHAR(10)
        );
        '''
        cursor.execute(query)
        connection.commit()
        print('Trade history table created successfully.')
    except Error as err:
        print(f'Error: "{err}"')
    finally:
        if connection.is_connected():
            cursor.close()

def create_region_coordinate(connection: object):
    try:
        cursor = connection.cursor()
        query = '''
        CREATE TABLE IF NOT EXISTS region_coordinate (
            pnu VARCHAR(10) NOT NULL PRIMARY KEY,
            type VARCHAR(12) NOT NULL,
            region VARCHAR(50) NOT NULL,
            lat DECIMAL(17,14) NOT NULL,
            lng DECIMAL(17,14) NOT NULL
        );
        '''
        cursor.execute(query)
        connection.commit()
        print('Region coordinate table created successfully.')
    except Error as err:
        print(f'Error: "{err}"')
    finally:
        if connection.is_connected():
            cursor.close()

def create_geometry_data(connection: object):
    try:
        cursor = connection.cursor()
        query = '''
        CREATE TABLE IF NOT EXISTS geometry_data (
            pnu VARCHAR(10) NOT NULL PRIMARY KEY,
            centroid_lat DECIMAL(17,14) NOT NULL,
            centroid_lng DECIMAL(17,14) NOT NULL,
            multi_polygon LONGTEXT NOT NULL
        );
        '''
        cursor.execute(query)
        connection.commit()
        print('Geometry data table created successfully.')
    except Error as err:
        print(f'Error: "{err}"')
    finally:
        if connection.is_connected():
            cursor.close()

def create_user_favorite_land(connection: object):
    try:
        cursor = connection.cursor()
        query = '''
        CREATE TABLE IF NOT EXISTS user_favorite_land (
            like_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            pnu VARCHAR(20) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user(user_id),
            FOREIGN KEY (pnu) REFERENCES land_info(pnu)
        );
        '''
        cursor.execute(query)
        connection.commit()
        print('Geometry data table created successfully.')
    except Error as err:
        print(f'Error: "{err}"')
    finally:
        if connection.is_connected():
            cursor.close()
