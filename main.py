from typing import Any, Union
import discord as d
from discord.ext import tasks

# TODO a few type ignores
# TODO embed view expiry

VX_TWITTER_BASE_URL = "https://vxtwitter.com/"
LINK_REPLACEMENTS = [
    ("https://twitter", "https://vxtwitter"),
    ("https://x", "https://vxtwitter"),
    ("https://instagram", "https://ddinstagram")
]


# Could be simplified
bot = d.Bot(intents=d.Intents.all())


class UndoButton(d.ui.Button):
    def __init__(self):
        super().__init__(
            label="↶",
            style=d.ButtonStyle.primary
        )
    
    async def callback(self, interaction):
        if not interaction.message:
            return
        
        original_poster = interaction.message.content.split("sent by: ", 1)[1]
        if str(interaction.user) != original_poster:
            return

        delete = DeleteButton()
        reverted_content = ""
        for replacement_pair in LINK_REPLACEMENTS:
            if replacement_pair[1] in interaction.message.content:
                reverted_content = interaction.message.content.replace(replacement_pair[1], replacement_pair[0])
                await interaction.message.edit(content=reverted_content, view=d.ui.View(delete, timeout=None))
                break
        
    
        
        self.disabled = True
        await interaction.response.defer() # TODO

class DeleteButton(d.ui.Button):
    def __init__(self):
        super().__init__(
            label="❌",
            style=d.ButtonStyle.danger
        )
    
    async def callback(self, interaction):
        if not interaction.message:
            return
        
        original_poster = interaction.message.content.split("sent by: ", 1)[1]
        if str(interaction.user) != original_poster:
            return
        
        await interaction.message.delete()



def get_file_contents(file):
    return open(file).read()

def reply_to_post(message: d.Message) -> bool:
    # Checks if it even is a reply
    if message.reference is None:
        return False
    
    # Checks for if it is a system message
    if message.is_system():
        return False

    # Checks if the original message is deleted
    reply_unknown: Union[None, d.DeletedReferencedMessage, d.Message] = message.reference.resolved
    if (not reply_unknown) or (reply_unknown is d.DeletedReferencedMessage):
        return False

    # Checks if user is in the server. "User" is reserved for users that are not in a Guild
    mentioned_user: Union[d.User, d.Member] = reply_unknown.author # type: ignore
    if mentioned_user is d.User:
        return False
    
    # Checks if the user replied to is the bot
    if str(mentioned_user) != str(bot.user):
        return False
    
    # Checks for a replaced link in the message, so that it actually is an embed
    not_found = True
    for replacement_pair in LINK_REPLACEMENTS:
        if replacement_pair[1] in reply_unknown.content: # type: ignore
            not_found = False
            break
    if not_found:
        return False
    
    return True

    
async def link_replace(message: d.Message) -> None:
    reply_content: str = ""
    for replacement_pair in LINK_REPLACEMENTS:
        if replacement_pair[0] in message.content:
            reply_content = message.content.replace(replacement_pair[0], replacement_pair[1]) + " sent by: " + str(message.author)
            break

    if reply_content == "":
        return

    undo = UndoButton()
    delete = DeleteButton()
    reply_view = d.ui.View(undo, delete, timeout=None)

    # await message.channel.send(content=reply_content, view=reply_view)
    print("triggered sending message")
    await message.delete()

@bot.listen()
async def on_message(message: d.Message):
    if reply_to_post(message):
        if not message.reference or (message.reference is d.DeletedReferencedMessage):
            return

        author_str = message.reference.resolved.content.split("sent by: ", 1)[1] # type: ignore
        user_tuple = (author_str.split("#")[0], author_str.split("#")[1])
        user = d.utils.get(bot.users, name=user_tuple[0], discriminator=user_tuple[1]) # type: ignore
        
        await message.channel.send(user.mention)
    

    await link_replace(message)


if __name__ == "__main__":
    bot.run(get_file_contents("token.dat"))
