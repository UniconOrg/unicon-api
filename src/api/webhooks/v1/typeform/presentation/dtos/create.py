from pydantic import BaseModel



class ResponseTypeformDto(BaseModel):
    event_id: str
    event_type: str
    form_response: dict
