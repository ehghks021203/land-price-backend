from pydantic import BaseModel

class KUMapBaseResponse(BaseModel):
  status: str
  message: str
  err_code: str
