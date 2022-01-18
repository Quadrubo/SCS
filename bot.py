import datetime
import os

from discord.ext import commands
from dotenv import load_dotenv

import discord

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

guild_ids = [499222173177872403]
owner_ids = [303544964174970882]

bot = commands.Bot(intents=discord.Intents.all())


@bot.event
async def on_ready():
    write_log("INFO", "bot.py", "Bot is ready.", True)


@bot.event
async def on_application_command_error(ctx, error):
    await ctx.defer()
    if isinstance(error.original, discord.ExtensionNotFound):
        # write_log("WARNING", "bot.py", f"{ctx.author.name}#{ctx.author.discriminator} tried to use an extension (" + str(ctx.message.content).split(" ")[1] + ") that doesn't exist.", True)
        await ctx.respond(f"The Extension does not exist.")
        return
    if isinstance(error.original, discord.ExtensionNotLoaded):
        # write_log("WARNING", "bot.py", f"{ctx.author.name}#{ctx.author.discriminator} tried to use an extension (" + str(ctx.message.content).split(" ")[1] + ") that isn't loaded.", True)
        await ctx.respond("The specified extension is not loaded.")
        return
    if isinstance(error.original, discord.ExtensionAlreadyLoaded):
        # write_log("WARNING", "bot.py", f"{ctx.author.name}#{ctx.author.discriminator} tried to load an extension (" + str(ctx.message.content).split(" ")[1] + ") that is already loaded.", True)
        await ctx.respond(f"The specified extension is already loaded.")
        return

    raise error


@bot.slash_command(guild_ids=guild_ids, description="Load an extension.")
@discord.commands.option("extension", str, description="The extension you want to load.")
async def load(ctx, extension: str):
    if ctx.author.id in owner_ids:
        bot.load_extension(f'cogs.{extension}')
        write_log("INFO", "bot.py", f"Extension {extension} was successfully loaded by {ctx.author.name}#{ctx.author.discriminator}.", True)
        await ctx.respond(f"The extension {extension} was successfully loaded.")
    else:
        write_log("WARNING", "bot.py", f"{ctx.author.name}#{ctx.author.discriminator} tried to load the extension {extension}.", True)
        await ctx.respond("Sorry, you don't have the permission to do this :/")


@bot.slash_command(guild_ids=guild_ids, description="Unload an extension.")
@discord.commands.option("extension", str, description="The extension you want to unload.")
async def unload(ctx, extension: str):
    if ctx.author.id in owner_ids:
        bot.unload_extension(f'cogs.{extension}')
        write_log("INFO", "bot.py", f"Extension {extension} was successfully unloaded by {ctx.author.name}#{ctx.author.discriminator}.", True)
        await ctx.respond(f"The extension {extension} was successfully unloaded.")
    else:
        write_log("WARNING", "bot.py", f"{ctx.author.name}#{ctx.author.discriminator} tried to unload the extension {extension}.", True)
        await ctx.respond("Sorry, you don't have the permission to do this :/")


@bot.slash_command(guild_ids=guild_ids, description="Reload an extension.")
@discord.commands.option("extension", str, description="The extension you want to reload.")
async def reload(ctx, extension: str):
    if ctx.author.id in owner_ids:
        bot.unload_extension(f'cogs.{extension}')
        bot.load_extension(f'cogs.{extension}')
        write_log("INFO", "bot.py", f"Extension {extension} was successfully reloaded by {ctx.author.name}#{ctx.author.discriminator}.", True)
        await ctx.respond(f"The extension {extension} was successfully reloaded.")
    else:
        write_log("WARNING", "bot.py", f"{ctx.author.name}#{ctx.author.discriminator} tried to reload the extension {extension}.", True)
        await ctx.respond("Sorry, you don't have the permission to do this :/")


def twoiger(nbr):
    nbr = str(nbr)
    if len(nbr) == 1:
        return "0" + str(nbr)
    else:
        return str(nbr)


def write_log(type, module, text, console_output):
    now = datetime.datetime.now()

    timestamp = str(now.year) + "-" + twoiger(now.month) + "-" + twoiger(now.day) + " " \
                + twoiger(now.hour) + "-" + twoiger(now.minute) + "-" + twoiger(now.second)

    write = timestamp + " " + module + " " + type + ": " + text

    f = open(bot_log_dir_path, "a")
    f.write(write + "\n")
    f.close()

    if console_output:
        print(write)


# Start the Logging
path = os.getcwd()
logs_path = os.path.join(path, "logs")

if not os.path.isdir(logs_path):
    os.mkdir(logs_path)

now = datetime.datetime.now()

current_log_dir_name = str(now.year) + "-" + twoiger(now.month) + "-" + twoiger(now.day) + "_" \
                       + twoiger(now.hour) + "-" + twoiger(now.minute) + "-" + twoiger(now.second)
current_log_dir_path = os.path.join(logs_path, current_log_dir_name)

if not os.path.isdir(current_log_dir_path):
    os.mkdir(current_log_dir_path)

bot_log_file_name = "bot.log"
bot_log_dir_path = os.path.join(current_log_dir_path, bot_log_file_name)

f = open(bot_log_dir_path, "w")
f.close()

load_cogs = ["scs.py"]

for filename in os.listdir(os.path.join(os.path.dirname(__file__), 'cogs')):
    if filename in load_cogs:
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
            write_log("INFO", "bot.py", "Extension " + filename[:-3] + " was successfully loaded.", True)

bot.run(TOKEN)
