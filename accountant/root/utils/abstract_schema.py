from pydantic import BaseModel, ConfigDict


class AbstractModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)
