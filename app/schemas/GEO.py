from pydantic import BaseModel, Field
from typing import Optional, List, Union
from app.schemas import KUMapBaseResponse

# data schema
class AddressSchema(BaseModel):
  sido: Optional[str] = Field(None, description='Province/City')
  sigungu: Optional[str] = Field(None, description='City/District')
  eupmyeondong: Optional[str] = Field(None, description='Township/Village')
  donglee: Optional[str] = Field(None, description='Neighborhood')
  detail: Optional[str] = Field(None, description='Detailed address (if applicable)')
  fulladdr: Optional[str] = Field(None, description='Full formatted address')

# requests
class GetPNURequest(BaseModel):
  lat: float = Field(..., description='Latitude coordinate')
  lng: float = Field(..., description='Longitude coordinate')

class GetCoordRequest(BaseModel):
  word: Optional[str] = Field(None, description='Land parcel address')

class AutoCompleteAddressRequest(BaseModel):
  query: str = Field(..., description='Search query')


# responses
class GetPNUResponse(KUMapBaseResponse):
  pnu: str = Field(..., description='19-digit PNU code')
  address: AddressSchema = Field(..., description='Land parcel address details')

class GetCoordResponse(KUMapBaseResponse):
  lat: float = Field(..., description='Latitude coordinate')
  lng: float = Field(..., description='Longitude coordinate')
  address: str = Field(..., description='Land parcel address')

class AutoCompleteAddressResponse(KUMapBaseResponse):
  related_search: list

class GetCadastralMapResponse(KUMapBaseResponse):
    polygons: list
