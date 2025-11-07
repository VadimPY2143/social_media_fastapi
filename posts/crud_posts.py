from urllib.request import Request
from better_profanity import profanity
from fastapi import HTTPException, APIRouter, UploadFile, File, Depends, Path, Request
from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import Session
from database import post_table, engine, user_table
from posts.models import Post, PostUpdate


router = APIRouter(
    tags=['Posts'],
    prefix='/posts'
)


@router.post('/post/create/{author_id}')
async def create_post(post: Post = Depends(), file: UploadFile = File(None), author_id: int = Path(..., ge=1)) -> dict:
    picture_data = None

    if profanity.contains_profanity(post.post_name):
        raise HTTPException(status_code=400, detail="Bad words are not allowed")

    elif profanity.contains_profanity(post.text):
        raise HTTPException(status_code=400, detail="Bad words are not allowed")

    if file:
        picture_data = await file.read()
    with Session(engine) as session:
        stmt1 = select(user_table.c.username).where(user_table.c.id == author_id)
        author = session.execute(stmt1).scalar_one_or_none()
        if author:
            stmt2 = insert(post_table).values(
                post_name=post.post_name,
                author=author_id,
                text=post.text,
                picture=picture_data or b""
            )
            session.execute(stmt2)
            session.commit()
            return {
                    'Post Name': post.post_name,
                    'Author': author,
                    'Text': post.text,
                    'Image': picture_data is not None
                    }
        else:
            raise HTTPException(status_code=404, detail='No such author')



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

@router.post('/post/get_all')
def read_all_posts() -> dict:
    with Session(engine) as session:
        stmt = select(post_table)
        result = session.execute(stmt)
        result_dict = {}

        for data in result:
            post = {'id': data[0],
                    'post_name': data[1],
                    'author': data[2],
                    'text': data[3],
                    'picture': data[4] is not None}
            result_dict[data[0]] = post

        if result_dict:
            return result_dict
        raise HTTPException(status_code=404, detail=f'There is no posts')


@router.put('/post/update')
def post_update(post_id: int, post: PostUpdate = Depends()) -> dict:
    with Session(engine) as session:
        if profanity.contains_profanity(post.text) or profanity.contains_profanity(post.post_name):
            raise HTTPException(status_code=400, detail="Bad words are not allowed")
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
            session.close()
            return result_dict
        raise HTTPException(status_code=404, detail=f'There is no post with id {post_id}')


@router.delete('post/delete')
def post_delete(post_id: int):
    with Session(engine) as session:
        stmt = delete(post_table).where(post_table.c.id == post_id)
        result = session.execute(stmt)
        if result:
            session.commit()
            return {'message': 'The post has been deleted'}

        else:
            raise HTTPException(status_code=404, detail=f'There is no post with id {post_id}')

