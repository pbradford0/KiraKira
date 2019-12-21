import discord
import os
import pendulum
import asyncio
import math
from event import major_event,task_event
from discord.ext import commands
from keep_alive import keep_alive

bot = commands.Bot(command_prefix='>', self_bot=False)
#organization improvements:
#set up variables for point names and such
#december calendar issues
#major operation / minor operation

minor_start = pendulum.datetime(2019, 4, 26, 0, tz='US/Pacific')
minor_end = pendulum.datetime(2019, 5, 15, 23, 59, tz='US/Pacific')
major_start = pendulum.datetime(2019, 4, 26, 0, tz='US/Pacific')
major_end = pendulum.datetime(2019, 5, 15, 23, 59, tz='US/Pacific')
major_event_name = 'Virtual Connection Synchronicity'
major_PT = 'Kizuna Points'
major_PT_dmission = 700
major_PT_total = 48450
major_farm_PT = 120
major_black_PT = 600
minor_event_name = 'Operation: Manjuu'
minor_event_PT = 'Chirps'
daily_reset = '07:00'


# Initialize
#@bot.event
#async def on_ready():
#  print('Bot online.')
#  print(bot.user)


#async def daily():
#  await bot.wait_until_ready()
#  #post the report, but only at daily reset time
#  while (True):
#    the_time = pendulum.now().strftime('%H:%M')
#    if the_time == daily_reset:
#      # update today's date and dates on remaining events
#      todays_date = pendulum.now('US/Pacific')
#      minor_days = minor_end.day_of_year - todays_date.day_of_year + 1
#      major_days = major_end.day_of_year - todays_date.day_of_year + 1
#      # generate the report detailing event info
#      report = generate_daily_report(todays_date,minor_days,major_days)
#      #now drop it in the bot spam channel
#      await bot.get_guild(139255063787864064).get_channel(572674736283189248).send(content=None, embed=report)
#    await asyncio.sleep(60)


# !test command, should just say beep
#@bot.command()
#async def test(beep):
#  await beep.send(pendulum.now().format('ddd[,] MMM Do[,] H[:]mm zz'))


# test object for testing new features
#@bot.command()
#async def exercise(beep):
#  friend = beep.author
#  await beep.send('What do you need, ' + friend.mention + '?', delete_after=10)

@bot.command()
async def manualreport(beep):
  #refresh variables for the date
  todays_date = pendulum.now('US/Pacific')
  minor_days = minor_end.day_of_year - todays_date.day_of_year + 1
  major_days = major_end.day_of_year - todays_date.day_of_year + 1
  #generate the report
  report = generate_daily_report(todays_date,minor_days,major_days)
  #now drop it in the bot spam channel
  #fix that: send to ctx's channel instead
  await bot.get_guild(139255063787864064).get_channel(572674736283189248).send(content=None, embed=report)


@bot.command()
async def points(ctx,pt):
  #catch bad inputs
  try:
    pt=int(pt)
  except ValueError:
    await ctx.send(ctx.author.mention + ', \"' + str(pt)+'\" cannot be the number of points you have. The correct usage of this command looks like this :'+
      ' *(replace 2000 with your point count)*  \n`>>points 2000`')
    return


@bot.command()
async def kizuna_points(ctx, pt):
 # kage is going to try to break this, like a total kage
  try:
    pt=int(pt)
  except ValueError:
    await ctx.send(ctx.author.mention + ', \"' + str(pt)+'\" cannot be the number of points you have. The correct usage of this command looks like this :'+
      ' *(replace 2000 with your point count)*  \n`>>points 2000`')
    return

  todays_date = pendulum.now('US/Pacific')
  major_days = major_end.day_of_year - todays_date.day_of_year + 1
  pt_remaining_at_end = (major_PT_total - (pt + (major_PT_dmission * (major_days-1))))
  pt_remaining_at_end_black = pt_remaining_at_end - (major_black_PT * (major_days-1))
  pt_total_now_daily = pt + (major_PT_dmission * (major_days-1))
  pt_total_now_daily_black = pt_total_now_daily + (major_black_PT * (major_days-1))
  maps_farmed = max(0,int(math.ceil(pt_remaining_at_end / major_farm_PT)))
  maps_farmed_black = max(0,int(math.ceil(pt_remaining_at_end_black / major_farm_PT )))
  maps_farmed_lazy = max(0,int(math.ceil((pt_remaining_at_end - 9300) / major_farm_PT)))
  maps_farmed_black_lazy = max(0,int(math.ceil((pt_remaining_at_end_black - 9300) / major_farm_PT )))
  
  # generate a default report if none of the if-cases go through
  points_report = discord.Embed(
      title = 'Commander, we need to have a talk.',
      description = 'You already have enough ' + major_PT + ' to clear out the event shop. What do you need a report from me for?'
    )

  # a good secretary omits irrelevant information
  if (maps_farmed_black_lazy > 0):
    points_report = discord.Embed(
      title = 'Commander, here is your report.',
      description = '**' + str(major_days) + ' days** remain for ' + str(major_event_name) +
      '.\nClearing out the event shop costs ' + str(major_PT_total) + ' ' + major_PT + '. \n' +
      'Completing all of the remaining daily missions brings your final-day total from ' + str(pt) + '  to *' + str(pt_total_now_daily) + ' ' + major_PT +
      '.*\n Completing Black-SP daily, in addition to your missions, will bring your final-day total to *' + str(pt_total_now_daily_black) + ' ' + major_PT +
      '.*\n\n In order to buy out the full event shop, you will need to clear SP4 **' + str(maps_farmed) + ' times** *if you skip or cannot complete Black-SP*' +
      '.\n Clearing both your missions and Black-SP daily reduces your SP4 clear count to **' + str(maps_farmed_black) + ' times**'
      '.\n You can save 9300 ' + major_PT + ' by not purchasing the T4 Tech Packs or T3 Parts, reducing your number of SP4 clears required' +
      '.\n You will only need to clear **' + str(maps_farmed_lazy) + ' times** for daily missions only, or **' + str(maps_farmed_black_lazy) + ' times** if you ' +
      'also clear Black-SP.'
    )
  if (maps_farmed_black_lazy == 0 and maps_farmed_lazy > 0):
    points_report = discord.Embed(
      title = 'Commander, here is your report.',
      description = '**' + str(major_days) + ' days** remain for ' + major_event_name +
      '.\nClearing out the event shop costs ' + str(major_PT_total) + ' ' + major_PT + '. \n' +
      'Completing all of the remaining daily missions brings your final-day total from ' + str(pt) + '  to *' + str(pt_total_now_daily) + ' ' + major_PT +
      '.*\n Completing Black-SP daily, in addition to your missions, will bring your final-day total to *' + str(pt_total_now_daily_black) + ' ' + major_PT +
      '.*\n\n In order to buy out the full event shop, you will need to clear SP4 **' + str(maps_farmed) + ' times** *if you skip or cannot complete Black-SP*' +
      '.\n Clearing both your missions and Black-SP daily reduces your SP4 clear count to **' + str(maps_farmed_black) + ' times**'
      '.\n You can save 9300 ' + major_PT + ' by not purchasing the T4 Tech Packs or T3 Parts, reducing your number of SP4 clears required' +
      '.\n You will only need to clear **' + str(maps_farmed_lazy) + ' times** for daily missions only' +
      '. Completing daily missions and Black-SP will mean that you are official finished with ' + major_event_name + '! Congratulations, Commander!'
    )
  if (maps_farmed_lazy == 0 and maps_farmed_black > 0):
    points_report = discord.Embed(
      title = 'Commander, here is your report.',
      description = '**' + str(major_days) + ' days** remain for ' + str(major_event_name) +
      '.\nClearing out the event shop costs ' + str(major_PT_total) + ' ' + major_PT + '. \n' +
      'Completing all of the remaining daily missions brings your final-day total from ' + str(pt) + '  to *' + str(pt_total_now_daily) + ' ' + major_PT +
      '.*\n Completing Black-SP daily, in addition to your missions, will bring your final-day total to *' + str(pt_total_now_daily_black) + ' ' + major_PT +
      '.*\n\n In order to buy out the full event shop, you will need to clear SP4 **' + str(maps_farmed) + ' times** *if you skip or cannot complete Black-SP*' +
      '.\n Clearing both your missions and Black-SP daily reduces your SP4 clear count to **' + str(maps_farmed_black) + ' times**'
      '.\n Completing daily missions and Black-SP will mean that you are official finished with ' + major_event_name + '! Congratulations, Commander!'
    )
  if (maps_farmed_black == 0 and maps_farmed > 0):
    points_report = discord.Embed(
      title = 'Commander, here is your report.',
      description = '**' + str(major_days) + ' days** remain for ' + str(major_event_name) +
      '.\nClearing out the event shop costs ' + str(major_PT_total) + ' ' + major_PT + '. \n' +
      'Completing all of the remaining daily missions brings your final-day total from ' + str(pt) + '  to *' + str(pt_total_now_daily) + ' ' + major_PT +
      '.*\n Completing Black-SP daily, in addition to your missions, will bring your final-day total to *' + str(pt_total_now_daily_black) + ' ' + major_PT +
      '.*\n\n In order to buy out the full event shop, you will need to clear SP4 **' + str(maps_farmed) + ' times** *if you skip or cannot complete Black-SP*' +
      '.\n Completing daily missions and Black-SP, however, will mean that you are official finished with ' + major_event_name + '! Congratulations, Commander!'
    )
  if (maps_farmed == 0 and pt_total_now_daily_black >= major_PT_total ):
    points_report = discord.Embed(
      title = 'Commander, here is your report.',
      description = '**' + str(major_days) + ' days** remain for ' + str(major_event_name) +
      '.\nClearing out the event shop costs ' + str(major_PT_total) + ' ' + major_PT + '. \n' +
      'Completing all of the remaining daily missions brings your final-day total from ' + str(pt) + '  to *' + str(pt_total_now_daily) + ' ' + major_PT +
      '.*\n Completing Black-SP daily, in addition to your missions, will bring your final-day total to *' + str(pt_total_now_daily_black) + ' ' + major_PT +
      '.*\n Completing daily missions and Black-SP will mean that you are official finished with ' + major_event_name + '! Congratulations, Commander!'
    )
    if (maps_farmed == 0 and pt_total_now_daily >= major_PT_total):
      points_report = discord.Embed(
        title = 'Commander, here is your report.',
        description = '**' + str(major_days) + ' days** remain for ' + str(major_event_name) +
        '.\nClearing out the event shop costs ' + str(major_PT_total) + ' ' + major_PT + '. \n' +
        'Completing all of the remaining daily missions brings your final-day total from ' + str(pt) + '  to *' + str(pt_total_now_daily) + ' ' + major_PT +
        '.*\n Completing daily missions will mean that you are official finished with ' + major_event_name + '! Congratulations, Commander!'
      )
    if (pt > major_PT_total):
      points_report = discord.Embed(
      title = 'Commander, we need to have a talk.',
      description = 'You already have enough ' + major_PT + ' to clear out the event shop. What do you need a report from me for?'
      )
  await ctx.send(content=None, embed=points_report)
#normal and hard versions for B3 vs D3
#set variables for the highest lv farmable map


def generate_daily_report(todays_date,minor_days,major_days):
  #some improvements need to be made to report generation
  #pvp season information needs to be calculated, 15 day chunks
  #perhaps it's best to reserve reporting pvp in the daily report for, let's say...
  #first day, AotN day, last day
  #last day before core shop reset
  #last day befpre token shop removal
  #there'll be a negative days remaining issue in december
  #is there a way to automatically

  #get the list fresh
  data = open('events_list.txt','r')
  events_list = []
  for line in data:
    events_list.append(line)
  data.close()
  events_list = process_events_list(events_list)


  report = discord.Embed(
    title = 'Good morning, Commanders!',
    description = 'Here is your report for *' +
    todays_date.format('ddd[,] MMM Do[,] H[:]mm zz') + '* (Server Time.)'
  )
  report.add_field(
    name = 'Operation: Manjuu',
    value = 'Begins: *' + minor_start.format('ddd[,] MMM Do[,] H[:]mm zz') + '*\n  Ends: *' +
    minor_end.format('ddd[,] MMM Do[,] H[:]mm zz') + '.* \n**' + str(minor_days) +
    ' days remain**, including today. Starting *May 5th, after maintenance*, all Chirp clear drops will be increased by 50%.'
  )
  report.add_field(
    name = major_event_name,
    value = 'Begins: *' + major_start.format('ddd[,] MMM Do[,] H[:]mm A zz') + '*\n Ends:*' +
    major_end.format('ddd[,] MMM Do[,] H[:]mm A zz') + '.* \n**' + str(major_days) +
    ' days remain**, including today.\n Daily missions grant 700 ' + str(major_PT) + '/day, granting a total of *'
    + str(major_PT_dmission * major_days) + ' Kizuna Points*. Black-SP provides 600 Kizuna Points/day, for a total of *'
    + str(600 * major_days) + ' ' + str(major_PT) +'*. Together, you may gain **' + str(1300 * major_days) +
    ' Kizuna Points** from daily missions and Black-SP by the end of the event.'
  )
  return report

def process_events_list(raw_list):
  processed_list = []
  for line in raw_list:
    # [name] starting[y][m][d] ending[y][m][d] is the order of events_list.txt
    event_deets = line.split()
    start_date = pendulum.datetime(event_deets[2], event_deets[3], event_deets[4], 0, tz='US/Pacific')
    end_date = pendulum.datetime(event_deets[5], event_deets[6], event_deets[7], 0, tz='US/Pacific')
    processed_list.append(event(event_deets[0],start_date,end_date))
  for line in 
  return processed_list

keep_alive()
bot.loop.create_task(daily())
token = os.environ.get('DISCORD_BOT_SECRET')
bot.run(token)