#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 21:15:01 2022

This project aims to explore Metrica's public tracking data and create 
visualizations that aid in the tactical analysis of the matchplay. This
analysis is exploratory and is not meant to serve as a comprehensive 
report.

This project is inspired by Laurie Shaw's video with Friends of Tracking
https://www.youtube.com/watch?v=8TrleFklEsE

@author: tuckerparon
"""

# Imports.
import math
import json
import string
import collections
from kloppy import metrica
import Metrica_Viz as mviz # https://github.com/Friends-of-Tracking-Data-FoTD/LaurieOnTracking


# Functions!
def read_event_data(directory, game_id):
    '''
    Read Metrica event data for game_id and return as data frame
    '''
    filename = '/Sample_Game_%d/Sample_Game_%d_events.json' % (game_id, game_id)
    filename = directory + filename # Get full path.
    file = open(filename) # Open file.
    events = json.load(file) # Read data.
    return events

def read_tracking_data(directory, game_id):
    '''
    Read Metrica tracking data and metadata and return it
    '''
    meta_data = '/Sample_Game_%d/Sample_Game_%d_metadata.xml' % (game_id, game_id)
    meta_data = directory + meta_data
    raw_data = '/Sample_Game_%d/Sample_Game_%d_tracking.txt' % (game_id, game_id)
    raw_data = directory + raw_data
    
    # https://kloppy.pysport.org/getting-started/metrica/#load-remote-csv-tracking-files
    tracking_data = metrica.load_tracking_epts(meta_data=meta_data, 
                                               raw_data=raw_data,
                                               sample_rate=1/5,
                                               limit=100,
                                               coordinates="metrica")
    return tracking_data

    
# Set directory and select the game.
directory = '' # Set directory (this will work if you download the repo as is)
game_id = 3

# Get type of action and frequency.
events = read_event_data(directory, game_id)
types = [ d['type']['name'] for d in events.get('data') ]
types_count = dict(collections.Counter(types))

# Now just the frequencies for team A...
typesA = [ d['type']['name'] for d in events.get('data') if d['team']['name'] == 'Team A' ]
types_countA = dict(collections.Counter(typesA)) 

# and for Team B.
typesB = [ d['type']['name'] for d in events.get('data') if d['team']['name'] == 'Team B' ]
types_countB = dict(collections.Counter(typesB))

# It may be interesting to isolate all of the shots for one Team...
shotsA = [ d for d in events.get('data') if (d['type']['name'] == 'SHOT' and d['team']['name'] == 'Team A') ]

# ... and further identify which were goals.
goalsA = [ s for s in shotsA if ( type(s['subtypes']) == list and s['subtypes'][1]['name'] == 'GOAL') ]
print(" Team A had", len(goalsA), "goals.\n")

# We can see Team A had zero goals as GoalsA , let's see if Team B scored...
shotsB = [ d for d in events.get('data') if (d['type']['name'] == 'SHOT' and d['team']['name'] == 'Team B') ]
goalsB = [ s for s in shotsB if ( type(s['subtypes']) == list and s['subtypes'][1]['name'] == 'GOAL') ]

print(" Team B had", len(goalsB), "goals. Below is the data for each goal.\n")
for g in goalsB:
    print(g, end = "\n\n")
    
# ... and maybe visualize them?
fig,ax = mviz.plot_pitch()
for g in goalsB:
     x = [( -53 + (106 * g['start']['x'])), ( -53 + (106 * g['end']['x']))] # Start and end x coordinate
     y = [( -53 + (106 * g['start']['y'])), ( -53 + (106 * g['end']['y']))] # Start and end y coordinate
     time = math.trunc(g['start']['time']/60) # Minute of shot
     player = g['from']['name'] # Player name
     label = player + "\n(" + str(time) + "')" # Player with minute
     
     ax.plot(x, y, color = 'b')
     ax.plot(x[0], y[0], marker = 'o', MarkerSize = 5, color = 'b')
     ax.annotate(text = label, xy = (x[0], y[0]), xytext = (x[0], y[0]+2), fontsize = 17, color = 'b')
ax.set_title("Team B Goals", fontsize=20)
     
# Now we can see the goals scored (both of which were by Team B), but it might be helpful to see all the
# shots plotted...
fig,ax = mviz.plot_pitch()
for s in shotsB:
     x = [( -53 + (106 * s['start']['x'])), ( -53 + (106 * s['end']['x']))] # Start and end x coordinate
     y = [( -53 + (106 * s['start']['y'])), ( -53 + (106 * s['end']['y']))] # Start and end y coordinate
     time = math.trunc(s['start']['time']/60) # Minute of shot
     player = s['from']['name'] # Player name
     label = player + "\n(" + str(time) + "')" # Player with minute
     
     # Select color and features of plotted points based on result of each shot.
     if type(s['subtypes']) == list and s['subtypes'][0]['name'] != 'ON TARGET':
         ax.plot(x, y, color = 'r')
         ax.plot(x[0], y[0], marker = 'o', MarkerSize = 5, color = 'r', label = 'on-target')
     elif type(s['subtypes']) == list and s['subtypes'][1]['name'] == 'GOAL':
         ax.plot(x, y, color = 'b')
         ax.plot(x[0], y[0], marker = 'o', MarkerSize = 5, color = 'b', label = 'goal')
         ax.annotate(text = label, xy = (x[0], y[0]), xytext = (x[0], y[0]+2), fontsize = 17, color = 'b')
     elif type(s['subtypes']) != list:
         ax.plot(x, y, color = 'r')
         ax.plot(x[0], y[0], marker = 'o', MarkerSize = 5, color = 'r')
         ax.plot(x[1], y[1], marker = '|', MarkerSize = 15, color = 'black', label = 'blocked')
     else:
         ax.plot(x, y, color = 'y')
         ax.plot(x[0], y[0], marker = 'o', MarkerSize = 5, color = 'y', label = 'off-taregt')
ax.set_title("Team B Shots", fontsize=20)

# ...and the build up play for the goals...
colors = ['red', 'green', 'cyan', 'orange', 'yellow', 'black', 'purple', 'brown', 'blue', 'pink']
types_colors = {}
i = 0
for key, val in types_count.items():
    types_colors[key] = colors[i]
    i += 1
 
fig,ax = mviz.plot_pitch()
labels = []
for g in goalsB:
    goal_index = g['index'] # Get index of goal
    preceding_events = [ e for e in events.get('data') if e['index'] in range(goal_index-5, goal_index+1) ] # Get 5 events leading up to goal
    for p in preceding_events:
        action = p['type']['name']
        color = types_colors[action]
        
        # Plot the actions as a line unless it is an action that occurs at only one point (like a tackle)
        try:
            x = [( -53 + (106 * p['start']['x'])), ( -53 + (106 * p['end']['x']))] # Start and end x coordinate
            y = [( -53 + (106 * p['start']['y'])), ( -53 + (106 * p['end']['y']))] # Start and end y coordinate
        except:
            x = [( -53 + (106 * p['start']['x']))] # Start and end x coordinate
            y = [( -53 + (106 * p['start']['y']))] # Start and end y coordinate
        
        # This code plots the actions and ensures the legend doesn't have duplicate labels!
        if action not in labels:
            ax.plot(x, y, color = color, label = action)
            ax.plot(x[0], y[0], marker = 'o', MarkerSize = 5, color = color)
            labels.append(action)
        else:
            ax.plot(x, y, color = color)
            ax.plot(x[0], y[0], marker = 'o', MarkerSize = 5, color = color)
ax.legend()
ax.set_title("Team B Build-Up", fontsize=20)

# ...and even the position of all the players.
tracking_data = read_tracking_data(directory, game_id)
metadata = tracking_data.metadata
home_team, away_team = metadata.teams

# Unfortunately, it seems as if this set only includes the first 100 frames so we cannot
# see the positions of the players during the goals; 
print("There are", len(tracking_data.frames), "frames at", (tracking_data.frame_rate), "frames per second")      

# however, we can rewind a bit and see how the teams lined up.
fig,ax = mviz.plot_pitch() 
first_frame = tracking_data.frames[0]
for player, player_coordinates in first_frame.players_coordinates.items():
    if player_coordinates != None:
        p = str(player_coordinates)
        x = float(p[p.find("x=")+2:p.find(",")])
        x = ( -53 + (106 * x))
        y = float(p[p.find("y=")+2:p.find(")")])
        y = ( -53 + (106 * y))
    if player.team == home_team:
        ax.plot(x, y, marker = 'o', MarkerSize = 5, color = 'b')
    else:
        ax.plot(x, y, marker = 'o', MarkerSize = 5, color = 'r')
        
ax.plot(0, 0, marker = 'o', MarkerSize = 0, color = 'b', label = 'Team B')
ax.plot(0, 0, marker = 'o', MarkerSize = 0, color = 'r', label = 'Team A')
ax.legend()
ax.set_title("Starting Formations", fontsize=20)
                                    



