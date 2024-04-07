from pydantic import BaseModel


class TextRequest(BaseModel):
    input: str
    config: dict
    kwargs: dict


class TextResponse(BaseModel):
    content: str
    additional_kwargs: dict
    type: str
