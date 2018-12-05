import discord


class ChatRoom:
    chats = {}

    def new_chat(self, creator: discord.Member, receiver: discord.Member, master: discord.Member, creator_alias: str,
                 receiver_alias: str, master_alias: str):
        """Creates a new Chat conversation between 2 members and the master moderating"""
        self.chats[(creator.id, receiver.id, master.id)] = Chat(creator, receiver, master, creator_alias, receiver_alias,
                                                     master_alias)

    def leave_chat(self, member: discord.Member):
        """Finishes a Chat conversation"""
        if not self.is_chatting(member):
            return
        chat_key = ()
        for chatters in self.chats:
            if member.id in chatters:
                chat_key = chatters
        leaver, remain_members = self.chats[chat_key].leave_chat(member)
        chat_new_key = tuple(member_key for member_key in chat_key if not member_key == member.id)
        self.chats[chat_new_key] = self.chats[chat_key]
        del self.chats[chat_key]
        if remain_members.__len__() <= 1:
            del self.chats[chat_new_key]
        return leaver, remain_members

    def is_chatting(self, member: discord.Member):
        """Checks if the member is already in some existing chat"""
        for chatters in self.chats.keys():
            if member.id in chatters:
                return True
        return False

    def get_receivers_for_message(self, message: discord.Message):
        """Returns a list of the tuple receivers for a message in their chat"""
        for chatters in self.chats.keys():
            if message.author.id in chatters:
                return self.chats[chatters].get_receivers(message.author)


class Chat:
    players = {}

    def __init__(self, creator: discord.Member, receiver: discord.Member, master: discord.Member, creator_alias: str,
                 receiver_alias: str, master_alias: str):
        self.players[creator.id] = (creator, creator_alias)
        self.players[receiver.id] = (receiver, receiver_alias)
        self.players[master.id] = (master, master_alias)

    def get_receivers(self, member):
        """Returns a list of the tuple receivers for a member"""
        aux_players = self.players.copy()
        member_alias = aux_players[member.id][1]
        del aux_players[member.id]
        return member_alias, aux_players.values()

    def leave_chat(self, member):
        leaver = self.players[member.id][1]
        del self.players[member.id]
        return leaver, self.players.values()


chat_room = ChatRoom()
