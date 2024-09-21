from fastapi import HTTPException, APIRouter, UploadFile, File, Depends
from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import Session
from database import post_table, engine
from posts.models import Post


router = APIRouter(
    tags=['Posts'],
    prefix='/posts'
)


@router.post('/post/create')
async def create_post(post: Post = Depends(), file: UploadFile = File(None)) -> dict:
    picture_data = None
    if file:
        picture_data = await file.read()

    with Session(engine) as session:
        stmt = insert(post_table).values(
            post_name=post.post_name,
            author=post.author,
            text=post.text,
            picture=picture_data or b""
        )
        session.execute(stmt)
        session.commit()

    return {
        'Post Name': post.post_name,
        'Author': post.author,
        'Text': post.text,
        'Image': picture_data is not None
    }


@router.get('/post/get')
def read_post(post_id: int) -> dict:
    with Session(engine) as session:
        stmt = select(post_table).where(post_table.c.id == post_id)
        result = session.execute(stmt).fetchone()
        if result:
            result_dict = {
                'id': result[0],
                'post_name': result[1],
                'author': result[2],
                'text': result[3],
                'picture': result[4] is not None
            }
            return result_dict
        raise HTTPException(status_code=404, detail=f'There is no post with id {post_id}')


@router.put('/post/update')
def post_update(post: Post, post_id: int) -> dict:
    with Session(engine) as session:
        stmt = update(post_table).where(post_table.c.id == post_id).values(post_name=post.post_name, text=post.text)
        session.execute(stmt)
        session.commit()
        stmt = select(post_table).where(post_table.c.id == post_id)
        result = session.execute(stmt).fetchone()
        if result:
            result_dict = {
                'id': result[0],
                'post_name': result[1],
                'author': result[2],
                'text': result[3],
                'picture': result[4] is not None
            }
            return result_dict
        raise HTTPException(status_code=404, detail=f'There is no post with id {post_id}')


@router.delete('/post/delete')
def post_delete(post_id: int) -> dict:
    with Session(engine) as session:
        stmt = select(post_table).where(post_table.c.id == post_id)
        result = session.execute(stmt).fetchone()
        if result:
            delete_stmt = delete(post_table).where(post_table.c.id == post_id)
            session.execute(delete_stmt)
            session.commit()
            return {'message': 'Successfully deleted'}

        raise HTTPException(status_code=404, detail=f'There is no post with id {post_id}')
