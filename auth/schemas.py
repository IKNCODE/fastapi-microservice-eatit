from fastapi_users import schemas

class UserSchema(schemas.BaseUser):
    id: int
    login: str
    email: str
    password: str
    is_active: bool
    is_superuser: bool


class UserCreate(schemas.BaseUserCreate):
    login: str
    email: str
    password: str
    is_active: bool
    is_superuser: bool
