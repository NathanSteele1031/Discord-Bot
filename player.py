import json

class Player:
    def __init__(self, file=None):
        if not file:
            self.level = 1
        else:
            self.load(file)
    
    def load(self, file):
        with open(file, 'r') as f:
            data = json.load(f)
            self.level = data['level']
        
    def save(self, file):
        with open(file, 'w') as f:
            json.dump({'level': self.level}, f)