import discord
import asyncio
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Your Discord Bot Token
TOKEN = 'TOKEN'

# Website URL to scrape
URL = 'https://d4armory.io/events/'  # Replace with the actual URL you want to scrape

# Channel ID to send new data
CHANNEL_ID = 1234

# Global dictionary to store the previously gathered data for each section
previous_data = {
    'boss': {'name': '', 'spawn_time': '', 'expected_spawn_time': ''},
    'helltide': {'spawn_time': '', 'despawn_time': '', 'next_time': ''},
#    'legion': {'time': '', 'expected_time': ''}
}

# Generic settings to get bot running
chrome_options = Options()
chrome_options.add_argument('--headless')
intents = discord.Intents.default()
client = discord.Client(intents=intents)

def scrape_data(section):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)

    # Waits for the page to load and the dynamic content to be rendered
    driver.implicitly_wait(10)
    page_source = driver.page_source

    driver.quit()

    soup = BeautifulSoup(page_source, 'html.parser')

    if section == 'boss':
        boss_data = {
            'name': soup.find('div', id='bossName').text,
            'spawn_time': soup.find('div', id='bossSpawnTime').text,
            'expected_spawn_time': soup.find('div', id='expectedSpawnTime').text
        }
        return boss_data
    elif section == 'helltide':
        helltide_data = {
            'spawn_time': soup.find('div', id='helltideSpawnTime').text,
            'despawn_time': soup.find('div', id='helltideDespawnTime').text,
            'next_time': soup.find('div', id='helltideNextTime').text
        }
        return helltide_data
    #elif section == 'legion':
    #    legion_data = {
    #        'time': soup.find('div', id='legionTime').text,
    #        'expected_time': soup.find('div', id='expectedLegionTime').text
    #    }
    #    return legion_data

# Compare the latest scrape data with the previously gathered data for a specific section
def compare_data(section, latest_data):
    if latest_data != previous_data[section]:
        return True
    return False

# Function to send new data to the specified channel
async def send_new_data(channel, section, data):
    message = ''
    if section == 'boss':
        message = f"Boss: {data['name']}: Spawntime: {data['spawn_time']} - Next one expected at: {data['expected_spawn_time']}"
    elif section == 'helltide':
        message = f"Helltide: Spawntime {data['spawn_time']} - Despawn: {data['despawn_time']} - Next one expected at: {data['next_time']}"
    # elif section == 'legion':
    #    message = f"legion: time {data['time']} - expected {data['expected_time']}"

    await channel.send(message)

# Scrape loop to run every 20 minutes for a specific section
async def scrape_loop(section):
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    while not client.is_closed():
        latest_data = scrape_data(section)
        if compare_data(section, latest_data):
            await send_new_data(channel, section, latest_data)
            previous_data[section] = latest_data.copy()

        await asyncio.sleep(1200)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    sections = ['boss', 'helltide'] #, 'legion']
    for section in sections:
        asyncio.ensure_future(scrape_loop(section))

client.run(TOKEN)
