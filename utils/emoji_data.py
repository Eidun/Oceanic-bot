players_id = ['222022647796465664', '186969542927450112', '176716105304244224', '187146845502439424',
              '404604675225157633', '245959396503453716', '194087774922604545']

emoji_list = [u"\u0031" + u"\u20E3", u"\u0032" + u"\u20E3", u"\u0033" + u"\u20E3", u"\u0034" + u"\u20E3",
              u"\u0035" + u"\u20E3", u"\u0036" + u"\u20E3", u"\u0037" + u"\u20E3", u"\u0038" + u"\u20E3",
              u"\u0039" + u"\u20E3"]


async def get_receiver(bot, user):
    players = __load_players(bot, user)
    # Asignar emoji a cada usuario
    grouped = __group_emoji_user(players)

    receivers_text = '**Seleccione al destinatario:**\n'
    for emoji, player in grouped.items():
        receivers_text += emoji + '  ' + player.name + '\n'
    receivers = await bot.send_message(user, receivers_text)

    for emoji in grouped.keys():
        await bot.add_reaction(receivers, emoji)

    receiver_emoji = await bot.wait_for_reaction(user=user, message=receivers, emoji=emoji_list, timeout=50)
    if receiver_emoji is None:
        return
    return grouped[receiver_emoji.reaction.emoji]


def __group_emoji_user(players):
    grouped = {}
    emojis = emoji_list.copy()
    for player in players:
        grouped[emojis[0]] = player
        emojis.pop(0)
    return grouped


def __load_players(bot, creator):
    return list(set(player for player in bot.get_all_members() if
                    player.id != creator.id and player.id in players_id))
