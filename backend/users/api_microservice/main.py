# ######################################################################################################################
# ########################################                               ###############################################
# ########################################              Main             ###############################################
# ########################################                               ###############################################
# ######################################################################################################################
import os
from typing import Optional, List

from .sqlmodels import (
    User, UserRead, UserCreate, UserUpdate, UserAuth,
    UserRole, UserRoleRead, UserRoleCreate, UserRoleUpdate
)

from fastapi import FastAPI, HTTPException, Depends, Query
from sqlmodel import Session, create_engine, SQLModel
from werkzeug.security import generate_password_hash

SQLALCHEMY_DATABASE_URL = os.getenv('DB_ACCESS_URI') or "mysql+pymysql://root:root@127.0.0.1:6603/utopia"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

app = FastAPI()


# ######################################################################################################################
# ########################################                               ###############################################
# ########################################          API Routes           ###############################################
# ########################################                               ###############################################
# ######################################################################################################################


# ------------------------------------------------
#                 Session Creator
# ------------------------------------------------


def get_session():
    with Session(engine) as session:
        yield session


# ------------------------------------------------
#                 Startup DB Creation
# ------------------------------------------------


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


# ------------------------------------------------
#                   Roll Call
# ------------------------------------------------


@app.get("/",
         tags=["infrastructure"],
         summary="Default landing url and presence check.")
def present():
    return {"msg": "Users microservice is present and ready for action."}


# ------------------------------------------------
#                   Health Check
# ------------------------------------------------


@app.get("/health",
         tags=["infrastructure"],
         summary="Health check url for ECS/EKS")
def health_check():
    """
    Both ECS and EKS like to have a health check route to ensure that a service
    is accessible and working.

    :return: Generic health message JSON.
    """
    return {"msg": "Healthy"}


# ------------------------------------------------
#                       Users
# ------------------------------------------------

# --------------------  Create  ------------------


@app.post("/api/v2/users/",
          response_model=UserRead,
          tags=["users"],
          summary="Create new users",
          response_description="Info for newly created user from database.")
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """
        Create an item with all the information:

        - **role_id**: the user's role id, indicating permissions
        - **given_name**: user's first/identifying name
        - **family_name**: user's last/family/clan name
        - **username**: user's identifying name on the service and for login
        - **email**: user's email for communication and alternate login credential
        - **phone**: user's phone number for verification and 2FA/MFA
    """
    db_user = session                           \
        .query(User)                            \
        .filter(User.email == user.email)       \
        .first()

    if db_user:
        raise HTTPException(
            status_code=400,
            detail="That email is already in use."
        )

    hashed_password = generate_password_hash(user.password)
    user.password = hashed_password
    new_user = User.from_orm(user)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


# --------------------   Read   ------------------


@app.get("/api/v2/users/{user_id}", response_model=UserRead, tags=["users"])
def get_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session                   \
        .query(User)                    \
        .filter(User.id == user_id)     \
        .first()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return db_user


@app.get("/api/v2/users/email/{user_email}", response_model=UserRead, tags=["users"])
def get_user_by_email(user_email: str, session: Session = Depends(get_session)):
    db_user = session                           \
        .query(User)                            \
        .filter(User.email == user_email)       \
        .first()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return db_user


@app.get("/api/v2/users/username/{username}", response_model=UserRead, tags=["users"])
def get_user_by_username(username: str, session: Session = Depends(get_session)):
    db_user = session                           \
        .query(User)                            \
        .filter(User.username == username)      \
        .first()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return db_user


@app.get("/api/v2/users/", response_model=List[UserRead], tags=["users"])
def get_users(skip: int = 0,
              limit: int = Query(default=100, lte=100),
              session: Session = Depends(get_session)):
    users = session         \
        .query(User)        \
        .offset(skip)       \
        .limit(limit)       \
        .all()

    # In python, an empty list is treated as a boolean False, so triggers if users is empty
    if not users:
        raise HTTPException(
            status_code=404,
            detail="No users found."
        )

    return users


@app.get("/api/v2/users/role_id/{role_id}", response_model=List[UserRead], tags=["users"])
def get_users_by_role(role_id: int, session: Session = Depends(get_session)):
    db_users = session                               \
        .query(User)                            \
        .filter(User.role_id == role_id)        \
        .all()

    # In python, an empty list is treated as a boolean False, so triggers if db_users is empty
    if not db_users:
        raise HTTPException(
            status_code=404,
            detail="No users with that role."
        )

    return db_users


@app.get("/api/v2/users/ids/", tags=["users"])
def get_user_ids(skip: int = 0,
                 limit: int = Query(default=100, lte=100),
                 session: Session = Depends(get_session)):
    users = session             \
        .query(User)            \
        .offset(skip)           \
        .limit(limit)           \
        .all()

    # In python, an empty list is treated as a boolean False, so triggers if user_ids is empty
    if not users:
        raise HTTPException(
            status_code=404,
            detail="No more users in database."
        )

    user_ids = [user.id for user in users]

    return user_ids


@app.get("/api/v2/users/{username}/auth", response_model=UserAuth, tags=["users"])
def get_user_auth(username: str, session: Session = Depends(get_session)):
    db_user = session                                \
        .query(User)                            \
        .filter(User.username == username)      \
        .first()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return db_user


# --------------------  Update  ------------------


@app.patch("/api/v2/users/{user_id}", response_model=UserRead, tags=["users"])
def update_user(user_id: int, user: UserUpdate, session: Session = Depends(get_session)):
    db_user = session                   \
        .query(User)                    \
        .filter(User.id == user_id)     \
        .first()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user_data = user.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


# --------------------  Delete  ------------------


@app.delete("/api/v2/users/{user_id}", tags=["users"])
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session                        \
        .query(User)                    \
        .filter(User.id == user_id)     \
        .first()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    session.delete(db_user)
    session.commit()

    return {"ok": True}


# ------------------------------------------------
#                      User Roles
# ------------------------------------------------

# --------------------  Create  ------------------

@app.post("/api/v2/user_roles/", response_model=UserRoleRead, tags=["user roles"])
def create_user_role(role: UserRoleCreate, session: Session = Depends(get_session)):
    db_role = session                           \
        .query(UserRole)                        \
        .filter(UserRole.name == role.name)     \
        .first()

    if db_role:
        raise HTTPException(
            status_code=404,
            detail="User role with that name already exists."
        )

    new_role = UserRole.from_orm(role)

    session.add(new_role)
    session.commit()
    session.refresh(new_role)

    return new_role


# --------------------   Read   ------------------


@app.get("/api/v2/user_roles/{role_id}", response_model=UserRoleRead, tags=["user roles"])
def get_user_role(role_id: int, session: Session = Depends(get_session)):
    db_role = session                       \
        .query(UserRole)                    \
        .filter(UserRole.id == role_id)     \
        .first()

    if not db_role:
        raise HTTPException(
            status_code=404,
            detail="User role not found."
        )

    return db_role


@app.get("/api/v2/user_roles/", response_model=List[UserRoleRead], tags=["user roles"])
def get_user_roles(skip: int = 0,
                   limit: int = Query(default=100, lte=100),
                   session: Session = Depends(get_session)):
    user_roles = session        \
        .query(UserRole)        \
        .offset(skip)           \
        .limit(limit)           \
        .all()

    if not user_roles:
        raise HTTPException(
            status_code=404,
            detail="No user roles found."
        )

    return user_roles


@app.get("/api/v2/user_roles/name/{name}", response_model=UserRoleRead, tags=["user roles"])
def get_user_role_by_name(name: str, session: Session = Depends(get_session)):
    db_role = session                       \
        .query(UserRole)                    \
        .filter(UserRole.name == name)      \
        .first()

    if not db_role:
        raise HTTPException(
            status_code=404,
            detail="No user role with that name."
        )

    return db_role


# --------------------  Update  ------------------


@app.patch("/api/v2/user_roles/{role_id}",
           response_model=UserRoleRead,
           tags=["user_roles"])
def patch_user_role(role_id: int, role: UserRoleUpdate, session: Session = Depends(get_session)):
    db_role = session                   \
        .query(UserRole)                \
        .filter(UserRole.id == role_id) \
        .first()

    if not db_role:
        raise HTTPException(
            status_code=404,
            detail="User role not found"
        )

    role_data = role.dict(exclude_unset=True)
    for key, value in role_data.items():
        setattr(db_role, key, value)

    session.add(db_role)
    session.commit()
    session.refresh(db_role)

    return db_role


# --------------------  Delete  ------------------


@app.delete("/api/v2/user_roles/{role_id}", tags=["user roles"])
def delete_user_role(role_id: int, session: Session = Depends(get_session)):
    db_role = session                       \
        .query(UserRole)                    \
        .filter(UserRole.id == role_id)     \
        .first()

    if not db_role:
        raise HTTPException(
            status_code=404,
            detail="User role not found."
        )

    session.delete(db_role)
    session.commit()

    return {'ok': True}
