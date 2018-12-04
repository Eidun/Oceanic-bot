import discord
from discord.ext import commands
import utils.emoji_data as emoji

class AnunciosCog:
    channels = {}

    default_channel = '258295391391449088'
    bernar_id = '194087774922604545'

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.load_channels()

    def load_channels(self):
        for channel in self.bot.get_all_channels():
            self.channels[channel.id] = channel

    @commands.command(pass_context=True, hidden=True)
    async def load(self, ctx):
        self.load_channels()

    @commands.command(pass_context=True, hidden=True)
    async def set_default(self, ctx, channel_id):
        self.default_channel = channel_id
        print(self.default_channel)

    @commands.command(pass_context=True)
    async def anuncio(self, ctx, channel=None):
        """Comienza el anuncio. La configuración después"""
        # Get the author
        user = ctx.message.author
        # Obtener canal destinatario
        if (channel is None):
            channel = self.default_channel
        try:
            send_channel = self.channels[channel]
        except:
            await self.bot.send_message(user, 'No se ha podido encontrar el canal destinatario')
            return
        # Mensaje a enviar
        mensaje_final = await self.construir(user)

        # Envío del mensaje
        try:
            await self.bot.send_message(send_channel, mensaje_final)
        except:
            await self.bot.send_message(user, 'No se ha podido enviar el comunicado al canal seleccionado')

    @commands.command(pass_context=True)
    async def anuncio_privado(self, ctx):
        """Comienza el anuncio privado. La configuración después"""
        # Get the author
        user = ctx.message.author
        # Obtener destinatario
        receiver = await emoji.get_receiver(self.bot, user)
        if receiver is None:
            await self.bot.send_message(user, 'No ha elegido un destinatario para el comunicado')
            return

        # Mensaje a enviar
        mensaje_final = await self.construir(user)
        # Envío del mensaje
        try:
            await self.bot.send_message(receiver, mensaje_final)
        except:
            await self.bot.send_message(user, 'No se ha podido enviar el comunicado al canal seleccionado')

    async def construir(self, user):
        # Solo desde los mensajes privados
        def private_channel(message):
            return message.channel.type == discord.ChannelType.private

        # Mensaje a anunciar
        msg: discord.Message = await self.bot.send_message(user, 'Escriba el anuncio que desea comunicar:')
        anuncio: discord.Message = await self.bot.wait_for_message(timeout=50, author=user, check=private_channel)
        if anuncio is None:
            return
        # Firma del anunciante
        msg: discord.Message = await self.bot.send_message(user, 'Recibido. ¿Desea añadir una firma?')
        await self.bot.add_reaction(msg, u"\u2705")
        await self.bot.add_reaction(msg, u"\u274E")

        # Solo uno de los dos emojis que se esperan
        def allowed_reaction(reaction, user):
            return (reaction.emoji == u"\u2705") or (reaction.emoji == u"\u274E")

        # Emoji respuesta
        response = await self.bot.wait_for_reaction(timeout=30, user=user, message=msg, check=allowed_reaction)

        # Añadir firma
        firma = 'Anónimo'
        if (response is None or response.reaction.emoji == u"\u274E"):
            await self.bot.send_message(user, 'Muy bien, será anónimo. En unos instantes se hará el comunicado.')
        else:
            await self.bot.send_message(user, 'Perfecto. ¿Qué nombre debería figurar?')
            firma: discord.Message = await self.bot.wait_for_message(timeout=50, author=user, check=private_channel)
            if firma is not None:
                firma = firma.content
            await self.bot.send_message(user, f'Muy bien, {firma}. En unos instantes se hará el comunicado.')

        # Construir mensaje respuesta
        mensaje_final = f'```ini\n\n[{firma}]\n{anuncio.content}\n```'
        return mensaje_final


def setup(bot):
    bot.add_cog(AnunciosCog(bot))
