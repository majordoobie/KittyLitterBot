from discord.ext import commands
from discord import Embed
from configparser import ConfigParser
import os
import datetime
import aiohttp
from io import BytesIO

#Read config file for prefix and token
config = ConfigParser()
config.read('KittyLitterConfig.ini')
discord_client = commands.Bot(command_prefix = config['KittyLitter Configuration']['prefix'])
discord_client.remove_command("help")


def authorized(users_roles):
    for role in users_roles:
        if role.name == "CoC Leadership":
            return True
    return False

@discord_client.command(pass_context=True)
async def test():
    # Get all the channels and find the one you're looking for
    for channel in discord_client.get_all_channels():
        if type(channel.type) != int:
            if channel.name == "morestuff": # What ever channel you're looking into
                async for message in discord_client.logs_from(channel, reverse = True):
                    if message.attachments:
                        async with aiohttp.ClientSession() as session:
                            # note that it is often preferable to create a single session to use multiple times later - see below for this.
                            async with session.get(message.attachments[0]['url']) as resp:
                                buffer = BytesIO(await resp.read())

                            await discord_client.send_file(discord_client.get_channel("513334681354240000"), fp=buffer, filename="something.png")

                    elif message.content:
                        await discord_client.send_message(discord_client.get_channel("513334681354240000"), message.content)
                    


@discord_client.event
async def on_ready():
    print("Bot connected.")

@discord_client.command(pass_context=True)
async def help():
    msg = """
This tool is used to purge channels after war/cwl. It must first be set up by running /setup which will list
all the channels on the server and ask you which of those channels you would like to exclude from ever being 
purged. After that config file is created you can begin to purge all or purge by regex.

    /setup
        Prompts user to create the config file used to exclude channels from being purged.

    /readconfig
        Reads the config file and displays it back to the user

    /purrrge
        The cat gets to work and purges everything BUT the files in the exclude file.

    /purrrge <regex>
        Displays the chanels your regex was able to pull and asks if you would like those purged

    /archive <regex> destination
        Move all the channels identified by your regex into the destinatino folder. It currently supports 
        sorting by string_num and num. Otherwise, it will not sort the channel but will display the
        title of the source channel.

    """
    await discord_client.say("```{}```".format(msg))




@discord_client.command(pass_context=True, help="Create a config file with the channels you want to exclude from purging",
                            usage="/setup")
async def setup(ctx):
    if authorized(ctx.message.author.roles):
        pass
    else:
        await discord_client.say("Sorry, you don't have permission to use this.")
        return

    def check(msg):
        if msg.content.lower() == 'no' or msg.content.lower() == 'yes':
            return True
        else:
            return False

    # Check to see if the config file is there
    if 'exclusions' in config.sections():
        if len(config['exclusions'].keys()) > 0:
            await discord_client.say("Exclusions already exist, if you continue you will **clear** the exclusion list and startover. Would you like to continue? (Yes/No)")
            msg = await discord_client.wait_for_message(author=ctx.message.author, check = check)
            if msg.content.lower() == 'no':
                return
            elif msg.content.lower() == 'yes':
                for i in config['exclusions']:
                    config['exclusions'].pop(i)
                with open('KittyLitterConfig.ini', 'w') as f:
                    config.write(f)
                await discord_client.say("Purrrrging. Done.")
    else:
        config.add_section('exclusions')

    # get the list of all channels on the server
    channel_list = []
    for channel in discord_client.get_all_channels():
        if type(channel.type) != int:
            if channel.type.name == 'text':
                channel_list.append(channel.name)
    

    # sort the list and get the max length name for proper formating
    def dahkey(x):
        if len(x.split('_')) > 1:
            if x.split('_')[-1].isdigit():
                print()
                x = x.split('_')
                return x[0] + '_' + f'{int(x[1]):03d}'
            else:
                return x
        else:
            return x
    channel_list.sort(key=dahkey)
    
    char_length = 0
    for channel in channel_list:
        if len(channel) > char_length:
            char_length = len(channel)

    # Print out the the screen
    output = ''
    space = ' '
    for index, channel in enumerate(channel_list):
        space_calc = char_length - len(channel)
        space_calc += 2
        output += "```{}: {} {}```".format(channel, (space * space_calc), index)

    # ask for which index they want of channels they want to add to the config exclusion list
    await discord_client.say(output)
    msg = "Please enter the number of the channel you would like to exclude from purging. You can provide a list of space seperated numbers."
    await discord_client.say(msg)
    msg = await discord_client.wait_for_message(author=ctx.message.author)
    selection = []
    for num in msg.content.split(' '):
        if num.isdigit() == False:
            await discord_client.say("Input error detected. One of the inputs was not a integer. Exiting.")
            return

        elif num.isdigit():
            if int(num) >= len(channel_list):
                await discord_client.say("Input error detected. One of the inputs is not within the range of allowed inputs. Exiting.")
                return
            else:
                selection.append(num)

    # Add exclusions to the config file
    for num in selection:
        if int(num) < len(channel_list):
            config.set('exclusions',channel_list[int(num)], '')
    
    # write the config file to disc
    with open('KittyLitterConfig.ini', 'w') as f:
        config.write(f)
    
    await discord_client.say("Exclusion rules set. You can verify with /readconfig or run /purrrge")


@discord_client.command(pass_context=True,description="Show the config file to confirm excluded channels")
async def readconfig(ctx):
    if authorized(ctx.message.author.roles):
        pass
    else:
        await discord_client.say("Sorry, you don't have permission to use this.")
        return

    if 'exclusions' in config.sections():
        if len(config['exclusions'].keys()) > 0:
            await discord_client.say("**Current Exclusions:**")
            output = ' '
            space = '      '
            for i in config['exclusions'].keys():
                output += "```{} {}```".format(space, i)
            await discord_client.say(output)
        else:
            await discord_client.say("There are no exclusion channels set. Please use /setup")
    else:
        await discord_client.say("There are no exclusion channels set. Please use /setup")

@discord_client.command(pass_context=True)
async def archive(ctx):
    #Authorizor 
    if authorized(ctx.message.author.roles):
        pass
    else:
        await discord_client.say("Sorry, you don't have permission to use this.")
        return
    
    # Check function for asking for user input
    def check(msg):
        if msg.content.lower() == 'no' or msg.content.lower() == 'yes':
            return True
        else:
            return False

    # check for the config file
    if 'exclusions' in config.sections():
        if len(config['exclusions'].keys()) < 1:
            await discord_client.say("There are no exclusion channels set, use /setup")
            return

    
    if len(ctx.message.content.split(' ')) == 3:
        # Get the regex and destination argument
        regex, destination = ctx.message.content.split(' ')[1:]

        # Make sure the destination exists
        dest_channel = None
        for channel in discord_client.get_all_channels():
            if channel.name == destination:
                dest_channel = channel
                await discord_client.say("Channel assigned: **{}**".format(dest_channel.name))
        if dest_channel == None:
            await discord_client.say("Could not find the channel supplied. Please check spelling.")
            return

        # Use the regex to find channels
        purging_channels = []
        for channel in discord_client.get_all_channels():
            if type(channel.type) != int:
                if channel.type.name == "text":
                    if channel.name not in config['exclusions'].keys():
                        if channel.name.lower().startswith(regex.lower()):
                            purging_channels.append(channel.name)

        # Show the user what their regex pulled
            # Custom sorting key
        await discord_client.say("**Channels identified with your regex: **")
        def dahkey(x):
            if len(x.split('_')) == 1:
                return x
            elif len(x.split('_')) > 1:
                if type(x.split('_')[-1]) == int:
                    x = x.split('_')
                    return x[0] + '_' + f'{int(x[1]):03d}'
                else:
                    return x
            else:
                return x
        
        # Sort our listusing our custom key
        purging_channels.sort(key=dahkey)
        
        # Stage the output
        output = ' '
        space = '      '
        for i in purging_channels:
            output += "```{} {}```".format(space, i)
        await discord_client.say(output)
        
        # Ask if they're okay with what was identified
        await discord_client.say("**Destinatino set to --->** {}".format(dest_channel.name))
        await discord_client.say("Your regex returned the following channels to archive. Would you like to continue with the archive movement (Yes/No)")
        msg = await discord_client.wait_for_message(author=ctx.message.author, check = check)
        if msg.content.lower() == 'no':
            return
        elif msg.content.lower() == 'yes':
            await discord_client.say("Everything working so far, now add the archive piece")

    # If the incorrect number of arguments were given
    else:
        await discord_client.say("This command takes two arguments. Please use /help")
        return

@discord_client.command(aliases=['purge','clearall'], pass_context=True, description="Purrrge all channels except for those in the exclusion list.")
async def purrrge(ctx):
    if authorized(ctx.message.author.roles):
        pass
    else:
        await discord_client.say("Sorry, you don't have permission to use this.")
        return

    def check(msg):
        if msg.content.lower() == 'no' or msg.content.lower() == 'yes':
            return True
        else:
            return False

    # check for the config file
    if 'exclusions' in config.sections():
        if len(config['exclusions'].keys()) < 1:
            await discord_client.say("There are no exclusion channels set, use /setup")
            return

    # list exclusion files
    await discord_client.say("**Current Exclusions:**")
    output = ' '
    space = '      '
    for i in config['exclusions'].keys():
        output += "```{} {}```".format(space, i)
    await discord_client.say(output)

    # ask for comfirmation
    await discord_client.say("Exclusion channels are currently set to the list above. Would you like to continue? (Yes/No)")
    msg = await discord_client.wait_for_message(author=ctx.message.author, check=check)
    if msg.content.lower() == 'no':
        return
    elif msg.content.lower() == 'yes':  # This is where you left off, can't print shit
        if len(ctx.message.content.split(' ')) == 1:
            for channel in discord_client.get_all_channels():
                if type(channel.type) != int:
                    if channel.type.name == 'text':
                        if channel.name not in config['exclusions'].keys():
                            await discord_client.say("Purrrrging {}".format(channel.name))
                            await discord_client.purge_from(channel)
    else:
        arg = ctx.message.content.split(' ')[1]
        purging_channels = []
        for channel in discord_client.get_all_channels():
            if type(channel.type) != int:
                if channel.type.name == "text":
                    if channel.name not in config['exclusions'].keys():
                        if channel.name.startswith(arg):
                            purging_channels.append(channel.name)

        # Verify user about the shit they're going to purge
        await discord_client.say("**Current Channels to Purge:**")
        def dahkey(x):
            if len(x.split('_')) == 1:
                return x
            elif len(x.split('_')) > 1:
                x = x.split('_')
                return x[0] + '_' + f'{int(x[1]):03d}'
            else:
                return x
        purging_channels.sort(key=dahkey)
        
        output = ' '
        space = '      '
        for i in purging_channels:
            output += "```{} {}```".format(space, i)
        await discord_client.say(output)
        
        await discord_client.say("Your regex returned the following channels to purge. Would you like to purge (Yes/No)")
        msg = await discord_client.wait_for_message(author=ctx.message.author, check = check)
        if msg.content.lower() == 'no':
            return
        elif msg.content.lower() == 'yes':
            for channel in discord_client.get_all_channels():
                if type(channel.type) != int:
                    if channel.type.name == 'text':
                        if channel.name in purging_channels:
                                await discord_client.say("Purrrrging {}".format(channel.name))
                                await discord_client.purge_from(channel)
            
            

if __name__ == "__main__":
    discord_client.run(config['KittyLitter Configuration']['token'])

    