import discord
from chat_channel import chat_channel


def chat_help(params):
    return "help"


def decode_argument(arg_type, string):
    if type == "int":
        return int(string)
    if type == "float":
        return float(string)
    if type == "bool":
        return bool(string)
    return string


class decode_params:
    # commands = {command_name:detail_dict}
    # detail_dict = {function:function_name(can async),need_arguments:arguments_dict,optional_arguments:arguments_dict}
    # arguments_dict = {argument_name:type}
    def __init__(self, command_start, commands, mention, SPLIT_CHAR=False):
        self.command_start = command_start
        self.commands = commands
        self.mention = mention["mention"]
        self.mention_func = mention["function"]
        self.SPLIT_CHAR = SPLIT_CHAR


def decode_command(message, params):
    text = message.content
    command_start = params.command_start
    commands = params.commands
    SPLIT_CHAR = params.SPLIT_CHAR
    mention = params.mention
    mention_func = params.mention_func

    if text.startswith(mention):
        return {"command": True, "function": mention_func, "arguments": {"message": message}}

    # コマンド開始判定
    if text.startswith("!"):
        text = text.lstrip("!")

        # 受け取るべきコマンドかどうかの判定
        if text.startswith(command_start):
            text = text.lstrip(command_start).lstrip(" ")
            detail_dict = {}

            # コマンドの探索
            for command in commands:
                if text.startswith(command):
                    detail_dict = commands[command]
                    text = text.lstrip(command).lstrip(" ")
                    break
            else:
                # コマンドが存在しない
                return {"command": False, "text": "this command is not found"}

            # 引数の読み込み
            arguments_dict = {}

            # フラグの探索
            if "flags" in detail_dict:
                for flag in detail_dict["flags"]:
                    if text.startswith(flag):
                        arguments_dict[flag] = True
                        text = text.lstrip(flag).lstrip(" ")

            # 必須引数の読み込み
            if "need_arguments" in detail_dict:
                for arg in detail_dict["need_arguments"]:
                    text = text.lstrip(arg + "=").lstrip(arg + " =").lstrip(" ")
                    if SPLIT_CHAR == "\n":
                        tmp_texts = text.split("\n", maxsplit=1)
                    else:
                        tmp_texts = text.split(maxsplit=1)
                    arguments_dict[arg] = decode_argument(arg_type=detail_dict["need_arguments"][arg], string=tmp_texts[0])
                    if len(tmp_texts) > 1:
                        text = tmp_texts[1]
                    else:
                        text = ""

            return {"command": True, "function": detail_dict["function"], "arguments": arguments_dict}

        else:
            # コマンドは受け入れ対象ではない
            return {"command": False, "text": "this command is not for me"}
    else:
        # コマンドが見つからない
        return {"command": False, "text": "this is not command"}
