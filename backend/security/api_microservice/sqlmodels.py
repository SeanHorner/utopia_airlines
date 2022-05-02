from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship


# ------------------------------------------------
#                       Users
# ------------------------------------------------


class UserBase(SQLModel):
    role_id: int = Field(nullable=False, foreign_key="user_role.id")
    given_name: str
    family_name: str
    username: str = Field(nullable=False)
    password: str = Field(nullable=False)
    email: str = Field(nullable=False, index=True)
    phone: str

    user_class: "UserRole" = Relationship(back_populates="users")


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int


class UserUpdate(SQLModel):
    role_id: Optional[int] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class UserAuth(SQLModel):
    username: str
    email: str
    password: str


# ------------------------------------------------
#                      User Roles
# ------------------------------------------------


class UserRoleBase(SQLModel):
    name: str = Field(nullable=False)

    users: List[User] = Relationship(back_populates="user_class")


class UserRole(UserRoleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleRead(UserRoleBase):
    id: int


class UserRoleUpdate(SQLModel):
    name: Optional[str] = None
