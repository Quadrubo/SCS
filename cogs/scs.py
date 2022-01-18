import datetime
import os

import discord
from discord.commands import slash_command
from discord.ext import commands

from database import Database

guild_ids = [499222173177872403]
owner_ids = [303544964174970882]

class Scs(commands.Cog):
    def __init__(self, bot):
        # self.relative_path = "/home/jubuntu/Quadbot"
        self.relative_path = "./"
        self.bot = bot
        self.database = Database(db_folder_path='db', db_file_name='scs.db')
        self.bot_log_file = os.path.join(self.get_log_dir(), "scs.log")

    def get_embed(self, title, description=None, type=None):
        if type == "info":
            embed = discord.Embed(title=title, description=description, color=discord.Color.og_blurple())
        elif type == "success":
            embed = discord.Embed(title=title, description=description, color=discord.Color.green())
        elif type == "warning":
            embed = discord.Embed(title=title, description=description, color=discord.Color.orange())
        elif type == "error":
            embed = discord.Embed(title=title, description=description, color=discord.Color.red())
        else:
            embed = discord.Embed(title=title, description=description)

        return embed

    def get_log_dir(self):
        current_folder_name = []

        for folder in os.listdir(os.path.join(os.getcwd(), "logs")):
            if os.path.isdir(os.path.join(os.path.join(os.getcwd(), "logs"), folder)):
                folder_tstamp = str(folder).split("_")
                folder_date = str(folder_tstamp[0]).split("-")
                folder_time = str(folder_tstamp[1]).split("-")
                folder_tstamp = datetime.datetime(int(folder_date[0]), int(folder_date[1]), int(folder_date[2]),
                                                  int(folder_time[0]), int(folder_time[1]), int(folder_time[2]))
                if not current_folder_name or current_folder_name[1] < folder_tstamp:
                    current_folder_name = [folder, folder_tstamp]

        return os.path.join(os.path.join(os.getcwd(), "logs"), current_folder_name[0])

    def twoiger(self, nbr):
        nbr = str(nbr)
        if len(nbr) == 1:
            return "0" + str(nbr)
        else:
            return str(nbr)

    def write_log(self, type, module, text, console_output):
        now = datetime.datetime.now()

        timestamp = str(now.year) + "-" + self.twoiger(now.month) + "-" + self.twoiger(now.day) + " " \
            + self.twoiger(now.hour) + "-" + self.twoiger(now.minute) + "-" + self.twoiger(now.second)

        write = timestamp + " " + module + " " + type + ": " + text

        f = open(self.bot_log_file, "a")
        f.write(write + "\n")
        f.close()

        if console_output:
            print(write)

    @commands.Cog.listener()
    async def on_ready(self):
        self.write_log("INFO", "scs.py", "Cog SCS is ready.", True)
        self.check_members()

    def check_members(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                if self.database.get_member(member.id) is None:
                    self.database.create_member(member.id)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        print(message)

        await self.bot.process_commands(message)

    @slash_command(guild_ids=guild_ids, description="Deletes messages.")
    @discord.commands.option("amount", int, description="The amount of messages you want to delete.")
    @discord.commands.option("channel", discord.TextChannel, description="The channel in which you want to delete the messages.", required=False)
    async def purge(self, ctx, amount: int, channel: discord.TextChannel):
        if channel is None:
            channel = ctx.channel

        deleted = await channel.purge(limit=amount)

        await ctx.respond(embed=self.get_embed(title=f'Deleted {len(deleted)} message(s)', type="success"))

    def get_member_by_id(self, member_id):
        guild = ""
        for guild in self.bot.guilds:
            for member in guild.members:
                if str(member.id) == str(member_id):
                    return member


def setup(bot):
    bot.add_cog(Scs(bot))
