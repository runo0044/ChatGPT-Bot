import json


def get_config(config_key: str):
    try:
        with open("config.json", mode="r", encoding="utf-8") as f:
            config = json.loads(f.read())
            if str(config_key) in config.keys():
                return config[config_key]
            else:
                return None
    except Exception as e:
        print(e)
        return None


def set_config(config_key: str, value):
    try:
        with open("config.json", mode="r", encoding="utf-8") as f:
            config = json.loads(f.read())
    except Exception as e:
        print(e)
        config = {}

    config[config_key] = value
    tmp = json.dumps(config)
    with open("config.json", mode="w", encoding="utf-8") as f:
        f.write(tmp)
