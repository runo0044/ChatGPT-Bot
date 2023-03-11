import asyncio
import time
import discord
import openai
import os


async def call_api(model="gpt-3.5-turbo",messages = [],temperature=0.5,max_tokens=2000):
    if os.getenv('OPENAI_API_KEY') is None:
        print(" Error : environment variable \"'OPENAI_API_KEY\" is not found")
        exit(1)
    openai.api_key = os.getenv('OPENAI_API_KEY')
    print("call_api "+model+","+str(temperature)+","+str(max_tokens))
    print(messages)
    response = await openai.ChatCompletion.acreate(
                model=model,
                messages = messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
    with open("api_log.txt",mode="a",encoding="utf-8") as f:
        f.write("api_call at "+discord.utils.utcnow().strftime("%Y: %m/%d %H:%M:%S")+
                ", use "+str(response["usage"]["total_tokens"])+" tokens\n")
    return response

