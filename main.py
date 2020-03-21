import discord
import os
import pendulum
import asyncio
import math
from event import event,pt_event
from discord.ext import commands
from keep_alive import keep_alive

bot = commands.Bot(command_prefix='>>', self_bot=False)
daily_reset = '00:00'

# initialize
@bot.event
async def on_ready():
  print('Bot online.')
  print(bot.user)

# !test123 command, should just say the date
@bot.command()
async def test123(beep):
  await beep.send('Today\'s day of year: ' + str(pendulum.now(tz='US/Pacific').day_of_year) + '\nDay of year of the 31st: ' + str(pendulum.date(2019, 5, 31).day_of_year))


@bot.command()
async def points(ctx,pt):
  #catch bad inputs
  try:
    pt=int(pt)
  except ValueError:
    await ctx.send(ctx.author.mention + ', something went wrong with your request. Please double-check and try again.' +
    + 'The correct usage of this command looks like this :*(replace 2000 with your point count)*  \n`>points 2000`')
    return
  # don't forget to assign 0 for black_pt if an event has no black / D0 map
  events_list = read_events_list()
  events_list = process_events_list(events_list)
  todays_date = pendulum.now('US/Pacific')
  events_points = read_events_points()
  events_points = process_events_points(events_points)
  current_events = []
  # create a list of current events
  found_match = False
  for line in events_list:
    if (todays_date >= line.start_date) and (todays_date <= line.end_date):
      current_events.append(line)
  for line in current_events:
    for line_pt in events_points:
      if line.name == line_pt.name:
        pt_event = line_pt
        pt_event.name = pt_event.name.replace('_', ' ')
        pt_event.event_pt = pt_event.event_pt.replace('_', ' ')
        event_date = line
        found_match = True
  if not found_match:
    points_report = discord.Embed(
      title = 'Commander, there is currently no operation involving points running.',
      description = 'Please take the time to get rest and catch up on any backlogged tasks.'
    )
    await ctx.send(content=None, embed=points_report)
    return
  # okay honestly, the rest of this is going to be a hecking mess, I'm just making my old code work for now
  major_event_name = pt_event.name
  major_PT = pt_event.event_pt
  major_farm_PT = pt_event.lastmap_pt
  major_PT_total = pt_event.shop_total_pt
  major_PT_dmission = pt_event.daily_mission_pt
  major_black_PT = pt_event.black_pt
  major_PT_total = pt_event.shop_total_pt
  major_PT_total_lazy = pt_event.shop_total_pt_lazy
  # acquire your cleanest math pants and equip them immediately
  major_days = event_date.end_date.day_of_year - todays_date.day_of_year + 1
  pt_remaining_at_end = (major_PT_total - (pt + (major_PT_dmission * (major_days-1))))
  pt_remaining_at_end_black = pt_remaining_at_end - (major_black_PT * (major_days-1))
  pt_remaining_at_end_lazy = (major_PT_total_lazy - (pt + (major_PT_dmission * (major_days-1))))
  pt_remaining_at_end_black_lazy = pt_remaining_at_end_lazy - (major_black_PT * (major_days-1))
  pt_total_now_daily = pt + (major_PT_dmission * (major_days-1))
  pt_total_now_daily_black = pt_total_now_daily + (major_black_PT * (major_days-1))
  maps_farmed = max(0,int(math.ceil(pt_remaining_at_end / major_farm_PT)))
  maps_farmed_black = max(0,int(math.ceil(pt_remaining_at_end_black / major_farm_PT )))
  maps_farmed_lazy = max(0,int(math.ceil((pt_remaining_at_end_lazy) / major_farm_PT)))
  maps_farmed_black_lazy = max(0,int(math.ceil((pt_remaining_at_end_black_lazy) / major_farm_PT )))

  # generate a default report if none of the if-cases go through
  points_report = discord.Embed(
      title = 'Commander, we need to have a talk.',
      description = 'You already have enough ' + major_PT + ' to clear out the event shop. What do you need a report from me for?'
    )
  
  points_report = discord.Embed(
    title = 'Commander, here is your report.',
    description = '**' + str(major_days) + ' days** remain for ' + str(major_event_name) +
    '.\nClearing out the event shop costs ' + str(major_PT_total) + ' ' + major_PT + '. \n' +
    'Completing each remaining daily missions brings your final-day total from ' + str(pt) + '  to *' + str(pt_total_now_daily) + ' ' + major_PT +
    '.*\n'
  )

  # cleaning up some of this code: using a string for value
  report_value = ''

  if (major_black_PT > 0):
    report_value = 'Completing daily missions will mean that you are official finished with ' + major_event_name + '! Congratulations, Commander!'
    if (maps_farmed == 0 and pt_total_now_daily >= major_PT_total):
      points_report.add_field(
        name = 'Your event plan:',
        value = report_value
        )

    elif (maps_farmed == 0 and pt_total_now_daily_black >= major_PT_total and pt_total_now_daily < major_PT_total ):
      report_value = 'Completing the Extra stage daily, in addition to your missions, will bring your final-day total to *' + str(pt_total_now_daily_black) + ' ' + major_PT
      + '.*\n Completing daily missions and the Extra stage will mean that you are official finished with ' + major_event_name + '! Congratulations, Commander!'
      points_report.add_field(
        name = 'Your event plan:',
        value = report_value
      )
    elif (maps_farmed_black == 0 and maps_farmed > 0):
      report_value = 'Completing the Extra stage daily, in addition to your missions, will bring your final-day total to *' + str(pt_total_now_daily_black) + ' ' + major_PT
      + '.*\n In order to buy out the full event shop, you will need to clear the final operation stage **' + str(maps_farmed) + ' times** *if you skip or cannot complete the Extra stage*' + '.\n Completing daily missions and the Extra stage, however, will mean that you are official finished with ' + major_event_name + '! Congratulations, Commander!'
      points_report.add_field(
        name = 'Your event plan:',
        value = report_value
      )
    # these steps can be optimized by building report_value one step at a time
    elif (maps_farmed_lazy == 0 and maps_farmed_black > 0):
      report_value = 'Completing the Extra stage daily, in addition to your missions, will bring your final-day total to *' + str(pt_total_now_daily_black) + ' ' + major_PT
      + '.*\n In order to buy out the full event shop, you will need to clear the final operation stage **' + str(maps_farmed) + ' times** *if you skip or cannot complete the Extra  stage*' + '.\n Clearing both your missions and the Extra stage daily reduces your the final operation stage clear count to **' + str(maps_farmed_black) + ' times**'
      + '.\n Completing daily missions and the Extra stage will mean that you are official finished with ' + major_event_name + '! Congratulations, Commander!'
      points_report.add_field(
        name = 'Your event plan:',
        value = report_value
      )
    elif (maps_farmed_black_lazy == 0 and maps_farmed_lazy > 0):
      report_value = 'Completing the Extra stage daily, in addition to your missions, will bring your final-day total to *' + str(pt_total_now_daily_black) + ' ' + major_PT
      + '.*\n In order to buy out the full event shop, you will need to clear the final operation stage **' + str(maps_farmed) + ' times** *if you skip or cannot complete the Extra stage*' + '.\n Clearing both your missions and the Extra stage daily reduces your the final operation stage clear count to **' + str(maps_farmed_black) + ' times**'
      + '.\n\n You can save 8,700 ' + major_PT + ' by skipping the T4 Tech Packs, T3 Parts, and Cognitive Chips, reducing your number of the final operation stage clears required'
      + '.\n You will only need to clear **' + str(maps_farmed_lazy) + ' times** for daily missions only'
      + '. Completing daily missions and the Extra stage will mean that you are official finished with ' + major_event_name + '! Congratulations, Commander!'
      points_report.add_field(
        name = 'Your event plan:',
        value = report_value
      )
    elif (maps_farmed_black_lazy > 0):
      report_value = 'Completing the Extra stage daily, in addition to your missions, will bring your final-day total to *' + str(pt_total_now_daily_black) + ' ' + major_PT
      + '.*\n In order to buy out the full event shop, you will need to clear the final operation stage **' + str(maps_farmed) + ' times** *if you skip or cannot complete the Extra stage*' + '.\n Clearing both your missions and the Extra stage daily reduces your the final operation stage clear count to **' + str(maps_farmed_black) + ' times**'
      + '.\n\n You can save 8,700 ' + major_PT + ' by skipping the T4 Tech Packs, T3 Parts, and Cognitive Chips, reducing your number of the final operation stage clears required'
      + '.\n You will only need to clear **' + str(maps_farmed_lazy) + ' times** for daily missions only, or **' + str(maps_farmed_black_lazy) + ' times** if you '
      + 'also clear the Extra stage.'
      points_report.add_field(
        name = 'Your event plan:',
        value = report_value, inline = False
      )
  else:
    if (maps_farmed == 0 and pt_total_now_daily >= major_PT_total):
      report_value = 'Completing daily missions will mean that you are official finished with ' + major_event_name + '! Congratulations, Commander!'
      points_report.add_field(
        name = 'Your event plan:',
        value = report_value
      )
    elif (maps_farmed > 0):
      report_value = 'Completing daily missions will bring your final-day total to *' + str(pt_total_now_daily) + ' ' + major_PT + '.*\n In order to buy out the full event shop, you will need to clear the final operation stage **' + str(maps_farmed) + ' times**.'
      points_report.add_field(
        name = 'Your event plan:',
        value = report_value
    )
  if (pt > major_PT_total):
    points_report = discord.Embed(
    title = 'Commander, we need to have a talk.',
    description = 'You already have enough ' + major_PT + ' to clear out the event shop. What do you need a report from me for?'
    )
  if (pt < 0):
    points_report = discord.Embed(
    title = 'Commander, something went wrong with your request. Please double-check and try again.',
    description = 'You should know by now Akashi doesn\'t accept credit. Points-debt must be your idea of a joke, right?'
    )
  await ctx.send(content=None, embed=points_report)
  return


# improvement(?): use emoji 1/2/3 for the last three days
async def daily():
  await bot.wait_until_ready()
  #post the report, but only at daily reset time
  while (True):
    the_time = pendulum.now('US/Pacific').strftime('%H:%M')
    # print(the_time) debug
    if the_time == daily_reset:
      # update today's date and dates on remaining events
      todays_date = pendulum.now('US/Pacific')
      print(todays_date)
      # generate the report detailing event info
      report = generate_daily_report(todays_date)
      #now drop it in the bot spam channel
      # kirakira test server 572663940375379988 / channel 572663940375379990
      # yakumo server 139255063787864064 / channel 572674736283189248
      await bot.get_guild(139255063787864064).get_channel(572674736283189248).send(content=None, embed=report)
    await asyncio.sleep(60)

def generate_daily_report(todays_date):
  #some improvements need to be made to report generation
  #last day before core shop reset
  #last day befpre token shop removal

  #get the list fresh
  events_list = read_events_list()
  events_list = process_events_list(events_list)
  report = discord.Embed(
    title = 'Good morning, Commanders!',
    description = 'Here is your report for *' +
    todays_date.format('ddd[,] MMM Do[,] H[:]mm zz') + '* (Server Time.)'
  )
  for line in events_list:
    # just skip any events that have ended already
    if todays_date < line.end_date:
      # if the end date is year 9999 (aka a placeholder)
      if line.end_date.year == 9999:
        day_days = 'days'
        if ((line.start_date.day_of_year) - todays_date.day_of_year) == 1:
          day_days = 'day'
        report.add_field(
          name = line.name.replace('_', ' '),
          value = '**Commencing in ' + str(line.start_date.day_of_year - todays_date.day_of_year) + ' '
          + day_days + 
          '.**\nStart: ' + str(line.start_date.format('ddd[,] MMM Do[,] H[:]mm zz')) +
          '.\nEnd date currently unknown.'
        )
      else:
        # if the event has begun and not ended
        if todays_date >= line.start_date:
          day_days = 'days remain'
          if (line.end_date.day_of_year - todays_date.day_of_year) == 0:
            day_days = 'day remains'
          if (line.end_date.day_of_year - todays_date.day_of_year) >= 0:
            report.add_field(
              name = line.name.replace('_', ' '),
              value = '**' + str(line.end_date.day_of_year - todays_date.day_of_year+1)
              + ' ' + day_days +
              '.**\n' +'Start: ' + str(line.start_date.format('ddd[,] MMM Do[,] H[:]mm zz')) +
              '.\nEnd: ' + str(line.end_date.format('ddd[,] MMM Do[,] H[:]mm zz')) + '.'
            )
            #bugfix for new year rollover
          else:
            report.add_field(
            name = line.name.replace('_', ' '),
            value = '**' + str((line.end_date.day_of_year - todays_date.day_of_year+1)+365)
            + ' ' + day_days +
            '.**\n' +'Start: ' + str(line.start_date.format('ddd[,] MMM Do[,] H[:]mm zz')) +
            '.\nEnd: ' + str(line.end_date.format('ddd[,] MMM Do[,] H[:]mm zz')) + '.'
            )
        else:
          # the event hasn't started but has an end date
          day_days = 'days'
          if ((line.start_date.day_of_year) - todays_date.day_of_year) == 1:
            day_days = 'day'
          report.add_field(
            name = line.name.replace('_', ' '),
            value = '**Commencing in ' + str(line.start_date.day_of_year - todays_date.day_of_year) + ' ' + day_days +
            '.**\nStart: ' + str(line.start_date.format('ddd[,] MMM Do[,] H[:]mm zz')) +
            '.\nEnd: ' + str(line.end_date.format('ddd[,] MMM Do[,] H[:]mm zz')) + '.'
          )
          # the order of doing that is really weird, and could be done better
          # I just don't give a shit right now, because it works.
  # add a message if there are no events running
  if str(report.fields) == '[]':
    report.add_field(
      name = 'Tranquil seas today',
      value = 'No operations are currently underway. Information on the next Mirror Sea will be available soon. Until then, enjoy some well-deserved peace and quiet.'
    )
  return report

@bot.command()
async def manualreport(ctx):
  #refresh variables for the date
  todays_date = pendulum.now('US/Pacific')
  #generate the report
  report = generate_daily_report(todays_date)
  #now drop it in the bot spam channel
  #upgrade: allow specific server to be targeted

  # kirakira test server 572663940375379988 / channel 572663940375379990
  # yakumo server 139255063787864064 / channel 572674736283189248
  await bot.get_guild(139255063787864064).get_channel(572674736283189248).send(content=None, embed=report)

@bot.event
async def on_raw_reaction_add(payload):
  ral = read_ral()
  #print(ral)
  for key in ral.keys():
    #print(str(payload.message_id) + ' vs ' + str(key))
    if str(payload.message_id) == key:
      #print(payload.emoji.name)
      server = payload.guild_id
      roles = bot.get_guild(server).roles
      match = False
      for role in roles:
        if role.name == payload.emoji.name:
          match = True
          break

      if match is True:
        print(role.name + " was found!")
        print(role.id)
        await bot.get_guild(server).get_member(payload.user_id).add_roles(role)
        print("added")

@bot.event
async def on_raw_reaction_remove(payload):
  ral = read_ral()
  for key in ral.keys():
    #print(str(payload.message_id) + ' vs ' + str(key))
    if str(payload.message_id) == key:
      #print(payload.emoji.name)
      server = payload.guild_id
      roles = bot.get_guild(server).roles
      match = False
      for role in roles:
        if role.name == payload.emoji.name:
          match = True
          break

    if match is True:
      print(role.name + " was found!")
      print(role.id)
      await bot.get_guild(server).get_member(payload.user_id).remove_roles(role)
      print("removed")

def read_events_list():
  data = open('events_list.txt','r')
  events_list = []
  for line in data:
    events_list.append(line)
  data.close()
  return events_list

def read_events_points():
  data = open('events_points.txt','r')
  events_points = []
  for line in data:
    events_points.append(line)
  data.close()
  return events_points

def read_ral():
  data = open('role_assignment_list.txt','r')
  ral = {}
  for line in data:
    (key, val1, val2) = line.split()
    ral[key] = (val1, val2)
  data.close()
  return ral

def process_events_list(raw_list):
  processed_list = []
  for line in raw_list:
    # [name] starting[y][m][d] ending[y][m][d] is the order of events_list.txt
    event_deets = line.split()
    event_deets[1] = int(event_deets[1])
    event_deets[2] = int(event_deets[2])
    event_deets[3] = int(event_deets[3])
    event_deets[4] = int(event_deets[4])
    event_deets[5] = int(event_deets[5])
    event_deets[6] = int(event_deets[6])
    start_date = pendulum.datetime(event_deets[1], event_deets[2], event_deets[3], tz='US/Pacific')
    end_date = pendulum.datetime(event_deets[4], event_deets[5], event_deets[6], 23, 59, tz='US/Pacific')
    #always assume events end at 23:59 PST
    processed_list.append(event(event_deets[0],start_date,end_date))
  return processed_list

def process_events_points(raw_list):
  processed_list = []
  for line in raw_list:
    # order of events_points.txt: event_name pt_name lastmap_pt daily_mission_pt black_pt shop_total_pt shop_total_pt_lazy
    event_deets = line.split()
    event_deets[2] = int(event_deets[2])
    event_deets[3] = int(event_deets[3])
    event_deets[4] = int(event_deets[4])
    event_deets[5] = int(event_deets[5])
    event_deets[6] = int(event_deets[6])
    processed_list.append(pt_event(event_deets[0],event_deets[1],event_deets[2],event_deets[3],event_deets[4],event_deets[5],event_deets[6]))
  return processed_list



keep_alive()
bot.loop.create_task(daily())
token = os.environ.get('DISCORD_BOT_SECRET')
bot.run(token)