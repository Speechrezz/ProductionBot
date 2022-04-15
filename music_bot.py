import discord
import numpy as np
import helper
from pydub import AudioSegment
import database
import io

# https://discord.com/api/oauth2/authorize?client_id=959708215627612162&permissions=274877918272&scope=bot

# Make our own client class
class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        # Call parent's init
        super().__init__(*args, **kwargs)
        self.colors = np.array(((0.95294118, 0.48235294, 0.40784314),  # salmon/orange
                                (0.60784314, 0.51764706, 0.9254902),   # indigo/purple
                                (0.03529412, 0.69019608, 0.94901961))) # blue
        self.token: str = None
        self.settingsDB = database.Database("MusicBotServers")
        defs = {"active_channels": [], 
                "command_prefix": '!'}
        self.settingsDB.set_defaults(defs)
        self.colorIdxs = {}

    def load_token(self, fname = "token.txt"):
        with open(fname, 'r') as f:
            self.token = f.readline()

    def run(self):
        super().run(self.token)

    def get_next_color(self, guild: int):
        if guild in self.colorIdxs:
            idx = self.colorIdxs[guild]
            color = self.colors[idx]
            idx += 1
            idx = idx % self.colors.shape[0]
            self.colorIdxs[guild] = idx
        else:
            color = self.colors[0]
            self.colorIdxs[guild] = 1
        return color

    async def on_ready(self):
        # Populates database if guild does not exist in it yet
        for guild in self.guilds:
            print(guild.name)
            if not self.settingsDB.exists_id(guild.id):
                self.settingsDB.create_id(guild.id)

        print("Bot has started")

    async def on_raw_reaction_add(self, payload):
        
        # Guild is the discord server
        guild = client.get_guild(payload.guild_id)

        # TODO: Count the number of updoots

        #print(payload.emoji.name)

    async def on_raw_reaction_remove(self, payload):
        
        # Guild is the discord server
        guild = client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        # TODO: Subtract number of updoots

        #print(payload.emoji.name)

    async def on_guild_join(self, guild):
        if not self.settingsDB.exists_id(guild.id):
            self.settingsDB.create_id(guild.id)
    
    async def on_guild_remove(self, guild):
        if self.settingsDB.exists_id(guild.id):
            self.settingsDB.delete_id(guild.id)

    def on_command(self, message):
        guild_id = message.guild.id
        cmd = message.content[1:].split(" ")
        if cmd[0] == "prefix":
            if len(cmd) >= 2:
                if len(cmd[1]) == 1:
                    print(f"Prefix: {cmd[1]}")
                    self.settingsDB.update_id(guild_id, {"command_prefix": cmd[1]})
                    return f"Command prefixed updated to `{cmd[1]}`"
                return "Command prefix must be a single character"
        
        if cmd[0] == "add_channel":
            if len(cmd) >= 2:
                cur_channels = self.settingsDB.read_id_key(guild_id, "active_channels").copy()

                # If channel already exists in list
                if cmd[1] in cur_channels:
                    return f"Channel `{cmd[1]}` already exists in channels list"
                
                cur_channels.append(cmd[1])
                self.settingsDB.update_id(guild_id, {"active_channels": cur_channels})
                return f"Channel `{cmd[1]}` added to active channels list"

        if cmd[0] == "remove_channel":
            if len(cmd) >= 2:
                cur_channels = self.settingsDB.read_id_key(guild_id, "active_channels").copy()

                # If channel already exists in list
                if not cmd[1] in cur_channels:
                    return f"Channel `{cmd[1]}` does not exist in channels list"
                
                cur_channels.remove(cmd[1])
                self.settingsDB.update_id(guild_id, {"active_channels": cur_channels})
                return f"Channel `{cmd[1]}` removed from active channels list"

        if cmd[0] == "list_channels":
            cur_channels = self.settingsDB.read_id_key(guild_id, "active_channels")
            if len(cur_channels) == 0:
                return "All channels are active"
            return "List of active channels: `" + ", ".join(cur_channels) + "`"

        if cmd[0] == "reset":
            self.settingsDB.reset_id(guild_id)
            return "Production bot settings have been reset"

        if cmd[0] == "help":
            return "Help command: `prefix, add_channel, remove_channel, list_channels, reset`"

        else:
            return "Unknown command"

    async def on_message(self, message):
        # Checks if message came from the bot itself
        if message.author == client.user:
            return
        
        # Checks for command
        if len(message.content) >= 2:
            prefix = self.settingsDB.read_id_key(message.guild.id, "command_prefix")
            if message.content[0] == prefix:
                await message.reply(self.on_command(message), mention_author=False)

        # Checks if user sent a music file
        if len(message.attachments) >= 1:
            if "audio" in message.attachments[0].content_type:
                active_channels = self.settingsDB.read_id_key(message.guild.id, "active_channels")
                if any(ext in message.channel.name for ext in active_channels) or len(active_channels) == 0:
                    await self.music_file_sent(message)
                
    async def music_file_sent(self, message):
        guild = message.guild.id

        # Initialize IO
        data_stream = io.BytesIO()

        # React to the file
        await message.add_reaction("\U0001F525")

        # Read the file
        data = await message.attachments[0].read()
        ext = message.attachments[0].filename.split(".")[-1]
        song = AudioSegment.from_file(io.BytesIO(data), format=ext)

        # Send message
        y = helper.generate_waveform(song, data_stream, self.get_next_color(guild))
        chart = discord.File(data_stream, filename="music-analysis.png")
        await message.reply(helper.get_loudness_str(song.frame_rate, y), file = chart, mention_author = False)

    def getNextColor(self):
        color = self.colours[self.colourIdx]
        self.colourIdx += 1
        self.colourIdx = self.colourIdx % self.colours.shape[0]
        return color
        


# Setup intents (what our discord bot wants to do)
intents = discord.Intents.default()
intents.guilds = True

# This client is our connection to discord
client = MyClient(intents=intents)
client.load_token()
client.run()