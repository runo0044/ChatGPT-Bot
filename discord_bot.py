import discord
import asyncio
import inspect
from chat_channel import chat_channel
from decode_command import decode_command, decode_params
import time
import threading
import os


def discord_bot():
    if os.getenv('DISCORD_API_KEY') is None:
        print(" Error : environment variable \"DISCORD_API_KEY\" is not found")
        exit(1)
    typing_flag = False
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True

    client = discord.Client(intents=intents)

    channel_dict = dict()

    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')

    @client.event
    async def on_message(message):
        # print("get:"+message.content)
        # チャンネル管理クラスの作成
        if not message.channel.id in channel_dict:
            channel_dict[message.channel.id] = chat_channel(myuser=client.user, mychannel=message.channel)
        channel = channel_dict[message.channel.id]

        # メッセージをコマンドとして解釈
        # decode_params:コマンド一覧
        p = decode_params("chat",
                          {"a": {"function": channel.chat_answer},
                           "help": {"function": channel.chat_help},
                           "listen": {"function": channel.chat_listen},
                           "temp": {"function": channel.set_temp,
                                    "need_arguments": {"temp": "float"}},
                           "chara": {"function": channel.character_init,
                                     "need_arguments": {"name": "str"}}
                           },
                          {"mention": client.user.mention, "function": channel.chat_mention}
                          )
        doing = decode_command(message, p)

        # コマンドであれば実行
        if doing["command"]:
            print(doing["function"])
            async with message.channel.typing():
                result = await doing["function"](**doing["arguments"])
                if inspect.iscoroutine(result):
                    await result
                else:
                    result

    with open("api_log.txt", mode="a", encoding="utf-8") as f:
        f.write("Bot start at " + discord.utils.utcnow().strftime("%Y: %m/%d %H:%M:%S") + "\n")
    client.run(os.getenv('DISCORD_API_KEY'))
    with open("api_log.txt", mode="a", encoding="utf-8") as f:
        f.write("Bot stop  at " + discord.utils.utcnow().strftime("%Y: %m/%d %H:%M:%S") + "\n")
