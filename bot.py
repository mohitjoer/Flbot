import discord
from discord.ext import commands
from groq import Groq
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Define sensitive information (API keys)
DISCORD_BOT_TOKEN = "MTMyMjU4Nzg4NzgxMTY5MDU4OQ.GEn8Cd.VgJsLfkwhQNDHlfwmkgfmng-CubsbifGXFsNM8"
GROQ_API_KEY = "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"

# Initialize the Groq client
client = Groq(api_key=GROQ_API_KEY)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

conversations = {}

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}')
    logging.info('Bot is ready and connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    channel_id = message.channel.id

    # Initialize conversation state if not present
    if channel_id not in conversations:
        conversations[channel_id] = {"messages": [{"role": "system", "content": "You are a helpful assistant."}]}

    conversation = conversations[channel_id]

    # Handle bot mention
    if bot.user in message.mentions:
        try:
            conversation["messages"].append({"role": "user", "content": message.content})

            # Send request to Groq
            completion = client.chat.completions.create(
                model="gemma2-9b-it",
                messages=conversation["messages"],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
            )

            ai_response = completion.choices[0].message.content
            conversation["messages"].append({"role": "assistant", "content": ai_response})

            # Send response in chunks
            def split_into_chunks(text, chunk_size=2000):
                return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

            response_chunks = split_into_chunks(ai_response)
            for chunk in response_chunks:
                await message.channel.send(chunk)

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            await message.channel.send("An error occurred while processing your request. Please try again later.")

    # Allow command processing to work
    await bot.process_commands(message)

bot.run(DISCORD_BOT_TOKEN)
