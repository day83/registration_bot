from datetime import datetime

class User:
    objects = {}

    def __init__(self, user_id, username="", full_name="", quest="", bot_active=False, last_visit=""):
        self.id = user_id
        self.username = username
        self.full_name = full_name
        self.quest = quest
        self.bot_active = bot_active
        self.last_visit = last_visit
        self.objects[user_id] = self

    def __repr__(self):
        res = f'{self.id} {self.username} {self.full_name}'
        res += f'\n{self.quest.rstrip()}\n {self.bot_active} {self.last_visit}'
        return res
