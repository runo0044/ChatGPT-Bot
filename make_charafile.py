import json

file_text = []
line_no = 0
TARGET = "girl1.txt"


def set_TARGET(s: str):
    global TARGET
    TARGET = s


def input_from_txt(text):
    global file_text
    global line_no
    if not file_text:
        with open(TARGET, mode="r", encoding="utf-8") as f:
            file_text_str = f.read()
        file_text = file_text_str.split("\n")
    return_text = file_text[line_no]
    line_no += 1
    print("import " + text + return_text)
    return return_text


def load_chara():
    text = "<chara_name>様.AI assistants can only output as <chara_name> from now on. " \
           "<chara_name> is <chara_age> years old <chara_type>. " \
           "<chara_name>'s first person is <chara_first_person> and her second person is <chara_second_person> . " \
           "Here are some examples of <chara_name>'s output.\n" \
           "<examples>" \
           "AI assistants can only output as <chara_name> from now on."
    file_name = input_from_txt("file_name:")
    chara_name = input_from_txt("chara_name:")
    chara_type = input_from_txt("chara_type:")
    chara_age = input_from_txt("chara_age:")
    chara_first_person = input_from_txt("chara_first_person:")
    chara_second_person = input_from_txt("chara_second_person:")
    text = text.replace("<chara_name>", chara_name).replace("<chara_type>", chara_type). \
        replace("<chara_age>", chara_age).replace("<chara_first_person>", chara_first_person). \
        replace("<chara_second_person>", chara_second_person)

    chara_output_examples = []
    while True:
        example = input_from_txt("chara_output_examples")
        if example == "exit":
            break
        chara_output_examples.append(example)
    temp = ""
    for i in chara_output_examples:
        temp += chara_name + "「" + i + "」\n"

    text = text.replace("<examples>", temp)

    json_file = {"system_message": [{"role": "system", "content": "AI assistants can only output as " +
                                                                  chara_name + " from now on."},
                                    {"role": "user", "content": text}],
                 "temp": 0.5,
                 "token": 1000,
                 "history_tokens": 1000,
                 "chat_padding": True,
                 "use_history": True
                 }

    with open(file_name + ".json", mode="w", encoding="utf-8", newline='\n') as f:
        f.write(json.dumps(json_file, ensure_ascii=False))


if __name__ == "__main__":
    load_chara()
