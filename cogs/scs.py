import datetime
import os

from discord.ext import commands


class Uno(commands.Cog):
    def __init__(self, bot):
        # self.relative_path = "/home/jubuntu/Quadbot"
        self.relative_path = "./"
        self.bot = bot
        self.prefix = "*"
        self.bot_log_file = os.path.join(self.get_log_dir(), "uno.log")
        self.uno_game_counter = 0
        self.uno_games = {}
        self.uno_cards = ["r0", "r1", "r1", "r2", "r2", "r3", "r3", "r4", "r4", "r5", "r5", "r6", "r6", "r7", "r7", "r8", "r8", "r9", "r9", "r+2", "r+2", "rreverse", "rreverse", "rskip", "rskip",
                          "y0", "y1", "y1", "y2", "y2", "y3", "y3", "y4", "y4", "y5", "y5", "y6", "y6", "y7", "y7", "y8", "y8", "y9", "y9", "y+2", "y+2", "yreverse", "yreverse", "yskip", "yskip",
                          "g0", "g1", "g1", "g2", "g2", "g3", "g3", "g4", "g4", "g5", "g5", "g6", "g6", "g7", "g7", "g8", "g8", "g9", "g9", "g+2", "g+2", "greverse", "greverse", "gskip", "gskip",
                          "b0", "b1", "b1", "b2", "b2", "b3", "b3", "b4", "b4", "b5", "b5", "b6", "b6", "b7", "b7", "b8", "b8", "b9", "b9", "b+2", "b+2", "breverse", "rreverse", "bskip", "bskip",
                          "cchoose", "cchoose", "cchoose", "cchoose", "c+4", "c+4", "c+4", "c+4"]

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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        await self.bot.process_commands(message)

    def get_member_by_id(self, member_id):
        guild = ""
        for guild in self.bot.guilds:
            for member in guild.members:
                if str(member.id) == str(member_id):
                    return member


def setup(bot):
    bot.add_cog(Uno(bot))
