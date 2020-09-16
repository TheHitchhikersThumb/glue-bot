import discord
import random
import pymongo
from pymongo import MongoClient

# Mongo Client
cluster = MongoClient("mongodb+srv://dylhit:qsi12345@gluecluster.kmn2g.mongodb.net/test")
db = cluster["GlueDatabase"]
collection = db["GlueCollection"]

# Setting up empty pots, boards, questions.
client = discord.Client()
pot = []
board_list = {}
question_list = {}
question_progress = {}

# Used to create a board display, for convenience.
def board_post(name):
    post_list = "```Board %s" % (name)
    count = 1
    for post in board_list[name]:
        post_list += "\n%s. %s" % (count, post)
        count += 1
    post_list += "```"
    return post_list

# Prints in console once Glue has logged on.
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message): # On ANY message.
    if message.author == client.user: # If Glue made the message being analyzed, there's no need to continue.
        return

    def pred(m):
        return m.author == message.author and m.channel == message.channel

    """
    if message.content.startswith('$y '):
        arg = message.content[3:]
        url = "https://www.youtube.com/results?search_query=%s" % (arg.replace(" ", "+"))
        html_content = urllib.request.urlopen(url)
        print(html_content)
        search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
        print(len(search_results))
        print("http://www.youtube.com/watch?v=" + search_results[0])

    if message.content.startswith("$advice"):
        await message.channel.send(random.choice(advice))
    """

    # Help
    if message.content.startswith("$help"):
        embedVar = discord.Embed(title="GlueBot Commands", description="To access this at any time, type `$help` in a channel with GlueBot.", color=0x5fabd7)
        embedVar.add_field(name = "Pot", value = "Typing `$pot your-message-here` will add your message to the Pot, a collection of anonymous users' posts. To get a message from the pot, type just `$pot`. **Each message can only be viewed once.**", inline = False)
        embedVar.add_field(name = "Board", value = "Typing `$b your-board` will let you view the Board of your choice. Each Board is a series of anonymous posts that stay there until removed. To add a post, type `$ab your-board your-message`. To remove a post, type `$rb your-board post-number`.", inline = False)
        embedVar.add_field(name = "Questions", value = "Typing `$aq your-question` will ask a question anonymously. Typing `$gq` will get a random unanswered question. People can either choose to answer it or skip it. **Answers are really sent to the question writer, and each question can only be answered once.**", inline = False)
        await message.channel.send(embed=embedVar)
    # Pot Functions
    if message.content.startswith("$p"):
        arg = message.content.split(' ', 1) # Splits the message into "$p", and the rest.
        if len(arg) < 2: # If the message is just "$p"...
            #try:
            pick = db.collection.find_one() # Picks a random message out of the pot.
            await message.channel.send("We fetched this from the pot:")
            await message.channel.send(pick)
            db.collection.delete_one({"post" : pick["post"]}) # Removes the message from the pot.
            #except: # If an error occurs.
                #await message.channel.send("Sorry, the pot is empty right now.")
        else: # If the message is "$p message..."
            pot.append(arg[1]) # The message is added. 
            await message.channel.send("Your message \"%s\" has been added." % (arg[1]))
            collection.insert_one({"post" : arg[1]})
    
    # Board Functions
    if message.content.startswith("$b"): # For viewing a Board.
        arg = message.content.split(' ', 1) # Splits the message into "$b", and the rest.
        if len(arg) < 2: # If the message is just "$b"...
            await message.channel.send("Try again with the name of your board plus your message, e.g. \"$b board_name\"")
        else: # If the message is "$b board_name"...
            try:
                if len(board_list[arg[1]]) == 0: # If there are no items in the board...
                    await message.channel.send("There's nothing on board %s right now." % (arg[1]))
                    return # Ends the function.
                await message.channel.send(board_post(arg[1])) # If there items in the board, the board name is sent to board_post().
            except: # If an error occurs.
                await message.channel.send("The board doesn't exist.")
    
    if message.content.startswith("$ab"): # For Adding to a Board.
        arg = message.content.split(' ', 2) # Splits the message into "$ab", "board_name", and the rest.
        if len(arg) < 3: # If the message is just "$ab" or just "$ab" and "board_name"... 
            await message.channel.send("Try again with the name of your board, e.g. \"$b board_name message\".")
            return # Ends the function.
        else: # If the message is "$ab board_name message"...
            try:
                board_list[arg[1]] # Tests to see if the Board exists. If not, an error should occur.
            except: # If the Board doesn't exist...
                board_list[arg[1]] = list() # A Board is created for it.
        try:
            board_list[arg[1]].append(arg[2]) # Adds the message to the Board.
            await message.channel.send("\"%s\" has been added to Board \"%s\"." % (arg[2], arg[1]))
        except: # If an error occurs...
            await message.channel.send("Oops, something went wrong. Maybe try again?")

    if message.content.startswith("$rb"): # For Removing from a Board.
        arg = message.content.split(' ', 2) # Splits the message into "$rb", "board_name", and the rest.
        if len(arg) < 3 or len(arg) > 3: # If the message is just "$rb" or just "$rb" and "board_name"... 
            await message.channel.send("Try again with the name of your board, e.g. \"$b board_name post_number\"")
        else: # If the message is "$ab board_name post_number"...
            try:
                board_list[arg[1]] # Checks if the Board exists. If not, it should return an error.
            except:
                await message.channel.send("Board \"%s\" doesn't exist." % (arg[1]))
                return # Ends the function.
        try:
            num = int(arg[2]) # Tests to see if the post_number is a number. If not, an error should occur.
            board_list[arg[1]].pop(num - 1) # Removes the post.
            await message.channel.send("Post %s successfully removed from Board \"%s\"." % (num, arg[1]))
        except: # If an error occurs...
            await message.channel.send("Your request wasn't a board number.")

    # Question Functions
    if message.content.startswith("$aq"): # For Asking a Question.
        try:
            arg = message.content.split(' ', 1) # Splits the message into "$aq", and the rest.
            if len(arg) < 2: # If the message is just "$aq"...
                await message.channel.send("Try again with your question, e.g. \"$aq question\".")
            else: # If the message is "$aq question"...
                while arg[1] in question_list: # If the question exists by coincidence in the question list...
                    arg[1] += " " # A space is added. If there are more, then a space continues to be added.
                question_list[arg[1]] = message.author # Marks the author as the value for the question for a reply.
                await message.channel.send("Your question \"%s\" was added. Let's hope somebody replies to it!" % (arg[1]))
        except: # If an error occurs...
                await message.channel.send("Oops, something went wrong. Maybe try again?")

    if message.content.startswith("$gq"): # For Getting a Question.
        try:
            if message.author in question_progress.keys():
                await message.channel.send("Your current question is:\n```%s```What do you think? Think of a reply, then send it with \"$rq your_reply\". Or, if you can't answer, reply with \"$sq\"." % (question_progress[message.author]))
                return
            pick = random.choice(list(question_list.keys())) # Picks a random question.
            await message.channel.send("An anonymous user asks:\n```%s```What do you think? Think of a reply, then send it with \"$rq your_reply\". Or, if you can't answer, reply with \"$sq\"." % (pick))
            finished = False # For the loop below.
            question_progress[message.author] = pick
            while finished == False: # The loop either ends with a proper "$rq" reply or a proper "$sq" reply.
                rep = await client.wait_for('message', check = pred) # Checks every message for an "$rq" or "$sq" message.
                if rep.content.startswith("$rq"): # For an "$rq" reply.
                    arg = rep.content.split(' ', 1) # Splits the reply into "$rq" and the rest.
                    if len(arg) < 2: # If the reply is just "$rq"...
                        await client.send(rep.channel, "Try again with your reply, e.g. \"$rq your_reply\"")
                        continue # The loop is not closed, so the bot continues looking for a reply.
                    reply = arg[1] # Sets the reply as the answer.
                    await message.channel.send("Your reply will be sent to the user. Thank you for participating!")
                    try:
                        await question_list[pick].create_dm() # Starts the DM with the person who asked the question.
                        await question_list[pick].dm_channel.send("---\nAn anonymous user has replied to your question:\n```%s```with the answer\n```%s```Hopefully the answer was good. Thank you for participating!" % (pick, reply))
                        question_list.pop(pick) # Removes the question.
                    except:
                        print("Something went wrong.") # If an error occurs, the question isn't removed, as it wasn't answered.
                    finished = True # The loop is ended.
                elif rep.content.startswith("$sq"): # For a "$sq reply."
                    await client.send(rep.channel, "Question skipped. Thank you for participating!")
                    finished = True # The loop is ended.
            question_progress.pop(message.author) # The author is removed and doesn't have to answer the question anymore.
        except:
            await message.channel.send("Oops, something went wrong. It's possible the question list may be empty. Try again?")
    
    """
    if message.content.startswith("$e"):
        try:
            arg = message.content.split(' ', 1) # Splits the message into "$aq", and the rest.
            if len(arg) < 2: # If the message is just "$aq"...
                await message.channel.send("Try again with your question, e.g. \"$e post\".")
            else:
                await message.channel.send("%s posted the opinion\n```%s```Vote :thumbsup: or :thumbsdown: to agree or disagree.")
                print(message.Reaction.count)
        except:
            await message.channel.send("Oops, something went wrong. Maybe try again?")
    """

print(discord.__version__)
client.run('NzUzMjg3ODM3ODgwOTQyNjIy.X1j_9w.2BPAtV8ve_T6stwFEwvCQf9uNiQ')