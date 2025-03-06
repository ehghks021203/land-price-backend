from sqlalchemy import Column, String, Text
from sqlalchemy.types import Numeric
from app import Base

class GeometryData(Base):
    __tablename__ = 'geometry_data'

    pnu = Column(String(10), primary_key=True, nullable=False, comment='Parcel number (PNU)')
    centroid_lat = Column(Numeric(17, 14), nullable=False, comment='Centroid Latitude')
    centroid_lng = Column(Numeric(17, 14), nullable=False, comment='Centroid Longitude')
    multi_polygon = Column(Text, nullable=False, comment='GeoJSON MultiPolygon data')

    def __repr__(self):
        return f'<GeometryData(pnu={self.pnu}, centroid_lat={self.centroid_lat}, centroid_lng={self.centroid_lng})>'
