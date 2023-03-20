import coloredlogs
from dotenv import load_dotenv

import const
from discord_bot import discord_bot


def main():
    # import .env file
    load_dotenv(override=True)
    coloredlogs.install("INFO", fmt="%(asctime)s %(levelname)s     %(name)s %(message)s",
                        field_styles=const.DEFAULT_FIELD_STYLES(), level_styles=const.DEFAULT_LEVEL_STYLES())

    discord_bot()


if __name__ == "__main__":
    main()
