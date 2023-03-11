import asyncio
import ChatGPTAPI
import threading
import json
import make_charafile
from tiktoken_wrapper import num_tokens_from_messages


class character_status:
    def __init__(self, system_message, message, listen=True, temp=0.5):
        self.system_message = system_message
        self.message = message
        self.listen = listen
        self.temp = temp


def get_character_status(name):
    try:
        with open(name + ".json", mode="r", encoding="utf-8") as f:
            text = f.read()
            return json.loads(text)
    except:
        try:
            make_charafile.set_TARGET(name + ".txt")
            make_charafile.load_chara()
            try:
                with open(name + ".json", mode="r", encoding="utf-8") as f:
                    text = f.read()
                    return json.loads(text)
            except Exception as e:
                print("character file is not found")
                return e

        except Exception as e:
            print("character file is not found")
            return e


class chat_channel:

    def __init__(self, myuser, mychannel):
        self.system_message = [{"role": "system", "content": "あなたはみんなの友達です。"}]
        self.chara_name = "def"
        self.message = []
        self.listen = False
        self.temp = 0.5
        self.token = 500
        self.chat_history = []
        self.myuser = myuser
        self.mychannel = mychannel
        self.history_tokens = 800
        self.chat_padding = True
        self.use_history = True

    def character_init(self, name):
        try:
            status = get_character_status(name)
        except Exception as e:
            print(e)
            return self.mychannel.send("character file is not found")
        try:
            self.system_message = status["system_message"]
            self.temp = status["temp"]
            self.token = status["token"]
            self.history_tokens = status["history_tokens"]
            self.chara_name = name
            self.chat_padding = status["chat_padding"]
            self.use_history = status["use_history"]
            self.listen = True
            return self.mychannel.send("!import character file \"" + name + "\"")
        except Exception as e:
            print(e)
            return self.mychannel.send("!Error character file is broken")

    async def chat_answer(self):
        if not self.listen:
            return self.mychannel.send("!Error I can't read this channel.")
        await self.history2message()
        try:
            response = await ChatGPTAPI.call_api("gpt-3.5-turbo", self.system_message + self.message, self.temp,
                                                 self.token)
        except Exception as e:
            print(e)
            return self.mychannel.send("!Error API Call failed")
        if self.chat_padding:
            text = response["choices"][0]["message"]["content"].split("「", 1)[-1].rstrip("」")
        else:
            text = response["choices"][0]["message"]["content"]
        return self.mychannel.send(text)

    async def chat_mention(self, message):
        if message.content.replace(self.myuser.mention, "").lstrip() == "":
            return await self.chat_answer()

        try:
            response = await ChatGPTAPI.call_api(messages=[{"role": "system", "content": "あなたは役に立つアシスタントです。"},
                                                           {"role": "user",
                                                            "content": message.content.replace(self.myuser.mention,
                                                                                               "")}])
        except Exception as e:
            print(e)
            return self.mychannel.send("!Error API Call failed")
        print(response)
        return self.mychannel.send(message.author.mention + response["choices"][0]["message"]["content"])

    def chat_help(self):
        return self.mychannel.send(
            "!ChatGPT-API Discord Bot\n"
            "ver0.3 2023/03/10\n\n"
            "command list \n"
            "!chat a : answer chats based on history.\n"
            "!split : Bot can't read the message history prior to this command.\n"
            "!chat listen : Allow or not allow this channel to be read.\n"
            "!chat chara : import character file.\n"
            "@mention : answer chats based on history.if you include a question, Bot answer a question.")

    def chat_listen(self):
        if self.listen:
            self.listen = False
        else:
            self.listen = True
        return self.mychannel.send("!setting listen = " + str(self.listen))

    def set_temp(self, temp: float):
        self.temp = temp
        return self.mychannel.send("!setting temp = " + str(self.temp))

    async def history2message(self):
        self.message = []
        if self.use_history:
            read_limit = 200
        else:
            read_limit = 2
        self.chat_history = [message async for message in self.mychannel.history(limit=read_limit)]
        for chat in self.chat_history:
            if chat.content == "!split":
                break
            if chat.content.startswith("!"):
                continue
            elif chat.content.startswith("<@"):
                continue
            elif chat.author == self.myuser:
                self.message.append({"role": "assistant", "content": chat.content})
            elif chat.author.bot:
                continue
            else:
                if self.chat_padding:
                    self.message.append({"role": "user", "content": chat.author.name + "「" + chat.content + "」"})
                else:
                    self.message.append({"role": "user", "content": chat.content})

            try:
                len_over = num_tokens_from_messages(self.message) > self.history_tokens
            except Exception as e:
                print(e)
                text_len = 0
                for text in self.message:
                    text_len += len(text["content"]) + len(text["role"])
                    len_over = text_len > self.history_tokens
            if len_over:
                break

        self.message.reverse()
        if (len(self.message)) > 0:
            print("read chat history")
            print(self.message[0])
            print(self.message[-1])
