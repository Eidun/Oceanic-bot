import discord


class Chat:

    id: str

    players = {}

    def __init__(self, creator: discord.Member):
        self.id = creator.id
        self.players[creator.id] = creator

    def add_guy(self, guy: discord.Member):
        self.players[guy.id] = guy

    def remove_guy(self, guy: discord.Member):
        del self.players[guy.id]
