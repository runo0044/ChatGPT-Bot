import inspect
import os
from logging import getLogger, StreamHandler

import coloredlogs
import discord

import const
from chatchannel import chatChannel
from decode_command import decode_command, decodeParams
import configIo

ON_DEBUG = False


def discord_bot():
    logger = getLogger(__name__)
    handler = StreamHandler()
    handler.setLevel("DEBUG")
    logger.addHandler(handler)
    logger.propagate = False
    coloredlogs.install("DEBUG", logger=logger, fmt="%(asctime)s %(levelname)s     %(name)s %(message)s",
                        field_styles=const.DEFAULT_FIELD_STYLES(), level_styles=const.DEFAULT_LEVEL_STYLES())

    # get api key
    if os.getenv('DISCORD_API_KEY') is None:
        logger.critical(" Error : environment variable \"DISCORD_API_KEY\" is not found")
        exit(1)

    # set bot intents
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True

    client = discord.Client(intents=intents)

    channel_dict = dict()

    async def bot_exit():
        if not ON_DEBUG:
            for channel_id in channel_dict:
                if channel_dict[channel_id].listen:
                    await channel_dict[channel_id].send_message("!Bot shut down!")
        await client.close()

    @client.event
    async def on_ready():
        logger.info(f'We have logged in as {client.user}')

    @client.event
    async def on_message(message):
        # create and register channel class
        if message.channel.id not in channel_dict:
            channel_dict[message.channel.id] = chatChannel(my_user=client.user, my_channel=message.channel,
                                                           listen=configIo.get_config(
                                                               str(message.channel.id) + "listen"))
            configIo.set_config(str(message.channel.id) + "listen", channel_dict[message.channel.id].listen)
        channel = channel_dict[message.channel.id]

        # interprets user commands
        # decode_params:commands list
        p = decodeParams("chat",
                         {"a": {"function": channel.chat_answer},
                          "help": {"function": channel.chat_help},
                          "listen": {"function": channel.chat_listen},
                          "temp": {"function": channel.set_temp,
                                   "need_arguments": {"temp": "float"}},
                          "chara": {"function": channel.character_init,
                                    "need_arguments": {"name": "str"}},
                          "conv": {"function": channel.chat_convert},
                          "setconv": {"function": channel.set_converter,
                                      "opt_arguments": {"name1": "str", "name2": "str", "name3": "str"}},
                          "exit": {"function": bot_exit},
                          "status": {"function": channel.print_status}
                          },
                         {"mention": client.user.mention, "function": channel.chat_mention}
                         )
        try:
            doing = decode_command(message, p)

            # コマンドであれば実行
            if doing["command"]:
                logger.info(doing["function"])
                if doing["function"] == bot_exit:
                    await doing["function"]()
                else:
                    async with message.channel.typing():
                        result = await doing["function"](**doing["arguments"])
                        if inspect.iscoroutine(result):
                            await result
                        else:
                            result
        except Exception as e:
            await channel_dict[message.channel.id].send_message(str(e))

    with open("api_log.txt", mode="a", encoding="utf-8") as f:
        f.write("Bot start at " + discord.utils.utcnow().strftime("%Y: %m/%d %H:%M:%S") + "\n")
    client.run(os.getenv('DISCORD_API_KEY'), log_handler=None)
    with open("api_log.txt", mode="a", encoding="utf-8") as f:
        f.write("Bot stop  at " + discord.utils.utcnow().strftime("%Y: %m/%d %H:%M:%S") + "\n")
