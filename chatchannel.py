import json
from logging import getLogger, StreamHandler

import coloredlogs

import ChatGPTAPI
import configIo
import const
import make_charafile
from tiktoken_wrapper import num_tokens_from_messages


class characterStatus:
    """
    bot Character definition file
    Attributes
    ----------
    system_message : list
        Opening message
    temp : float
        parameter "temperature"
    send_token : int
        Maximum number of sending tokens
    receive_token : int
        Maximum number of reply tokens
    messages_preloaded : int
        Number of past messages to reference (subject to token limits)
    send_user_name : bool
        Whether to send the username
    """

    def __init__(self, system_message, temp=0.5, send_token=1000, receive_token=1000,
                 messages_preloaded=200, send_user_name=True, name="def"):
        self.system_message = system_message
        self.temp = temp
        self.send_token = send_token
        self.receive_token = receive_token
        self.messages_preloaded = messages_preloaded
        self.send_user_name = send_user_name
        self.name = name

    def toString(self):
        return "name : " + self.name + \
                "\ntemp : " + str(self.temp) + \
                "\ntoken : " + str(self.send_token) + " send / " + str(self.receive_token) + " receive"


logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel("DEBUG")
logger.addHandler(handler)
logger.propagate = False
coloredlogs.install("INFO", logger=logger, fmt="%(asctime)s %(levelname)s     %(name)s %(message)s",
                    field_styles=const.DEFAULT_FIELD_STYLES(), level_styles=const.DEFAULT_LEVEL_STYLES())


def get_character_status(name):
    """
    load character_status by file
    :param name: file_name
    :return: character_status object
    """
    if name is None:
        name = "def"
    try:
        with open("character profile/" + name + ".json", mode="r", encoding="utf-8") as f:
            text = f.read()
            logger.info("character file " + name + ".json is loading")
            return characterStatus(**json.loads(text), name=name)
    except Exception as e:
        logger.error(e)
        try:
            make_charafile.set_TARGET("character profile/" + name + ".txt")
            make_charafile.load_chara()
            try:
                with open("character profile/" + name + ".json", mode="r", encoding="utf-8") as f:
                    text = f.read()
                    return characterStatus(**json.loads(text), name=name)
            except Exception as e:
                logger.error("create character file, but this is broken")
                logger.error(e)

        except Exception as e:
            logger.error("character file is not found")
            logger.error(e)


class chatChannel:

    def __init__(self, my_user, my_channel, listen=False):
        # bot channel status
        if listen is None:
            listen = False
        self.listen = listen
        chara_name = configIo.get_config(str(my_channel.id) + "chara")
        if chara_name is None:
            chara_name = "def"
            configIo.set_config(str(my_channel.id) + "chara", "def")
        self.chara_status = get_character_status(chara_name)
        self.converter_status = []
        self.use_converter_at_all = False

        # sender
        self.message = []
        self.chat_history = []

        # discord channel status
        self.my_user = my_user
        self.my_channel = my_channel

        # get logger
        self.logger = getLogger(__name__ + str(my_channel.id))
        _handler = StreamHandler()
        _handler.setLevel("DEBUG")
        self.logger.addHandler(_handler)
        self.logger.propagate = False
        coloredlogs.install("INFO", logger=self.logger, fmt="%(asctime)s %(levelname)s     %(name)s %(message)s",
                            field_styles=const.DEFAULT_FIELD_STYLES(), level_styles=const.DEFAULT_LEVEL_STYLES())
        if listen is not None:
            self.logger.debug("listen load" + str(listen))

    async def send_message(self, value: str):
        await self.my_channel.send(value)

    async def print_status(self):
        text = "!status\nlisten : " + str(self.listen) + "\ncharacter " + self.chara_status.toString()
        if len(self.converter_status) == 0:
            text = text + "\nconverter is None"
        else:
            text = text + "\nconverter : "
            for conv in self.converter_status:
                text = text + conv.name + " : "
        return self.my_channel.send(text)

    def character_init(self, name: str):
        try:
            self.chara_status = get_character_status(name)
            self.listen = True
            configIo.set_config(str(self.my_channel.id) + "chara", name)
            configIo.set_config(str(self.my_channel.id) + "listen", True)
            return self.my_channel.send("!setting character file " + name)
        except Exception as e:
            self.logger.error(e)
            return self.my_channel.send("!Error character file is not found")

    async def set_converter(self, name1=None, name2=None, name3=None):
        try:
            self.converter_status = []
            if name1 is not None:
                self.converter_status.append(get_character_status(name1))
            if name2 is not None:
                self.converter_status.append(get_character_status(name2))
            if name3 is not None:
                self.converter_status.append(get_character_status(name3))
            if len(self.converter_status) == 0:
                self.use_converter_at_all = False
                return self.my_channel.send("!reset converter")
            else:
                text = ""
                if name1 is not None:
                    text = text + name1
                if name2 is not None:
                    text = text + " " + name2
                if name3 is not None:
                    text = text + " " + name3
                return self.my_channel.send("!set converter "+text)
        except Exception as e:
            self.logger.error(e)
            self.my_channel.send("!Error " + str(e))

    async def converting_init(self, text):
        self.message = []
        self.message.append({"role": "user", "content": text})

    async def __converting__(self, mention=None):
        for converter in self.converter_status:
            try:
                response = await ChatGPTAPI.call_api("gpt-3.5-turbo", converter.system_message + self.message,
                                                     converter.temp, max_tokens=2000)
                self.message[0]["content"] = response["choices"][0]["message"]["content"]
            except Exception as e:
                self.logger.error(e)
                return self.my_channel.send("!Error API Call failed\n" + str(e))

        if len(self.converter_status) > 0:
            text = response["choices"][0]["message"]["content"]
        else:
            text = "!Error converter is not setting"

        if mention is not None:
            text = mention + text
        return self.my_channel.send(text)

    async def chat_convert(self):
        if not self.listen:
            return self.my_channel.send("!Error I can't read this channel. For more information !chat help")

        await self.get_last_message()
        return await self.__converting__()

    async def chat_answer(self):
        if not self.listen:
            return self.my_channel.send("!Error I can't read this channel. For more information !chat help")
        await self.history2message()
        try:
            response = await ChatGPTAPI.call_api("gpt-3.5-turbo", self.chara_status.system_message + self.message,
                                                 self.chara_status.temp, self.chara_status.receive_token)
        except Exception as e:
            self.logger.error(e)
            return self.my_channel.send("!Error API Call failed\n" + str(e))
        if self.chara_status.send_user_name:
            text = response["choices"][0]["message"]["content"].split("「", 1)[-1].rstrip("」")
        else:
            text = response["choices"][0]["message"]["content"]

        if self.use_converter_at_all:
            await self.converting_init(text)
            return await self.__converting__()
        else:
            return self.my_channel.send(text)

    async def chat_mention(self, message):
        # mention only -> !chat answer
        if message.content.replace(self.my_user.mention, "").lstrip() == "":
            return await self.chat_answer()

        # answer a question
        try:
            response = await ChatGPTAPI.call_api(messages=[{"role": "system", "content": "あなたは役に立つアシスタントです。"},
                                                           {"role": "user",
                                                            "content": message.content.replace(self.my_user.mention,
                                                                                               "")}])
            text = response["choices"][0]["message"]["content"]
            if self.use_converter_at_all:
                await self.converting_init(text)
                return await self.__converting__(message.author.mention)
            else:
                return self.my_channel.send(text)
            # return self.my_channel.send(message.author.mention + response["choices"][0]["message"]["content"])
        except Exception as e:
            self.logger.error(e)
            return self.my_channel.send("!Error API Call failed\n" + str(e))

    def chat_help(self):
        return self.my_channel.send(
            "!ChatGPT-API Discord Bot\n"
            "ver0.5 2023/03/21\n\n"
            "command list \n"
            "!chat a : answer chats based on history.\n"
            "!split : Bot can't read the message history prior to this command.\n"
            "!chat listen : Allow or not allow this channel to be read.\n"
            "!chat chara : import character file.\n"
            "!chat setconv : import converter file.(can chain 3 file)\n"
            "!chat conv : convert just before message\n"
            "!chat status : print channel status\n"
            "!chat exit : exit bot\n"
            "@mention : answer chats based on history.if you include a question, Bot answer a question.")

    def chat_listen(self):
        if self.listen:
            self.listen = False
            configIo.set_config(str(self.my_channel.id) + "listen", False)
        else:
            self.listen = True
            configIo.set_config(str(self.my_channel.id) + "listen", True)
        return self.my_channel.send("!setting listen = " + str(self.listen))

    def chat_convert_all(self):
        if self.use_converter_at_all:
            self.use_converter_at_all = False
        elif len(self.converter_status) > 0:
            self.use_converter_at_all = True
        else:
            return self.my_channel.send("!Error converter is None")
        return self.my_channel.send("!setting use_converter_at_all = " + str(self.use_converter_at_all))

    def set_temp(self, temp: float):
        self.chara_status.temp = temp
        return self.my_channel.send("!setting temp = " + str(self.chara_status.temp))

    async def history2message(self, limit=None):
        if limit is None:
            limit = self.chara_status.messages_preloaded
        self.message = []
        self.chat_history = \
            [message async for message in self.my_channel.history(limit=limit)]

        for chat in self.chat_history:
            if chat.content == "!split":
                break
            if chat.content.startswith("!setting character file"):
                break
            if chat.content.startswith("!"):
                continue
            elif chat.content.startswith("<@"):
                continue
            elif chat.author == self.my_user:
                self.message.append({"role": "assistant", "content": chat.content})
            elif chat.author.bot:
                continue
            else:
                if self.chara_status.send_user_name:
                    self.message.append({"role": "user", "content": chat.author.name + "「" + chat.content + "」"})
                else:
                    self.message.append({"role": "user", "content": chat.content})

            if num_tokens_from_messages(self.message) > self.chara_status.send_token:
                break

        self.message.reverse()
        if (len(self.message)) > 1:
            self.logger.info("read chat history : " + self.message[0]["content"] + " ~ " + self.message[-1]["content"])
        elif (len(self.message)) == 1:
            self.logger.info("read chat history : " + self.message[0]["content"])

    async def get_last_message(self):
        self.message = []
        self.chat_history = \
            [message async for message in self.my_channel.history(limit=50)]

        for chat in self.chat_history:
            if chat.content.startswith("!"):
                continue
            elif chat.content.startswith("<@"):
                continue
            elif chat.author == self.my_user:
                self.message.append({"role": "user", "content": chat.content})
                break
            elif chat.author.bot:
                continue
            else:
                self.message.append({"role": "user", "content": chat.content})
                break

        self.logger.info("read chat history : " + self.message[0]["content"])
