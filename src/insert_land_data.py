import os
import sys
import json
sys.path.append('/home/kumap/land-price-backend/')
from app.config import BASE_DIR
from app.functions.geo import get_coord
from src.database import create_connection, USER_NAME, USER_PW, DATABASE_NAME

def insert_region_coordinates(connection: object):
  try:
    print('# Insert region coordinates data')
    cursor = connection.cursor()
    query = '''
    INSERT INTO region_coordinate
    (pnu, type, region, lat, lng)
    VALUES
    (%s, %s, %s, %s, %s);
    '''
    with open(os.path.join(BASE_DIR, 'data/PnuCode.csv'), 'r', encoding='utf-8') as rcf:
      lines = rcf.readlines()
    count = 0
    for line in lines:
      count += 1
      print(f'\r#   {count:5d}/{len(lines):5d}', end='')
      if line.split(',')[1] in ['sido']:
        continue
      if line.split(',')[4] == '' or line.split(',')[4] == '\n':
        if line.split(',')[3] == '':
          if line.split(',')[2] == '':
            connection.commit()
            lat, lng = get_coord(line.split(',')[1])
            cursor.execute(query, (line.split(',')[0][0:2], 'sido', line.split(',')[1], lat, lng))
          else:
            lat, lng = get_coord(line.split(',')[1] + ' ' + line.split(',')[2])
            cursor.execute(query, (line.split(',')[0][0:5], 'sigungu', line.split(',')[2], lat, lng))
        else:
          lat, lng = get_coord(line.split(',')[1] + ' ' + line.split(',')[2] + ' ' + line.split(',')[3])
          cursor.execute(query, (line.split(',')[0][0:8], 'eupmyeondong', line.split(',')[3], lat, lng))
  except Exception as e:
    print(e)
  connection.commit()

def insert_cadastral_data(connection: object):
  print('# Insert cadastral map data')
  cursor = connection.cursor()
  query = '''
    INSERT INTO geometry_data
    (pnu, centroid_lat, centroid_lng, multi_polygon)
    VALUES
    (%s, %s, %s, %s);
  '''
  for scale in ['emd', 'sig', 'sido']:
    with open(os.path.join(BASE_DIR, 'src/dataset/cadastralmap', scale + '.json'), 'r') as gf:
      data = json.load(gf)
    polygons = data['features']
    count = 1
    for polygon in polygons:
      centroids = []
      total_area = 0
      try:
        for p in polygon['geometry']['coordinates']:
          for coords in p:
            x_sum = 0
            y_sum = 0
            n = len(coords)
            for coord in coords:
              x_sum += coord[1]
              y_sum += coord[0]
            centroid = [y_sum/n, x_sum/n]
            centroids.append(centroid)
            total_area += 1
        x_sum = sum([centroid[1] for centroid in centroids])
        y_sum = sum([centroid[0] for centroid in centroids])
        centroid = [y_sum/total_area, x_sum/total_area]
        if scale == 'emd':
          print(f'({count:4d}/{len(polygon):4d}) {polygon["properties"]["EMD_CD"]}')
          cursor.execute(query, (polygon['properties']['EMD_CD'], centroid[1], centroid[0], json.dumps(polygon['geometry']['coordinates'])))
          connection.commit()
          count += 1
        elif scale == 'sig':
          print(f'({count:4d}/{len(polygon):4d}) {polygon["properties"]["SIG_CD"]}')
          cursor.execute(query, (polygon["properties"]["SIG_CD"], centroid[1], centroid[0], json.dumps(polygon['geometry']['coordinates'])))
          connection.commit()
          count += 1
        elif scale == 'sido':
          print(f'({count:4d}/{len(polygon):4d}) {polygon["properties"]["CTPRVN_CD"]}')
          cursor.execute(query, (polygon['properties']['CTPRVN_CD'], centroid[1], centroid[0], json.dumps(polygon['geometry']['coordinates'])))
          connection.commit()
          count += 1
      except Exception as e:
        print(e)

if __name__ == '__main__':
  connection = create_connection('localhost', USER_NAME, USER_PW, DATABASE_NAME)
  # insert_region_coordinates(connection)
  insert_cadastral_data(connection)
  connection.close()