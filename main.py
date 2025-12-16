import discord, json, os
import player

def get_token(path):
    with open(path, 'r') as f:
        return f.read()

def get_player_names(): 
    try:
        with open('UserData/players.txt', 'r') as f:
            return f.read().split("\n")
    except FileNotFoundError:
        with open('UserData/players.txt', 'w') as f:
            pass
        return []
    
def user_loaded(user_id, users_loaded):
    return True if user_id in users_loaded else False

def main():
    player_names = get_player_names()
    print(player_names)
    players = {}

    users_loaded = {}

    for name in player_names:
        if name == "":
            continue
        players[name] = player.Player(f"UserData/{name}.json")

    for name, user in players.items():
        print(user.level)

    # 1. Setup minimal permissions
    intents = discord.Intents.default()
    intents.message_content = True

    # 2. Create the client connection
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')

    @client.event
    async def on_message(message):
        # Don't let the bot reply to itself (infinite loop prevention)
        if message.author == client.user:
            return

        if message.content.startswith('!show'):
            if message.content.strip() == '!show' and not user_loaded(message.author.id, users_loaded):
                await message.channel.send('Please specify a player name')
                return
            elif user_loaded(message.author.id, users_loaded):
                player_data = users_loaded[message.author.id]
                await message.channel.send(f'Level: {player_data.level}\nItems: {player_data.items}')
                return

            name = message.content[6:]
            if name in players:
                await message.channel.send(f'Level: {players[name].level}\nItems: {players[name].items}')
            else:
                await message.channel.send('Player not found')

        if message.content.startswith('!create'):
            if message.content.strip() == '!create':
                await message.channel.send('Please specify a player name')
            
            name = message.content[8:]
            if name in players:
                await message.channel.send('Player already exists')
            else:
                players[name] = player.Player()
                player_names.append(name)
                with open('UserData/players.txt', 'w') as f:
                    f.write("\n".join(player_names))
                players[name].save(f"UserData/{name}.json")
                await message.channel.send('Player created')
        
        if message.content.startswith("!remove"):
            if message.content.strip() == '!remove':
                await message.channel.send('Please specify a player name')
            
            name = message.content[8:]
            if name in players:
                del players[name]
                player_names.remove(name)
                os.remove(f"UserData/{name}.json")
                with open('UserData/players.txt', 'w') as f:
                    f.write("\n".join(player_names))
                await message.channel.send('Player removed')
            else:
                await message.channel.send('Player not found')

        if message.content.startswith("!levelup"):
            if message.content.strip() == '!levelup' and not user_loaded(message.author.id, users_loaded):
                await message.channel.send('Please specify a player name')
            elif user_loaded(message.author.id, users_loaded):
                player_data = users_loaded[message.author.id]
                player_data.level += 1
                player_data.save(f"UserData/{player_data.name}.json")
                await message.channel.send(f'⭐⭐{player_data.name} has leveled up to level {player_data.level}⭐⭐')
                return
            
            name = message.content[9:]
            if name in players:
                players[name].level += 1
                players[name].save(f"UserData/{name}.json")
                await message.channel.send(f'⭐⭐{name} has leveled up to level {players[name].level}⭐⭐')
            else:
                await message.channel.send('Player not found')

        if message.content.startswith("!load"):
            user = message.author
            player_name = message.content[6:]
            users_loaded[user.id] = players[player_name]
            await message.channel.send(f'Loaded player {player_name} to {user.name}')

    # 3. Run it
    client.run(input('Enter your token: '))

if __name__ == "__main__":
    main()