from faststream.rabbit.fastapi import RabbitRouter

router = RabbitRouter("amqp://guest:guest@localhost:5672/")