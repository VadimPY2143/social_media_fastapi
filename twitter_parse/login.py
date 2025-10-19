import asyncio
from twikit import Client
from configparser import ConfigParser


config = ConfigParser()
config.read('config.ini')
username = config['X']['username']
email = config['X']['email']
password = config['X']['password']


async def login():
    client = Client(language='en-US')
    await client.login(
        auth_info_1=username,
        auth_info_2=email,
        password=password
    )
    client.save_cookies('cookies.json')




if __name__ == "__main__":
    asyncio.run(login())