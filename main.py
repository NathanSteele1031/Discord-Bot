import discord, json
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

def main():
    player_names = get_player_names()
    players = {}

    for name in player_names:
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
            name = message.content[6:]
            if name in players:
                await message.channel.send(f'Level: {players[name].level}')
            else:
                await message.channel.send('Player not found')

        if message.content.startswith('!bye'):
            await message.channel.send('See ya!')

    # 3. Run it
    client.run(get_token(input('Enter your token: ')))

if __name__ == "__main__":
    main()