import discord
from discord.ext import commands
import os, time
import requests, datetime, logging, asyncio
from dotenv import load_dotenv


load_dotenv()

# Create and configure logger
logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger()
 
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

CHANNEL_ID = 1223752579125608568
TEST_CHANNEL = 1218391871324164189
DISCORD_TOKEN = os.getenv('TOKEN')
TEST_DICTIONARY = {
    "Fajr": "06:00",
    "Dhuhr": "12:00",
    "Asr": "17:00",
    "Maghrib": (time.ctime(time.time())).split(" ")[4][:-3],
    "Isha": "22:00"
    }

bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())

@bot.tree.command(name="prayer", description="Alerts you the prayer times for a specific city and country")
async def prayer(ctx, city: str, country: str):
    # Make the Prayer Time API call 
    response = requests.get("https://api.aladhan.com/v1/calendarByCity/" + str(datetime.date.today().year) + "/" + str(datetime.date.today().month) + "?city=" + city + "&country=" + country+ "&method=2")
    response = response.json()
    
    await ctx.response.send_message("You will receive prayer time notifications for {}, {}".format(city, country))
    # Set up the prayer_times dictionary
    prayer_times = populate_prayer_time_dict(response)
    # Continuesly check prayer time
    await check_prayer_time(prayer_times, CHANNEL_ID)

@bot.event
async def on_ready():
    await bot.tree.sync()
    logging.debug(f"Logged in as {bot.user.name}")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("The Islamic Bot is live! \nUse /prayer to get prayer notifications for a specific city")
    logging.debug("Bot to user: \"The Islamic Bot is live! \nUse /prayer to get prayer notifications for a specific city\"")
    
        
'''
This function will check if prayer time has reached and send a message to the guild.
'''
async def check_prayer_time(prayer_time_dict, channel_id):
    channel = bot.get_channel(channel_id)
    while True:
        await asyncio.sleep(60)
        # Get the current time and split the resulting string to a list to get the time
        current_time = (time.ctime(time.time())).split(" ")
        # This will get the 4th element which is the current time and remove the seconds
        current_time = current_time[4][:-3]
        logging.debug("Current Time: {}".format(current_time))
        logging.debug("current_time in Prayer Time Dictionary: {}".format(current_time in list(prayer_time_dict.values())))

        # Check if the prayer time has been reached.
        for prayer, prayertime in prayer_time_dict.items():
            if current_time == prayertime:
                Embed = discord.Embed(
                    colour=discord.Colour.random(),
                    description= "It is {} prayer time! Get ready to pray!".format(prayer),
                    title="Prayer Time 🕌"
                )
                # Add the author's name to the embed
                Embed.set_author(name = "Islamic Bot")
                Embed.set_image(url="https://cdn.discordapp.com/attachments/1224226488614654052/1224226673436921918/praying.jpg?ex=661cb8ef&is=660a43ef&hm=9e98f770de3cd4858e01c6b9261def1dd4812fa169ca87039a9104a4f3bccc3e&")
                Embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/1224226488614654052/1224389168595996703/pic.jpg?ex=661d5045&is=660adb45&hm=bc9cdd7156d8fa40d01f232f4c7d2698b5a4612a0541f5192d53c279f263bb31&")
                Embed.add_field(name="Prayer", value=prayer)
                Embed.add_field(name="Time of Prayer", value=prayertime)
                await channel.send(embed=Embed)
                print("Message sent!")

'''
This function will populate our PRAYER_TIME_DICT with the correct information
'''
def populate_prayer_time_dict(response):
    # Create a Dictionary with the values I need. Use Split to remove the "EDT" from the time
    PRAYER_TIME_DICT = {}
    PRAYER_TIME_DICT["Fajr"] = response["data"][datetime.date.today().day]["timings"]["Fajr"].split(" ")[0]
    PRAYER_TIME_DICT["Dhuhr"] = response["data"][datetime.date.today().day]["timings"]["Dhuhr"].split(" ")[0]
    PRAYER_TIME_DICT["Asr"] = response["data"][datetime.date.today().day]["timings"]["Asr"].split(" ")[0]
    PRAYER_TIME_DICT["Maghrib"] = response["data"][datetime.date.today().day]["timings"]["Maghrib"].split(" ")[0]
    PRAYER_TIME_DICT["Isha"] = response["data"][datetime.date.today().day]["timings"]["Isha"].split(" ")[0]

    return PRAYER_TIME_DICT

bot.run(DISCORD_TOKEN)


