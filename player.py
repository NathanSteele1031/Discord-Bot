import json

class Player:
    def __init__(self, file=None):
        if not file:
            self.level = 1
            self.items = []
        else:
            self.load(file)
    
    def load(self, file):
        with open(file, 'r') as f:
            data = json.load(f)
            self.level = data['level']
            self.items = data['items']
        
    def save(self, file):
        with open(file, 'w') as f:
            json.dump({
                'level': self.level,
                'items': self.items
            }, f)