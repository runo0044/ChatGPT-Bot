from discord_bot import discord_bot
from dotenv import load_dotenv


def main():
    load_dotenv(override=True)
    discord_bot()


if __name__ == "__main__":
    main()
