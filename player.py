import json

class Player:
    def __init__(self, file=None, name=None):
        if not file:
            self.level = 1
            self.items = []
            self.owner = None
            self.name = name
        else:
            self.load(file)
    
    def set_owner(self, owner):
        """
        The value of owner should be a discord user id
        """

        self.owner = owner
    
    def is_owner(self, user_id):
        return self.owner == user_id

    def load(self, file):
        with open(file, 'r') as f:
            data = json.load(f)
            self.level = data['level']
            self.items = data['items']
            self.owner = data['owner']
            self.name = data['name']
        
    def save(self, file):
        with open(file, 'w') as f:
            json.dump({
                'level': self.level,
                'items': self.items,
                'owner': self.owner,
                'name': self.name
            }, f)