import discord
from discord.ext import tasks

class UndoButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="↶",
            style=discord.ButtonStyle.primary
        )
    
    async def callback(self, interaction):
        tweet_user = interaction.message.content.split("sent by: ", 1)[1]
        if str(interaction.user) != tweet_user:
            return

        reverted_content = interaction.message.content.replace('vxtwitter', 'twitter')
        # Do it a second time for instagram, won't trigger if it doesnt find instagram in the link
        

        reverted_content =  reverted_content.replace('ddinstagram', 'instagram')
        
        delete = DeleteButton()
        await interaction.message.edit(content=reverted_content, view=discord.ui.View(delete, timeout=None))
        
        self.disabled = True
        await interaction.response.defer()

class DeleteButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="❌",
            style=discord.ButtonStyle.danger
        )
    
    async def callback(self, interaction: discord.Interaction):
        tweet_user = interaction.message.content.split("sent by: ", 1)[1]
        if str(interaction.user) != tweet_user:
            return
        
        await interaction.message.delete()
        # await interaction.delete_original_message()


bot = discord.Bot(intents=discord.Intents.all())

def get_file_contents(file):
    return open(file).read()

@bot.listen()
async def on_message(message):
    # Checks if reply and if bot is author of referenced message, and that its not author replying
    # Purpose of this is to @ when replied to tweet/instagram post
   if message.reference is not None and not message.is_system():
        if (str(message.reference.resolved.author) == str(bot.user)):
            # Check if reply is actually setup to mention the user
            if not message.mentions:
                return
            author_str = message.reference.resolved.content.split("sent by: ", 1)[1]
            if author_str == str(message.author):
                return
            username = author_str.split("#")
            user = discord.utils.get(bot.users, name=username[0], discriminator=username[1])
            if user is None:
                return
            else:
                await message.channel.send(user.mention)
   # Replaces the link and deletes the message
   else:
        if (message.content.find('https://twitter') != -1) and (message.content.find('https://vxtwitter') == -1):
            reply_content = message.content.replace('twitter', 'vxtwitter') + " sent by: " + str(message.author)
            undo = UndoButton()
            delete = DeleteButton()
            reply_view = discord.ui.View(undo, delete, timeout=None)

            reply_message = await message.channel.send(content=reply_content, view=reply_view)
            await message.delete()
        # Normally would work without www, but instagram for some reason still uses www when copying in the browser
        if (message.content.find('https://www.instagram') != -1) and (message.content.find('https://ddinstagram') == -1):
            reply_content = message.content.replace('instagram', 'ddinstagram') + " sent by: " + str(message.author)
            undo = UndoButton()
            delete = DeleteButton()
            reply_view = discord.ui.View(undo, delete, timeout=None)

            reply_message = await message.channel.send(content=reply_content, view=reply_view)
            await message.delete()


if __name__ == "__main__":
    bot.run(get_file_contents("token.dat"))
