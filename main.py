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
    return True if user_id in users_loaded.keys() else False

def remove_from_load(player_name, users_loaded):
    if player_name in users_loaded:
        del users_loaded[player_name]

def is_gm(user_id, gm_id):
    return True if user_id == gm_id else False

def get_gm_id():
    with open('UserData/gm.txt', 'r') as f:
        return int(f.read())

def save_gm_id(gm_id):
    with open('UserData/gm.txt', 'w') as f:
        f.write(str(gm_id))

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
        gm_id = get_gm_id()

        # Don't let the bot reply to itself (infinite loop prevention)
        if message.author == client.user:
            return
        
        if message.content.startswith("!help"):
            await message.channel.send('''
            Commands:
            !showplayers - Shows all players
            !remove <name> - Removes a player
            !load <name> - Loads a player so you don't have to type the player name for commands below
            !show <name> - Shows a specific player
            !create <name> - Creates a player
            !levelup <name> - Levels up a player
            !additem <name> - Adds an item to a player
            ''')

        if message.content.startswith("!showplayers"):
            if player_names != [] and player_names != [""]:
                await message.channel.send("\n".join(player_names))
            else:
                await message.channel.send("None have been made! Make some with !create <name>")

        if message.content.startswith('!show') and not message.content.startswith("!showplayers"):
            if message.content.strip() == '!show' and not user_loaded(message.author.id, users_loaded):
                await message.channel.send('Please specify a player name')
                return
            elif user_loaded(message.author.id, users_loaded):
                player_data = users_loaded[message.author.id]
                await message.channel.send(f'Level: {player_data.level}\nItems: {player_data.items}\nSkills: {player_data.skills}')
                return

            name = message.content[6:]
            if name in players:
                await message.channel.send(f'Level: {players[name].level}\nItems: {players[name].items}\nSkills: {players[name].skills}')
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
                players[name].set_owner(message.author.id)
                players[name].name = name
                player_names.append(name)
                with open('UserData/players.txt', 'w') as f:
                    f.write("\n".join(player_names))
                players[name].save(f"UserData/{name}.json")
                await message.channel.send('Player created')
        
        if message.content.startswith("!remove"):
            if message.content.strip() == '!remove':
                await message.channel.send('Please specify a player name')
            
            name = message.content[8:]
            if name in players and players[name].is_owner(message.author.id):
                del players[name]
                player_names.remove(name)
                remove_from_load(name, users_loaded)
                os.remove(f"UserData/{name}.json")
                with open('UserData/players.txt', 'w') as f:
                    f.write("\n".join(player_names))
                await message.channel.send('Player removed')
            else:
                await message.channel.send('Player not found')

        if message.content.startswith("!levelup"):
            if message.content.strip() == '!levelup' and not user_loaded(message.author.id, users_loaded):
                await message.channel.send('Please specify a player name')
            
            if user_loaded(message.author.id, users_loaded):
                player_data = users_loaded[message.author.id]
                name = player_data.name
            else:
                name = message.content[9:]
            if name in players:
                players[name].level += 1

                players[name].save(f"UserData/{name}.json")
                skills_unlocked = players[name].skills_unlocked()
                await message.channel.send(f'⭐⭐{name} has leveled up to level {players[name].level}⭐⭐')
                if skills_unlocked != []:
                    await message.channel.send(f'You have unlocked the following skills: {", ".join(skills_unlocked)}')
            else:
                await message.channel.send('Player not found')

        if message.content.startswith("!additem"):
            if message.content.strip() == '!additem' and not user_loaded(message.author.id, users_loaded):
                await message.channel.send('Please specify a player name')
            elif user_loaded(message.author.id, users_loaded):
                player_data = users_loaded[message.author.id]
                player_data.items.append(message.content[9:])
                player_data.save(f"UserData/{player_data.name}.json")
                await message.channel.send(f'Added {message.content[9:]} to {player_data.name}')
                return
            
            message_split = message.content.split(' ')
            name = message_split[1]
            if name in players and (players[name].is_owner(message.author.id) or message.author.id == is_gm(message.author.id, gm_id)):
                players[name].items.append(message_split[2])
                players[name].save(f"UserData/{name}.json")
                await message.channel.send(f'Added {message.content[9:]} to {name}')
            elif name in players and message.author.id != is_gm(message.author.id, gm_id):
                await message.channel.send('You do not own this player')
            else:
                await message.channel.send('Player not found')

        if message.content.startswith("!load"):
            user = message.author
            player_name = message.content[6:]
            if players[player_name].is_owner(user.id):
                users_loaded[user.id] = players[player_name]
                await message.channel.send(f'Loaded player {player_name} to {user.name}')
            else:
                await message.channel.send('You do not own this player')

        if message.content.startswith("!addskill"):
            if message.content.strip() == '!addskill' and not user_loaded(message.author.id, users_loaded):
                await message.channel.send('Please specify a player name')
            elif user_loaded(message.author.id, users_loaded):
                message_split = message.content.split(' ')
                if len(message_split) != 3:
                    await message.channel.send('Please specify a skill and level with spaces (!addskill skillname level)')
                player_data = users_loaded[message.author.id]
                player_data.skills.append([message_split[1], int(message_split[2])])
                player_data.save(f"UserData/{player_data.name}.json")
                await message.channel.send(f'Added {message.content[11:]} to {player_data.name}')
                return
            
            message_split = message.content.split(' ')
            name = message_split[1]
            if name in players and (players[name].is_owner(message.author.id) or message.author.id == is_gm(message.author.id, gm_id)):
                players[name].skills.append([message_split[2], int(message_split[3])])
                players[name].save(f"UserData/{name}.json")
                await message.channel.send(f'Added {message_split[2]} to {name}')
            elif name in players and message.author.id != is_gm(message.author.id, gm_id):
                await message.channel.send('You do not own this player')
            else:
                await message.channel.send('Player not found')

        if message.content.startswith("!gmme"):
            gm_id = message.author.id
            save_gm_id(gm_id)
            await message.channel.send(f'GM set to {message.author.name}')

    # 3. Run it
    client.run(input('Enter your token: '))

if __name__ == "__main__":
    main()