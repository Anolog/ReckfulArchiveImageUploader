import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the Discord token from environment variables
discord_token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

#Temp data storage
pending_approvals = {}

class Submission:
    def __init__(self, user, image_url, title, tags, date, original_link):
        self.user = user
        self.image_url = image_url
        self.title = title
        self.tags = tags
        self.date = date
        self.original_link = original_link

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Command to handle image submissions
@bot.command(name='submit')
async def submit(ctx, title: str, tags: str, date: str, original_link: str):
    print("Received !submit command")  # Debug statement
    if len(ctx.message.attachments) > 0:
        image_url = ctx.message.attachments[0].url
        submission = Submission(ctx.author, image_url, title, tags, date, original_link)
        message = await ctx.send(
            f"New submission by {ctx.author.mention}\nTitle: {title}\nTags: {tags}\nDate: {date}\nOriginal Link: {original_link}\nImage: {image_url}"
        )
        pending_approvals[message.id] = submission
        await message.add_reaction('✅')
        await message.add_reaction('❌')
    else:
        await ctx.send("Please attach an image to your submission.")

# Event to handle reactions to submissions
@bot.event
async def on_reaction_add(reaction, user):
    # Ignore the bot's own reactions
    if user == bot.user:
        return

    print(f"Reaction added by {user.name}: {reaction.emoji}")  # Debug statement

    # Check if the message is in pending approvals and if the user has the required permissions
    if reaction.message.id in pending_approvals and user.guild_permissions.manage_messages:
        submission = pending_approvals.pop(reaction.message.id)  # Remove from pending approvals immediately

        # Process approval
        if reaction.emoji == '✅':
            await reaction.message.channel.send(f"Submission by {submission.user.mention} approved.")
            # Code to store the data locally or send to web server goes here

        # Process denial
        elif reaction.emoji == '❌':
            await reaction.message.channel.send(f"Submission by {submission.user.mention} denied.")

        # Optional: Remove reactions from the message to indicate it's been processed
        await reaction.message.clear_reactions()

bot.run(token=discord_token)