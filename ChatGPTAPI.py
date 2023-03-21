import json
import os
from logging import getLogger, StreamHandler

import coloredlogs
import discord
import openai

import const

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel("DEBUG")
logger.addHandler(handler)
logger.propagate = False
coloredlogs.install("DEBUG", logger=logger, fmt="%(asctime)s %(levelname)s     %(name)s %(message)s",
                    field_styles=const.DEFAULT_FIELD_STYLES(), level_styles=const.DEFAULT_LEVEL_STYLES())


async def call_api(model="gpt-3.5-turbo", messages=None, temperature=0.5, max_tokens=2000):
    if messages is None:
        messages = []

    if os.getenv('OPENAI_API_KEY') is None:
        logger.critical(" Error : environment variable \"'OPENAI_API_KEY\" is not found")
        exit(1)
    openai.api_key = os.getenv('OPENAI_API_KEY')
    logger.info("call_api " + model + "," + str(temperature) + "," + str(max_tokens))
    with open("./api_response_log/" + discord.utils.utcnow().strftime("%Y_%m_%d_%H_%M_%S") + "_api_response.json",
              mode="w", encoding="utf-8") as r, \
            open("./api_response_log/" + discord.utils.utcnow().strftime("%Y_%m_%d_%H_%M_%S") + "_api_call.json",
                 mode="w", encoding="utf-8") as s:
        send_json = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        response = await openai.ChatCompletion.acreate(**send_json)
        s.write(json.dumps(send_json,ensure_ascii=False))
        r.write(json.dumps(response,ensure_ascii=False))

    with open("api_log.txt", mode="a", encoding="utf-8") as f:
        f.write("api_call at " + discord.utils.utcnow().strftime("%Y: %m/%d %H:%M:%S") +
                ", use " + str(response["usage"]["total_tokens"]) + " tokens\n")

    logger.info("api_call return " + discord.utils.utcnow().strftime("%Y: %m/%d %H:%M:%S") +
                ", use " + str(response["usage"]["total_tokens"]) + " tokens")
    return response
