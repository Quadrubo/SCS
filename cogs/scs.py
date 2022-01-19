import datetime
import os
import re

import discord
from discord.commands import slash_command
from discord.ext import commands, pages, tasks
from discord.ext.commands import has_permissions

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
        self.check_last_point_change.start()
        self.check_voice_channels.start()

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

        self.database.create_message(message.author.id, message.id)

        db_member = self.database.get_member(message.author.id)
        if db_member is None:
            self.database.create_member(message.author.id)
            db_member = self.database.get_member(message.author.id)

        current_score = db_member[1]

        rows = self.database.get_messages_from_today(message.author.id)
        if len(rows) <= 10:
            if current_score < 0:
                add_amount = 7500
            else:
                add_amount = 15000
            new_score = current_score + add_amount
            self.database.set_score(message.author.id, new_score)
            self.database.set_last_gained(message.author.id)
            self.database.set_punished(message.author.id, 0)

        await self.bot.process_commands(message)

    """
    # UNUSED
    def number_to_emoji(self, number):
        number_str = str(number)
        return_str = ''
        for number_char in number_str:
            if number_char == '0':
                return_str += ':zero:'
            elif number_char == '1':
                return_str += ':one:'
            elif number_char == '2':
                return_str += ':two:'
            elif number_char == '3':
                return_str += ':three:'
            elif number_char == '4':
                return_str += ':four:'
            elif number_char == '5':
                return_str += ':five:'
            elif number_char == '6':
                return_str += ':six:'
            elif number_char == '7':
                return_str += ':seven:'
            elif number_char == '8':
                return_str += ':eight:'
            elif number_char == '9':
                return_str += ':nine:'

        return return_str
    """

    def format_number(self, n):
        return re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', str(n))

    @tasks.loop(hours=24)
    async def check_last_point_change(self):
        print("Checking last point change for all members...")
        for guild in self.bot.guilds:
            for member in enumerate(guild.members):
                print(member[0])
                member = member[1]
                db_member = self.database.get_member(member.id)
                if db_member is None:
                    self.database.create_member(member.id)
                    db_member = self.database.get_member(member.id)

                current_score = db_member[1]

                if self.database.check_inactive(member.id):
                    print(db_member[3])
                    if not db_member[3]:
                        new_score = current_score - 350000
                    else:
                        new_score = current_score - 200000

                    self.database.set_score(member.id, new_score)
                    self.database.set_punished(member.id, 1)

        print("Finished")

    @tasks.loop(minutes=1)
    async def check_voice_channels(self):
        print("Checking voice channels...")
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if type(channel) is discord.channel.VoiceChannel:
                    for member in channel.members:
                        db_member = self.database.get_member(member.id)
                        if db_member is None:
                            self.database.create_member(member.id)
                            db_member = self.database.get_member(member.id)

                        current_score = db_member[1]

                        if current_score < 0:
                            add_amount = 1500
                        else:
                            add_amount = 3000

                        new_score = current_score + add_amount

                        self.database.set_score(member.id, new_score)
                        self.database.set_last_gained(member.id)
                        self.database.set_punished(member.id, 0)
        print("Finished")

    @slash_command(guild_ids=guild_ids, description="Shows the social credit score of a person.")
    @discord.commands.option("member", discord.Member, description="The person you want to see the social credit score of.")
    async def show(self, ctx, member: discord.Member):
        db_member = self.database.get_member(member.id)
        if db_member is None:
            self.database.create_member(member.id)
            db_member = self.database.get_member(member.id)

        current_score = db_member[1]

        await ctx.respond(embed=self.get_embed(title=f"The social credit score of {member.name}#{member.discriminator} is {self.format_number(current_score)}.", type="info"))

    @slash_command(guild_ids=guild_ids, description="Sets the social credit score of a person.")
    @discord.commands.option("member", discord.Member, description="The person you want to set the social credit score of.")
    @discord.commands.option("amount", int, description="The amount of social credit score you want the person to have.")
    @discord.commands.option("reason", str, description="The reason of the social credit score change.", required=False)
    @has_permissions(administrator=True)
    async def set(self, ctx, member: discord.Member, amount: int, reason: str):

        if self.database.get_member(member.id) is None:
            self.database.create_member(member.id)

        self.database.set_score(member.id, amount)

        await ctx.respond(embed=self.get_embed(
            title=f"Set the social credit score of {member.name}#{member.discriminator} to {self.format_number(amount)}.",
            description=f"The social credit score of {member.mention} is now at {self.format_number(amount)}", type="info"))

    @slash_command(guild_ids=guild_ids, description="Collect your daily social credit score.")
    async def daily(self, ctx):
        print(ctx.author.mention)

        db_member = self.database.get_member(ctx.author.id)
        if db_member is None:
            self.database.create_member(ctx.author.id)
            db_member = self.database.get_member(ctx.author.id)

        current_score = db_member[1]

        if not self.database.collected_daily(ctx.author.id):
            if current_score < 0:
                add_amount = 75000
            else:
                add_amount = 150000
            new_score = current_score + add_amount
            self.database.set_score(ctx.author.id, new_score)
            self.database.set_daily(ctx.author.id)
            self.database.set_last_gained(ctx.author.id)
            self.database.set_punished(ctx.author.id, 0)

            await ctx.respond(embed=self.get_embed(title=f"You collected your daily bonus of 150.000.", description=f"Your social credit score is now at {self.format_number(new_score)}", type="info"))
        else:
            await ctx.respond(embed=self.get_embed(title=f"You already collected your daily bonus for today.", type="info"))

    @slash_command(guild_ids=guild_ids, description="Removes social credit score from a person.")
    @discord.commands.option("member", discord.Member, description="The person you want to remove social credit score from.")
    @discord.commands.option("amount", int, description="The amount of social credit score you want to remove from the person.")
    @discord.commands.option("reason", str, description="The reason of the social credit score reduction.", required=False)
    @has_permissions(administrator=True)
    async def remove(self, ctx, member: discord.Member, amount: int, reason: str):
        db_member = self.database.get_member(member.id)
        if db_member is None:
            self.database.create_member(member.id)
            db_member = self.database.get_member(member.id)

        current_score = db_member[1]
        new_score = current_score - amount

        self.database.set_score(member.id, new_score)

        await ctx.respond(embed=self.get_embed(
            title=f"Removed {self.format_number(amount)} from the social credit score of {member.name}#{member.discriminator}.",
            description=f"The social credit score of {member.mention} is now at {self.format_number(new_score)}", type="info"))

    @slash_command(guild_ids=guild_ids, description="Gives a person social credit score.")
    @discord.commands.option("member", discord.Member, description="The person you want to give social credit score to.")
    @discord.commands.option("amount", int, description="The amount of social credit score you want to give to the person.")
    @discord.commands.option("reason", str, description="The reason of the social credit score addition.", required=False)
    @has_permissions(administrator=True)
    async def give(self, ctx, member: discord.Member, amount: int, reason: str):
        db_member = self.database.get_member(member.id)
        if db_member is None:
            self.database.create_member(member.id)
            db_member = self.database.get_member(member.id)

        current_score = db_member[1]
        new_score = current_score + amount

        self.database.set_score(member.id, new_score)

        await ctx.respond(embed=self.get_embed(title=f"Added {self.format_number(amount)} to the social credit score of {member.name}#{member.discriminator}.", description=f"The social credit score of {member.mention} is now at {self.format_number(new_score)}", type="info"))

    @slash_command(guild_ids=guild_ids, description="Shows the leaderboard.")
    async def leaderboard(self, ctx):

        rows = self.database.get_scores()

        leaderboard_pages = []

        def get_medal(number):
            if number == 1:
                return ':first_place:'
            elif number == 2:
                return ':second_place:'
            elif number == 3:
                return ':third_place:'
            return number

        page_counter = 1
        entry_counter = 1
        all_counter = 1
        leaderboard_page = self.get_embed(title=f'Leaderboard | Page {page_counter}')
        leaderboard_page.description = ''
        for row in rows:
            member = self.get_member_by_id(row[0])
            leaderboard_page.description += f"{get_medal(all_counter)} | {self.format_number(row[1])} | {member.mention}\n"
            if entry_counter >= 15:
                page_counter += 1
                leaderboard_pages.append(leaderboard_page)
                leaderboard_page = self.get_embed(title=f'Leaderboard | Page {page_counter}')
                leaderboard_page.description = ''
                entry_counter = 1
            else:
                entry_counter += 1
            all_counter += 1
        if entry_counter != 1:
            leaderboard_pages.append(leaderboard_page)

        paginator = pages.Paginator(pages=leaderboard_pages)

        await paginator.respond(ctx.interaction, ephemeral=False)

    @slash_command(guild_ids=guild_ids, description="Deletes messages.")
    @discord.commands.option("amount", int, description="The amount of messages you want to delete.")
    @discord.commands.option("channel", discord.TextChannel, description="The channel in which you want to delete the messages.", required=False)
    @has_permissions(administrator=True)
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
