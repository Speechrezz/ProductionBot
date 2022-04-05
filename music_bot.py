import discord
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import ticker
from pydub import AudioSegment
import io
import time

# https://discord.com/api/oauth2/authorize?client_id=959708215627612162&permissions=274877918272&scope=bot

# Make our own client class
class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        # Call parent's init
        super().__init__(*args, **kwargs)
        self.music_channel_names = ["sample", "production", "feedback"]
        self.colours = np.array(((0.95294118, 0.48235294, 0.40784314), (0.60784314, 0.51764706, 0.9254902), (0.03529412, 0.69019608, 0.94901961)))
        self.colourIdx: int = 0
        self.token: str = None

    def load_token(self, fname = "token.txt"):
        with open(fname, 'r') as f:
            self.token = f.readline()

    def run(self):
        super().run(self.token)

    async def on_ready(self):
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

    async def on_message(self, message):
        # Checks if message came from the bot itself
        if message.author == client.user:
            return
        if not any(ext in message.channel.name for ext in self.music_channel_names):
            return

        # Checks if user sent a music file
        if len(message.attachments) >= 1:
            if "audio" in message.attachments[0].content_type:
                await self.music_file_sent(message)
                
    async def music_file_sent(self, message):
        # Initialize IO
        data_stream = io.BytesIO()

        # React to the file
        await message.add_reaction("\U0001F525")

        # Read the file
        data = await message.attachments[0].read()
        ext = message.attachments[0].filename.split(".")[-1]
        song = AudioSegment.from_file(io.BytesIO(data), format=ext)
        y = np.array(song.get_array_of_samples())
        if song.channels >= 2:
            y = y.reshape((-1, song.channels))
        
        # Generate graph
        amp = np.zeros(y.shape[0])
        for i in range(y.shape[1]):
            amp += y[:, i]
        amp = amp / y.shape[1]
        plt.figure(figsize=(8,3), facecolor=(0.21176471, 0.22352941, 0.24313725))
        plt.rcParams['xtick.color'] = "white" #(0.6, 0.66666667, 0.70980392)
        plt.plot(np.linspace(0, y.shape[0] / song.frame_rate, y.shape[0]), amp, color = self.getNextColor())
        ax = plt.gca()
        ax.get_yaxis().set_visible(False)
        ax.set_facecolor((0.21176471, 0.22352941, 0.24313725))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        formatter = ticker.FuncFormatter(lambda s, x: time.strftime('%M:%S', time.gmtime(s)))
        ax.xaxis.set_major_formatter(formatter)

        # Save content into the data stream
        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
        plt.close()
        data_stream.seek(0)
        chart = discord.File(data_stream, filename="music-analysis.png")

        # Send message
        await message.reply(file = chart, mention_author = False)

    def getNextColor(self):
        color = self.colours[self.colourIdx]
        self.colourIdx += 1
        self.colourIdx = self.colourIdx % self.colours.shape[0]
        return color
        
        

# Setup intents (what our discord bot wants to do)
intents = discord.Intents.default()
intents.members = True

# This client is our connection to discord
client = MyClient(intents=intents)
client.load_token()
client.run()