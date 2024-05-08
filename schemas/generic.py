from pydantic import BaseModel

class ResponseMsg(BaseModel):
    msg: str
