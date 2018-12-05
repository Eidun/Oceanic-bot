import discord
import requests
from discord.ext import commands

import utils.emoji_data as emoji
from models.chat_model import chat_room


class ChatCog:
    bernar_id = '194087774922604545'
    server_id = '258295391391449088'

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def crear_chat(self, ctx):
        """Crea un nuevo chat privado."""
        user = ctx.message.author
        # Checks if user is already chatting
        if chat_room.is_chatting(user):
            await self.bot.send_message(user, 'Usted solo puede mantener una conversación '
                                              'bajo nuestra privacidad al mismo tiempo.')
            return
        await self.bot.send_message(user, 'Bienvenido a nuestros servicios de chat privado')
        # Select receiver for chatting
        receiver = await emoji.get_receiver(self.bot, user)
        if receiver is None:
            await self.bot.send_message(user, 'No ha seleccionado un destinatario, interrumpimos la operación')
            return
        # Adds master to chat
        master = self.bot.get_server(self.server_id).get_member(self.bernar_id)

        if chat_room.is_chatting(receiver) or chat_room.is_chatting(master):
            await self.bot.send_message(user, 'Lamentamos informarle que esa persona se encuentra involucrada en '
                                              'OTRA maldad ahora mismo. Increíble, ¿verdad?')
            return

        # Only private messages for privacy
        def private_channel(message):
            return message.channel.type == discord.ChannelType.private

        # Creator chooses alias
        await self.bot.send_message(user,
                                    'Es importante que elija un alias en conversación privada. ¿Cuál debería ser?')
        creator_alias = await self.bot.wait_for_message(timeout=50, author=user, check=private_channel)
        if creator_alias is None:
            await self.bot.send_message(user, 'Lo lamentamos, pero debe usted proporcionarnos algún alias. '
                                              'Se interrumpe la operación')
            return
        await self.bot.send_message(user, f'Muy bien, {creator_alias.content}.')
        # Receiver alias
        await self.bot.send_message(user, 'Usted ya conoce a su destinatario, claro... Pero nosotros no. '
                                          '¿De qué forma debemos dirigirnos a esa persona?')
        receiver_alias = await self.bot.wait_for_message(timeout=50, author=user, check=private_channel)
        if receiver_alias is None:
            await self.bot.send_message(user, 'Lo lamentamos, pero debe usted proporcionarnos algún alias. '
                                              'Se interrumpe la operación')
            return
        await self.bot.send_message(user, f'Muy bien, {creator_alias.content}. Haremos llegar a '
                                          f'{receiver_alias.content} sus deseos por hablar. Si acepta, entrarán ustedes'
                                          f' en un chat privado.')

        # Receivers accepts of rejects the chat
        proposal = await self.bot.send_message(receiver, f'Cordiales saludos, {receiver_alias.content}. El Oceanic le '
                                                         f'hace saber que hay una persona muy interesada en mantener '
                                                         f'una conversación privada con usted. Se hace llamar '
                                                         f'{creator_alias.content}. \n¿Aceptaría mantener una breve '
                                                         f'charla con esa persona?')
        await self.bot.add_reaction(proposal, u"\u2705")
        await self.bot.add_reaction(proposal, u"\u274E")

        def allowed_reaction(reaction, response_user):
            return (reaction.emoji == u"\u2705") or (reaction.emoji == u"\u274E")

        # Emoji respuesta
        response = await self.bot.wait_for_reaction(timeout=99, user=receiver, message=proposal, check=allowed_reaction)

        if (response is None or response.reaction.emoji == u"\u274E"):
            await self.bot.send_message(receiver, 'Entendido. Chat rechazado')
            await self.bot.send_message(user, 'Lamentamos comunicarle que no ha aceptado su conversación. '
                                              'Que tenga un buen día.')
        else:
            await self.bot.send_message(receiver, 'Entendido. El chat acaba de comenzar. Todo lo que diga será '
                                                  f'retransmitido a {creator_alias.content}.Puede dejar '
                                                  f'la charla en cualquier momento escribiendo ``$fin``')
            await self.bot.send_message(user, f'Buenas noticias, {receiver_alias.content} ha accedido a su '
                                              f'conversación. A partir de ahora todo será retransmitido. Puede dejar '
                                              f'la charla en cualquier momento escribiendo ``$fin``')

            if master.id not in (receiver.id, user.id):
                await self.bot.send_message(master, '```bash\n'
                                                    '$Ding $Ding $Ding! Maldad a la vista.\nDos jugadores han iniciado '
                                                    'un chat privado a través del Oceanic. Los integrantes son:\n'
                                                    f'"{user.name}" con el alias de "{creator_alias.content}"\n'
                                                    f'"{receiver.name}" con el alias de "{receiver_alias.content}"\n'
                                                    f'Ahora recibirá sus mensajes retransmitidos```')
            master_alias = creator_alias.content if master.id == user.id else 'Master Malvado'
            chat_room.new_chat(creator=user, receiver=receiver, master=master, creator_alias=creator_alias.content,
                               receiver_alias=receiver_alias.content, master_alias=master_alias)

    @commands.command(pass_context=True)
    async def fin(self, ctx):
        """Salir del chat actual"""
        user = ctx.message.author
        if chat_room.is_chatting(user):
            leaver, remain_members = chat_room.leave_chat(user)
            for remain_member in remain_members:
                await self.bot.send_message(remain_member[0], f'``{leaver} ha abandonado la sala``')
        else:
            await self.bot.send_message(user, 'No estás en ningún chat')

    async def on_message(self, message: discord.Message):
        # Check if user is chatting
        if not chat_room.is_chatting(message.author):
            return
        if not message.channel.type == discord.ChannelType.private:
            return
        if message.content.startswith('$a'):
            return
        author_alias, receivers = chat_room.get_receivers_for_message(message)
        for member in receivers:
            if message.attachments:
                with open('img/' + message.attachments[0]['filename'], 'wb') as image:
                    response = requests.get(message.attachments[0]['url'])
                    image.write(response.content)
                with open('img/' + message.attachments[0]['filename'], 'rb') as image:
                    await self.bot.send_file(member[0], image,
                                             content=f'```ini\n\n[{author_alias}]\n{message.content}\n```')
            else:
                await self.bot.send_message(member[0], f'```ini\n\n[{author_alias}]\n{message.content}\n```')


def setup(bot):
    bot.add_cog(ChatCog(bot))
