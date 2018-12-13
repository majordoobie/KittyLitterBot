from discord.ext import commands
from discord import Embed
import discord
from configparser import ConfigParser
import os
import datetime
import aiohttp
#from io import BytesIO
import io

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
        if m.content.lower() in ['yes','no']:
            return True
        else:
            return False

def get_channel(channel_str):
    for cat_obj in discord_client.guilds[0].categories:
        if cat_obj.name.upper() == 'ARCHIVES':
            for channel_obj in cat_obj.channels:
                if channel_obj.name.upper() == channel_str.upper():
                    return channel_obj


@discord_client.command()
async def test(ctx):
    pass


    # collect all the categories and ask if there is any they want to add
    #print(dir(discord_client.guilds[0].categories.index('ARCHVIES')))
    # arch = ''
    # for i in discord_client.guilds[0].categories:
    #     if i.name == 'ARCHIVES':
    #         arch = i
    # for i in dir(arch):
    #     print(i)

    # async with ctx.typing():
    #     for i in discord_client.guilds[0].by_category():
    #         if isinstance(i[0], discord.channel.CategoryChannel):
    #             if i[0].name.upper() == 'ARCHIVES':
    #                 print(i[0].name)
    #                 for j in i[0].channels:
    #                     print(j.name)
        
    # for i in category_list:
    #     if i.name.upper() == 'ARCHIVES':
    #         print("it's there {}".format(i.name))
    #     else:
    #         pass
    # for i in discord_client.get_all_channels():
    #     print(isinstance(i, discord.TextChannel))
    #     return
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
    await discord_client.change_presence(status=discord.Status.online, activity=game)

    
    

@discord_client.command()
async def help(ctx):
    desc = ("KittyLitter is used to archive and purge channels after war/cwl. It must first be set up (once) by running /setup. "
    "Setup will promt you for two options.\n\n"
    "(Option 1: Categories)\n"
    "Identify the categories that will be the war channels. The category will be used to streamline "
    "archiving and purging the channels that fall underneath it. Each category should list the channels that correspond to "
    "the CoC war enemy position in order from least to greatest. For example:\n\n"
    "---> NORMAL_WAR\n"
    "-----> warroom_1\n"
    "-----> warroom_2\n\n"
    "Once you have identified NORMAL_WAR as a war category, you will be promt to map that category to a channel under "
    "'ARCHIVES'. If the category or a channel under this category does not exist, please create it. Once that category "
    "has been mapped to a unique archive channel, the archive command will automatically use that channel as the destination "
    "for all the channels in the category.\n\n"
    "(Option 2: Exclusions)\n"
    "Option 2 is used to set up channels you want the script to ignore. Some channels to consider would be channels used "
    "to post rules or discussion channels you would like to exempt from being purged.\n\n"
    "NOTE!!: that it is recommended to use option 1 first to avoid listing too many channels.")

    setup_desc = ("Prompts user to setup the configuration file. Be sure to use option zero first.")

    readconfig_desc = ("Prints out the configuration file for verification of proper setup.")

    archive_desc = ("Uses the config file to archive all channels identified to be archived in the config file.")

    archive_descc = ("Only archives the category supplied by the user to the archive channel mapped in the config file.")

    purge_desc = ("Purges all channels identified in the config file as safe to purge.")

    prige_descc = ("Only purges the category or channel supplied by the user. Channels whitelisted will be ignored. ")

    embed = Embed(title='Meowwww!', description= desc, color=0x8A2BE2)
    embed.add_field(name="Commands:", value="-----------", inline=True)
    embed.add_field(name="/setup", value=setup_desc, inline=False)
    embed.add_field(name="/readconfig", value=readconfig_desc, inline=False)
    embed.add_field(name="/archive", value=archive_desc, inline=False)
    embed.add_field(name="/archive <category>", value=archive_descc, inline=False)
    embed.add_field(name="/purge", value=purge_desc, inline=False)
    embed.add_field(name="/purge <category> or <channel>", value=prige_descc, inline=False)
    await ctx.send(embed=embed)




@discord_client.command()
async def setup(ctx):
    if authorized(ctx.message.author.roles):
        pass
    else:
        await ctx.send("Sorry, you don't have permission to use this.")
        return

    # collect all the categories and ask if there is any they want to add
    category_list = discord_client.guilds[0].categories
    
    abort_loop = True
    for i in category_list:
        if i.name.upper() == 'ARCHIVES':
            abort_loop = False
    
    if abort_loop:
        await ctx.send("ERROR: Please create a category named 'ARCHIVE'. Please see /help")
        return
        
    def inter(msg):
        if msg.content in ['1', '2', 'q', 'Q']:
            return True
        else:
            return False
        
    # Way to control the options chosen by the user
    categorize = False
    exclusionize = False

    # Ask to set up either category or exclusions 
    await ctx.send("Would you like to setup your discord categories or exclusions?")
    await ctx.send("```Categories:    1 <-- Rec First``````Exclusions:    2``````Quit:          q```")
    msg = await discord_client.wait_for('message', check = inter)
    if msg.content.lower() == 'q':
        await ctx.send("Aborting.")
        return
    elif msg.content == '1':
        categorize = True
    elif msg.content == '2':
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

        # Remove archives as a possible category
        for i,e in enumerate(category_list):
            if e.name == 'ARCHIVES':
                category_list.pop(i)
                break

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
        msg = "**Please select the categories that will be flagged as war channels.**\nUse space seperated integers."
        async with ctx.typing():
            await ctx.send(msg)
            await ctx.send(output)
        msg = await discord_client.wait_for('message')

        # Actual selection list
        selection = []
        for num in msg.content.split(' '):
            if num.isdigit() == False:
                await ctx.send("Input error detected. One of the inputs was not a integer. Exiting.")
                return
            elif num.isdigit():
                if int(num) >= len(category_list):
                    await ctx.send("Input error detected. One of the inputs is not within the range of allowed inputs. Aborting.")
                    return
                else:
                    selection.append(num)
        
        # Add exclusions to the config file and map them to a channel under the archives channel
        archive_channels = []
        for i in discord_client.guilds[0].by_category():
            if isinstance(i[0], discord.channel.CategoryChannel):
                if i[0].name.upper() == 'ARCHIVES':
                    for j in i[0].channels:
                        archive_channels.append(j.name)
        
        if len(archive_channels) == 0:
            await ctx.send("You must create channels under ARCHIVES.")
            return

        # Calculate the space to add when printing
        char_length = 0
        for channel in archive_channels:
            if len(channel) > char_length:
                char_length = len(channel)

        # Set up printing variable
        output = ''
        space = ' '
        for index, channel in enumerate(archive_channels):
            space_calc = char_length - len(channel)
            space_calc += 2
            output += "```{}: {} {}```".format(channel, (space * space_calc), index)

        for num in selection:
            msg = "**Please select the channel you would like to map ***{}*** to**".format(category_list[int(num)].name)
            await ctx.send(msg)
            await ctx.send(output)
            msg = await discord_client.wait_for('message')
            if msg.content.isdigit():
                if int(msg.content) >= len(archive_channels):
                    await ctx.send("Input error detected. One of the inputs is not within the range of allowed inputs. Aborting.")
                    return
                else:
                    config.set('categories',category_list[int(num)].name, archive_channels[int(msg.content)])
            else:
                await ctx.send("Input error detected. Inputs must be integers that correspond to the values presented to you.")
                return

        # write the config file to disc
        with open('KittyLitterConfig.ini', 'w') as f:
            config.write(f)
        
        await ctx.send("Categories set. You can verify with /readconfig or run /setup again for exclusions.\n\n\n")
############################################################################################################ -- > categories
############################################################################################################ -- > exclusions
    if exclusionize == False:
        await ctx.send("Would you like to continue the setup process with exclusions? You can do this later. (Yes/No)")
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
    
    warchannels.append("archives")
    print(warchannels)   
    
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
            await ctx.send("Input error detected. One of the inputs was not a integer. Aborting.")
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


@discord_client.command()
async def readconfig(ctx):
    if authorized(ctx.message.author.roles):
        pass
    else:
        await ctx.send("Sorry, you don't have permission to use this.")
        return

    async with ctx.typing():
        if 'exclusions' in config.sections():
            if len(config['exclusions'].keys()) > 0:
                await ctx.send("**Current Exclusions:**")
                output = "```|{}|```".format("Channel")
                for i in config['exclusions'].keys():
                    output += "```{}```".format(i)
                await ctx.send(output)
            else:
                await ctx.send("There are no exclusion channels set. Please use /setup")
        else:
            await ctx.send("There are no exclusion channels set. Please use /setup")


        if 'categories' in config.sections():
            if len(config['categories'].keys()) > 0:
                space = '      '
                await ctx.send("**Current Categories Identified:**")
                output = "```|{}| {} |{}|```".format("Category", space, "Mapped To")        
                for key,value in config['categories'].items():
                    output += "```{} --> {}```".format(key.upper(), value)
                await ctx.send(output)
            else:
                await ctx.send("There are no exclusion channels set. Please use /setup")
        else:
            await ctx.send("There are no exclusion channels set. Please use /setup")
    

@discord_client.command()
async def archive(ctx):

    if authorized(ctx.message.author.roles):
        pass
    else:
        await ctx.send("Sorry, you don't have permission to use this.")
        return

    # check for the config file
    if 'exclusions' in config.sections():
        if len(config['exclusions'].keys()) < 1:
            await ctx.send("There are no exclusion channels set. Would you like to continue without setting up exclusions? (Yes/No)")
            msg = await discord_client.wait_for('message', check=yesno_check)
            if msg.content.lower() == 'no':
                await ctx.send("Very well. You can use /setup to set up those exclusion files.")
                return
            elif msg.content.lower() =='yes':
                print("hello")
                pass
            else:
                await ctx.send("Input error. Aborting.")

        # Check if they're doing a archive all or archive a channel
        if len(ctx.message.content.split(' ')) == 1:
            #game = discord.Game("with cat nip~")
            activity = discord.Activity(type = discord.ActivityType.watching, name="the archives")
            await discord_client.change_presence(status=discord.Status.dnd, activity=activity)
            async with ctx.typing():
                # Retrive the archive channels
                for key, value in config['categories'].items():                             
                    for cat_obj in discord_client.guilds[0].categories:                    
                        if cat_obj.name.upper() == key.upper():
                            dest_channel = get_channel(value)                             
                            for channel_obj in cat_obj.channels:
                                await ctx.send("Archiving: {}".format(channel_obj.name))
                                await dest_channel.send("```.```")
                                await dest_channel.send("```Archiving from: {}```".format(channel_obj.name))
                                await dest_channel.send("```.```")
                                async for message in channel_obj.history(limit=10000, reverse = True, after = datetime.datetime.utcnow() - datetime.timedelta(days=50)):
                                    send_message = "**[{}]** {}".format(message.author, message.clean_content)
                                    files = []
                                    if message.attachments:
                                        async with aiohttp.ClientSession() as session:
                                            for attachment_obj in message.attachments:
                                                async with session.get(attachment_obj.url) as resp:
                                                    buffer = io.BytesIO(await resp.read())
                                                    files.append(discord.File(fp=buffer, filename=attachment_obj.filename))
                                    files = files or None
                                    await dest_channel.send(send_message, files=files)
                        else:
                            continue 
            game = discord.Game("with cat nip~")
            activity = discord.Activity(type = discord.ActivityType.online, name=game)           
            await ctx.send("All done!")                     
            return
        if len(ctx.message.content.split(' ')) == 2 or len(ctx.message.content.split(' ')) == 3:
            valid = False
            dest_str = ''
            cat_str = ' '.join(ctx.message.content.split(' ')[1:])
            for key,value in config['categories'].items():
                if key.lower() == cat_str.lower():
                    valid = True
                    dest_str = value
                else:
                    continue

            if valid == False:
                await ctx.send("Must supply a valid category. Please see /help")
                return

            if valid:
                activity = discord.Activity(type = discord.ActivityType.watching, name="the archives")
                await discord_client.change_presence(status=discord.Status.dnd, activity=activity)
                async with ctx.typing():
                # Retrive the archive channels                           
                    for cat_obj in discord_client.guilds[0].categories:                    
                        if cat_obj.name.upper() == cat_str.upper():
                            dest_channel = get_channel(dest_str)                             
                            for channel_obj in cat_obj.channels:
                                await ctx.send("Archiving: {}".format(channel_obj.name))
                                await dest_channel.send("```.```")
                                await dest_channel.send("```Archiving from: {}```".format(channel_obj.name))
                                await dest_channel.send("```.```")
                                async for message in channel_obj.history(limit=10000, reverse = True, after = datetime.datetime.utcnow() - datetime.timedelta(days=50)):
                                    send_message = "**[{}]** {}".format(message.author, message.clean_content)
                                    files = []
                                    if message.attachments:
                                        async with aiohttp.ClientSession() as session:
                                            for attachment_obj in message.attachments:
                                                async with session.get(attachment_obj.url) as resp:
                                                    buffer = io.BytesIO(await resp.read())
                                                    files.append(discord.File(fp=buffer, filename=attachment_obj.filename))
                                    files = files or None
                                    await dest_channel.send(send_message, files=files)
                        else:
                            continue 
                game = discord.Game("with cat nip~")
                await discord_client.change_presence(status=discord.Status.online, activity=game)          
                await ctx.send("All done!")
                return  


@discord_client.command(aliases=['purge','clearall'])
async def purrrge(ctx):
    if authorized(ctx.message.author.roles):
        pass
    else:
        await ctx.send("Sorry, you don't have permission to use this.")
        return

    # check for the config file
    if 'exclusions' in config.sections():
        if len(config['exclusions'].keys()) < 1:
            await ctx.send("There are no exclusion channels set, would you like to continue anyways? (Yes/No)")
            msg = await discord_client.wait_for('message', check = yesno_check)
            if msg.content.lower() == 'no':
                ctx.send("Aborting.")
                return
            else:
                pass
    # list exclusion files
    await ctx.send("**Current Exclusions:**")
    output = ' '
    space = '      '
    for i in config['exclusions'].keys():
        output += "```{} {}```".format(space, i)
    await ctx.send(output)

    # ask for comfirmation
    await ctx.send("Exclusion channels are currently set to the list above. Would you like to continue? (Yes/No)")
    msg = await discord_client.wait_for('message', check=yesno_check)
    if msg.content.lower() == 'no':
        await ctx.send("Aborting.")
        return
    elif msg.content.lower() == 'yes':  # This is where you left off, can't print shit
        pass


    if len(ctx.message.content.split(' ')) == 1:
        desc = ("I will now begin to purge all the channels under the war channels identified in /readconfig. Please "
        "be sure to have archived the files before continuing. This cannot be undone. Would you like to proceed? \n\nplease type: KittyLitterBot")
        await ctx.send(embed = Embed(title='WARNING!', description= desc, color=0xFF0000)) 
        
        msg = await discord_client.wait_for('message')
        if msg.content != 'KittyLitterBot':
            await ctx.send("You seem unsure. Going to abort.")
            return
        else:
            pass

        activity = discord.Activity(type = discord.ActivityType.watching, name="messages getting nuked")
        await discord_client.change_presence(status=discord.Status.dnd, activity=activity)
        async with ctx.typing():
            for key in config['categories'].keys():
                for cat_obj in discord_client.guilds[0].categories:
                    if cat_obj.name.upper() == key.upper():
                        for channel_obj in cat_obj.channels:
                            deleted = await channel_obj.purge(bulk=True)
                            await ctx.send("Deleted {} message(s) from {}".format(len(deleted), channel_obj.name))
        
        game = discord.Game("with cat nip~")
        await discord_client.change_presence(status=discord.Status.online, activity=game)                       
        await ctx.send("All done!")
        return

    if len(ctx.message.content.split(' ')) == 2 or len(ctx.message.content.split(' ')) == 3:
        valid = False
        cat_str = ' '.join(ctx.message.content.split(' ')[1:])
        for key in config['categories'].keys():
            if key.lower() == cat_str.lower():
                valid = True
            else:
                continue

        channel_ob = ''
        if valid == False:
            for channel_obj in discord_client.get_all_channels():
                if channel_obj.name.lower() == cat_str:
                    channel_ob = channel_obj
                    valid = True
                else: 
                    continue

        if valid == False:
            await ctx.send("Could not identify user input as either a category or channel. Aborting.")
            return

        if valid:
            desc = ("I will not purge {}. This can not be undone. Please be sure to have archived this "
            "channel before proceeding. \n\nplease type to purge: KittyLitterBot".format(channel_ob.name))
            await ctx.send(embed = Embed(title='WARNING!', description= desc, color=0xFF0000)) 
            
            msg = await discord_client.wait_for('message')
            if msg.content != 'KittyLitterBot':
                await ctx.send("You seem unsure. Going to abort.")
                return
            else:
                pass
            deleted = await channel_ob.purge(bulk=True)
            await ctx.send("Deleted {} message(s) from {}".format(len(deleted), channel_ob.name))
        
        game = discord.Game("with cat nip~")
        await discord_client.change_presence(status=discord.Status.online, activity=game)                       
        await ctx.send("All done!")
        return
            
            

if __name__ == "__main__":
    discord_client.run(config['KittyLitter Configuration']['token'])

    