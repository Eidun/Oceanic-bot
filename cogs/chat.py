from discord.ext import commands
import utils.emoji_data as emoji


class ChatCog:
    chats = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(pass_context=True, hidden=True)
    async def crear_chat(self, ctx):
        """Crea un nuevo chat privado."""
        user = ctx.message.author
        receiver = await emoji.get_receiver(self.bot, user)
        print(receiver)


def setup(bot):
    bot.add_cog(ChatCog(bot))
