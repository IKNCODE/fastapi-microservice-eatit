from fastapi_users import schemas

class UserSchema(schemas.BaseModel):
    login: str
    password: str


class UserCreate(schemas.BaseUserCreate):
    login: str
    email: str
    password: str
    is_active: bool
    is_superuser: bool
