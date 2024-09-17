from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from weather_parse.weather import get_weather
from posts.crud_posts import router as post_router
from twitter_parse.parse_tweet import router as twitter_router
from authentication.crud_users import router as user_router

app = FastAPI()
app.include_router(post_router)
app.include_router(twitter_router)
app.include_router(user_router)


@app.websocket('/get_weather')
async def websocket_(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            location = await websocket.receive_text()
            await websocket.send_json(get_weather(location))
    except WebSocketDisconnect:
        await websocket.close()




