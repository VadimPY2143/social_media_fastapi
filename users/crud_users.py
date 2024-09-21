from fastapi import HTTPException, APIRouter, status, Depends
from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import Session
from database import user_table, engine
from .models import UserCreate, UpdateUser


router = APIRouter(
    tags=['Users'],
    prefix='/users'
)


@router.post('/user/create')
async def create_user(user: UserCreate = Depends()) -> dict:
    with Session(engine) as session:
        stmt = insert(user_table).values(
            username=user.username,
            email=user.email,
            password=user.password.get_secret_value()
        )
        session.execute(stmt)
        session.commit()

    return {
        'username': user.username,
        'email': user.email,
        'password': '*' * len(user.password)
    }


@router.get('/user/get')
async def get_user(user_id: int) -> dict:
    with Session(engine) as session:
        stmt = select(user_table).where(user_table.c.id == user_id)
        result = session.execute(stmt).fetchone()
        if result:
            result_dict = {
                'id': result[0],
                'username': result[1],
                'email': result[2],
                'password': result[3]
            }
            return result_dict
        raise HTTPException(status_code=404, detail=f'There is no user with id {user_id}')


@router.put('/user/update')
async def update_user(user_upd: UpdateUser, user_id: int) -> dict:
    with Session(engine) as session:
        stmt = select(user_table).where(user_table.c.id == user_id)
        user_data = session.execute(stmt).fetchone()
        if user_data[2] == user_upd.old_email and user_data[3] == user_upd.old_password:
            stmt = update(user_table).where(user_table.c.id == user_id).values(username=user_upd.new_username,
                                                                               email=user_upd.new_email,
                                                                               password=user_upd.new_password)
            session.execute(stmt)
            session.commit()
            stmt = select(user_table).where(user_table.c.id == user_id)
            user_data = session.execute(stmt).fetchone()

        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Wrong password or email!')

        if user_data:
            result_dict = {
             'id': user_data[0],
             'username': user_data[1],
             'email': user_data[2],
             'password': user_data[3],
            }
            return result_dict
        raise HTTPException(status_code=404, detail=f'There is no user with id {user_id}')


@router.delete('/user/delete/{user_id}')
async def delete_user(user_id: int) -> dict:
    with Session(engine) as session:
        stmt = select(user_table).where(user_table.c.id == user_id)
        result = session.execute(stmt).fetchone()
        if result:
            delete_stmt = delete(user_table).where(user_table.c.id == user_id)
            session.execute(delete_stmt)
            session.commit()
            return {'message': 'Successfully deleted'}

        raise HTTPException(status_code=404, detail=f'There is no user with id {user_id}')



