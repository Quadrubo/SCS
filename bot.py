import os
from dotenv import load_dotenv

import discord

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

bot = discord.Bot()

@bot.event
async def on_ready():
    print("Hi")

@bot.slash_command()
async def hello(ctx, name: str = None):
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")

@bot.user_command(name="Say Hello")
async def hi(ctx, user):
    await ctx.respond(f"{ctx.author.mention} says hello to {user.name}!")

bot.run(TOKEN)