from discord.ext import commands
from discord import Embed
import discord
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

# Check functino for the discord_client.wait_for(check=yesno_check)
def yesno_check(m):
        print(m.content)
        if m.content == 'yes':
            return m.content
        elif m.content == 'no':
            return m.content
        

@discord_client.command()
async def test(ctx):
    for i in discord_client.get_all_channels():
        print(isinstance(i, discord.TextChannel))
        return
    #     print(i.category) #cat name
    #     print(i.category_id) #cat ID
    #     print(i.guild)  # discord name
    #     print(i.id)     #CHANNEL ID 
    #     print(i.name)   #name of channel
    #     async for j in i.history():
    #         print(j.created_at)
    #         print(j.type)
            
    #     #print(i.members)
    #     print("---------------")
    # category_list = discord_client.guilds[0].categories 
    # for i in category_list:
    #     print(i)
    
        


@discord_client.event
async def on_ready():
    print("Bot connected.")
    game = discord.Game("with cat nip~")
    await discord_client.change_presence(status=discord.Status.idle, activity=game)
    

@discord_client.command()
async def help(ctx):
    desc = ("KittyLitter is used to archive and purge channels after war/cwl. It must first be set up by running /setup. "
    "Setup will prompt you for the categories in the channel i.e. traditional_war and then prompt you for an "
    "anchor. An anchor is a regex you can use to identify the channels within the categories i.e. warroom "
    "Afer the categories and war channels are identified, you will be prompt to add any channels into the "
    "'safe' exclusion list. This will make sure the bot will always ignore those channels.") 

    setup_desc = ("Prompts user to setup the configuration file. Be sure to use option zero first.")

    readconfig_desc = ("Prints out the configuration file for verification of proper setup.")

    archive_desc = ("Uses the config file to identify the categories enabled for archiving. The list of "
    "categories will be displayed to you. Once channels are identified and archive channel exists, archiving will beging. "
    "This process may take a while. Please be patient as the bot is only as fast as the network traffic.")

    archive_descc = ("Queries the configuration file for the achor with the category supplied. Once channels are identified "
    "and archive channel exists, archiving will beging. This process may take a while. Please be patient as the bot is only "
    "as fast as the network traffic.")

    purge_desc = ("Queries the configuration file for the categories enabled for archiving. The list of "
    "categories will be displayed to you. Once channels are identified, purging will beging. Please be sure to"
    "archive the channels first if you want to save them.")

    prige_descc = ("Queries the configuration file for the archor with the category supplied. The list of "
    "categories will be displayed to you. Once channels are identified, purging will beging. Please be sure to "
    "archive the channels first if you want to save them.")

    embed = Embed(title='Meowwww!', description= desc, color=0x8A2BE2)
    embed.add_field(name="Commands:", value=":", inline=True)
    embed.add_field(name="/setup", value=setup_desc, inline=False)
    embed.add_field(name="/readconfig", value=readconfig_desc, inline=False)
    embed.add_field(name="/archive", value=archive_desc, inline=False)
    embed.add_field(name="/archive <category>", value=archive_descc, inline=False)
    embed.add_field(name="/purge", value=purge_desc, inline=False)
    embed.add_field(name="/purge <category>", value=prige_descc, inline=False)
    await ctx.send(embed=embed)




@discord_client.command()
async def setup(ctx):
    if authorized(ctx.message.author.roles):
        pass
    else:
        await ctx.send("Sorry, you don't have permission to use this.")
        return
        
    def inter(msg):
        if msg.content in ['0', '1', 'q', 'Q']:
            return msg.content
        return
        
    # Way to control the options chosen by the user
    categorize = False
    exclusionize = False

    # Ask to set up either category or exclusions 
    await ctx.send("Would you like to setup your discord categories or exclusions?")
    await ctx.send("```Categories:    0 <-- Rec First``````Exclusions:    1``````Quit:          q```")
    msg = await discord_client.wait_for('message', check = inter)
    if msg.content.lower() == 'q':
        await ctx.send("Aborting.")
        return
    elif msg.content == '0':
        categorize = True
    elif msg.content == '1':
        exclusionize = True
    else:
        await ctx.send("Timed out or user entry not understood. Aborting.")
        return

############################################################################################################ -- > category
    # Set up categories
    if categorize:
        # Ask if they want to clear our their category or continue
        if 'categories' in config.sections():
            if len(config['categories'].keys()) > 0:
                await ctx.send("Exclusions already exist, if you continue you will **clear** the exclusion list and startover. Would you like to continue? (Yes/No)")
                msg = await discord_client.wait_for('message', check = yesno_check)
                if msg.content.lower() == 'no':
                    return
                elif msg.content.lower() == 'yes':
                    for i in config['categories']:
                        config['categories'].pop(i)
                    with open('KittyLitterConfig.ini', 'w') as f:
                        config.write(f)
                    await ctx.send("Purrrrging. Done.")
        else:
            config.add_section('categories')

        # collect all the categories and ask if there is any they want to add
        category_list = discord_client.guilds[0].categories


        # Calculate the space to add when printing
        char_length = 0
        for channel in category_list:
            if len(channel.name) > char_length:
                char_length = len(channel.name)

        # Set up printing variable
        output = ''
        space = ' '
        for index, channel in enumerate(category_list):
            space_calc = char_length - len(channel.name)
            space_calc += 2
            output += "```{}: {} {}```".format(channel.name, (space * space_calc), index)

        # ask for which index they want of channels they want to add to the config exclusion list
        await ctx.send(output)
        msg = "**Please select the categories that will be flagged as war channels.**\nUse space seperated integers."
        await ctx.send(msg)
        msg = await discord_client.wait_for('message')

        # Actual selection list
        selection = []
        for num in msg.content.split(' '):
            if num.isdigit() == False:
                await ctx.send("Input error detected. One of the inputs was not a integer. Exiting.")
                return
            elif num.isdigit():
                if int(num) >= len(category_list):
                    await ctx.send("Input error detected. One of the inputs is not within the range of allowed inputs. Exiting.")
                    return
                else:
                    selection.append(num)
        

        # Add exclusions to the config file
        for num in selection:
            if int(num) < len(category_list):
                await ctx.send("What is a good anchor regex for this category? --> **{}**".format(category_list[int(num)].name))
                msg = await discord_client.wait_for('message')
                config.set('categories',category_list[int(num)].name, msg.content)

        # write the config file to disc
        with open('KittyLitterConfig.ini', 'w') as f:
            config.write(f)
        
        await ctx.send("Categories set. You can verify with /readconfig or run /setup again for exclusions\n")
############################################################################################################ -- > categories
############################################################################################################ -- > exclusions
    if exclusionize == False:
        await ctx.send("Would you like to continue with exclusions on setup? You can do this later. (Yes/No)")
        msg = await discord_client.wait_for('message', check=yesno_check)
        if msg.content == 'no':
            await ctx.send("Okay, you can check the current settings with /readconfig.")
            return
        elif msg.content == 'yes':
            exclusionize = True
    if exclusionize:
        # Check to see if the config file is there
        if 'exclusions' in config.sections():
            if len(config['exclusions'].keys()) > 0:
                await ctx.send("Exclusions already exist, if you continue you will **clear** the exclusion list and startover. Would you like to continue? (Yes/No)")
                msg = await discord_client.wait_for('message', check = yesno_check)
                if msg.content.lower() == 'no':
                    return
                elif msg.content.lower() == 'yes':
                    for i in config['exclusions']:
                        config['exclusions'].pop(i)
                    with open('KittyLitterConfig.ini', 'w') as f:
                        config.write(f)
                    await ctx.send("Clearing exclusions.")
        else:
            config.add_section('exclusions')
    else:
        return

    # Grab all the war channels to exclude them from exclusions LOL
    warchannels = [] #contains category names
    if len(config['categories'].keys()) > 0:
        for i in config['categories'].keys():
            warchannels.append(i.lower())
    else:
        await ctx.send("There are no categories identified. Please follow option one to set up categories for war.")
        return
    
    # get the list of all channels on the server
    channel_list = []
    for channel in discord_client.get_all_channels():
        if str(channel.category).lower() not in warchannels:
            if isinstance(channel, discord.TextChannel):
                channel_list.append(channel.name)
    
    # sort channel
    channel_list.sort(key=dahkey)

    # Calculate the space to add when printing
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
    await ctx.send(output)
    msg = "Please enter the number of the channel you would like to exclude from purging. You can provide a list of space seperated numbers."
    await ctx.send(msg)
    msg = await discord_client.wait_for('message')
    selection = []
    for num in msg.content.split(' '):
        if num.isdigit() == False:
            await ctx.send("Input error detected. One of the inputs was not a integer. Exiting.")
            return

        elif num.isdigit():
            if int(num) >= len(channel_list):
                await ctx.send("Input error detected. One of the inputs is not within the range of allowed inputs. Exiting.")
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
    
    await ctx.send("Exclusion rules set. You can verify with /readconfig.")

############################################################################################################ -- > exclusions


@discord_client.command(pass_context=True,description="Show the config file to confirm excluded channels")
async def readconfig(ctx):
    if authorized(ctx.message.author.roles):
        pass
    else:
        await ctx.send("Sorry, you don't have permission to use this.")
        return

    if 'exclusions' in config.sections():
        if len(config['exclusions'].keys()) > 0:
            await ctx.send("**Current Exclusions:**")
            space = '      '
            output = "```{} |{}|```".format(space, "Channel")
            for i in config['exclusions'].keys():
                output += "```{} {}```".format(space, i)
            await ctx.send(output)
        else:
            await ctx.send("There are no exclusion channels set. Please use /setup")
    else:
        await ctx.send("There are no exclusion channels set. Please use /setup")

    if 'categories' in config.sections():
        if len(config['categories'].keys()) > 0:
            await ctx.send("**Current Categories Identified:**")
            space = '      '
            output = "```{} |{}|    |{}|```".format(space, "Category", "Regex")
            for i,e in config['categories'].items():
                output += "```{} {} -> {}```".format(space, i, e)
            await ctx.send(output)
        else:
            await ctx.send("There are no exclusion channels set. Please use /setup")
    else:
        await ctx.send("There are no exclusion channels set. Please use /setup")
    

@discord_client.command(pass_context=True)
async def archive(ctx):
    #Authorizor 
    if authorized(ctx.message.author.roles):
        pass
    else:
        await ctx.send("Sorry, you don't have permission to use this.")
        return

    # check for the config file
    if 'exclusions' in config.sections():
        if len(config['exclusions'].keys()) < 1:
            await ctx.send("There are no exclusion channels set, use /setup")
            return

    if len(ctx.message.content.split(' ')) == 3:
        # Get the regex and destination argument
        regex, destination = ctx.message.content.split(' ')[1:]

        # Make sure the destination exists
        dest_channel = None
        for channel in discord_client.get_all_channels():
            if channel.name == destination:
                dest_channel = channel
        if dest_channel == None:
            await ctx.send("Could not find the channel supplied. Please check spelling.")
            return

        # Use the regex to find channels
        purging_channels = []
        for channel in discord_client.get_all_channels():
            if type(channel.type) != int:
                if channel.type.name == "text":
                    if channel.name not in config['exclusions'].keys():
                        if channel.name.lower().startswith(regex.lower()):
                            if channel.name.lower().endswith("archive"):
                                pass
                            else:
                                purging_channels.append(channel.name)

        # Show the user what their regex pulled

        await ctx.send("**Channels identified with your regex: **")
        
        # Sort our listusing our custom key
        purging_channels.sort(key=dahkey)
        
        # Stage the output
        output = ' '
        space = '      '
        for i in purging_channels:
            output += "```{} {}```".format(space, i)
        await ctx.send(output)
        
        # Ask if they're okay with what was identified
        await ctx.send("**Destinatino set to --->** {}".format(dest_channel.name))
        await ctx.send("Your regex returned the following channels to archive. Would you like to continue with the archive movement (Yes/No)")
        msg = await discord_client.wait_for('message', check = yesno_check)
        if msg.content.lower() == 'no':
            return #dest_channel
        elif msg.content.lower() == 'yes':
            await ctx.send("Please standby while I archive the channel(s) selected. I will let you know when it is done. Be aware that this could take a while due to network traffic.")
            for channel_str in purging_channels:
                for channel in discord_client.get_all_channels():
                    if channel.name == channel_str:
                        await discord_client.send_message(dest_channel, "**Copied from {} on {}**\n\n\n".format(channel.name, datetime.datetime.utcnow()))
                        async for message in discord_client.logs_from(channel, limit=1000, reverse = True, after = datetime.datetime.utcnow() - datetime.timedelta(days=5)):
                            if message.attachments:
                                async with aiohttp.ClientSession() as session:
                                    # note that it is often preferable to create a single session to use multiple times later - see below for this.
                                    async with session.get(message.attachments[0]['url']) as resp:
                                        buffer = BytesIO(await resp.read())
                                    await discord_client.send_file(dest_channel, fp=buffer, filename="something.png")
                            elif message.content:
                                await discord_client.send_message(dest_channel, message.content)
            await ctx.send("That took a while! Job is all done.")
                                
    # If the incorrect number of arguments were given
    else:
        await ctx.send("This command takes two arguments. Please use /help")
        return

@discord_client.command(aliases=['purge','clearall'], pass_context=True, description="Purrrge all channels except for those in the exclusion list.")
async def purrrge(ctx):
    if authorized(ctx.message.author.roles):
        pass
    else:
        await ctx.send("Sorry, you don't have permission to use this.")
        return

    def check(msg):
        if msg.content.lower() == 'no' or msg.content.lower() == 'yes':
            return True
        else:
            return False

    # check for the config file
    if 'exclusions' in config.sections():
        if len(config['exclusions'].keys()) < 1:
            await ctx.send("There are no exclusion channels set, use /setup")
            return

    # list exclusion files
    await ctx.send("**Current Exclusions:**")
    output = ' '
    space = '      '
    for i in config['exclusions'].keys():
        output += "```{} {}```".format(space, i)
    await ctx.send(output)

    # ask for comfirmation
    await ctx.send("Exclusion channels are currently set to the list above. Would you like to continue? (Yes/No)")
    msg = await discord_client.wait_for(author=ctx.message.author, check=check)
    if msg.content.lower() == 'no':
        return
    elif msg.content.lower() == 'yes':  # This is where you left off, can't print shit
        if len(ctx.message.content.split(' ')) == 1:
            for channel in discord_client.get_all_channels():
                if type(channel.type) != int:
                    if channel.type.name == 'text':
                        if channel.name not in config['exclusions'].keys():
                            await ctx.send("Purrrrging {}".format(channel.name))
                            await discord_client.purge_from(channel)
        else:
            arg = ctx.message.content.split(' ')[1]
            purging_channels = []
            for channel in discord_client.get_all_channels():
                if type(channel.type) != int:
                    if channel.type.name == "text":
                        if channel.name not in config['exclusions'].keys():
                            if channel.name.lower().startswith(arg):
                                if channel.name.lower().endswith("archive"):
                                    pass
                                else:
                                    purging_channels.append(channel.name)

        # Verify user about the shit they're going to purge
        await ctx.send("**Current Channels to Purge:**")
        purging_channels.sort(key=dahkey)
        
        output = ' '
        space = '      '
        for i in purging_channels:
            output += "```{} {}```".format(space, i)
        await ctx.send(output)
        
        await ctx.send("Your regex returned the following channels to purge. Would you like to purge (Yes/No)")
        msg = await discord_client.wait_for(author=ctx.message.author, check = check)
        if msg.content.lower() == 'no':
            return
        elif msg.content.lower() == 'yes':
            await ctx.send("Please stand by while I get to work. This may take a while due to network traffic.")
            for channel in discord_client.get_all_channels():
                if type(channel.type) != int:
                    if channel.type.name == 'text':
                        if channel.name in purging_channels:
                                await ctx.send("Purrrrging {}".format(channel.name))
                                await discord_client.purge_from(channel)
            await ctx.send("All done!")
            
            

if __name__ == "__main__":
    discord_client.run(config['KittyLitter Configuration']['token'])

    