import json
import queue

def parse_stream(file_name = "StreamingHistory.json"):
	'''
	Takes a streaming history file and returns a dictionary of artists, songs, 
		and runtime

	Inputs:
		file_name: Should be "StreamingHistory.json"

	Outputs:
		history, a dictionary of artists keys. Artists keys link to dictionaries of
			songs, which link to minutes of total streaming time for that song.
	'''

	history = dict()
	with open(file_name, "r") as f:
		stream = json.loads(f.read())

	for song in stream:
		if song["artistName"] not in history.keys():
			history[song["artistName"]] = dict()
			history[song["artistName"]] = dict()
			history[song["artistName"]][song["trackName"]] = song["msPlayed"] / 60000
		else:
			if song["trackName"] in history[song["artistName"]].keys():
				history[song["artistName"]][song["trackName"]] += song["msPlayed"] / 60000
			else:
				history[song["artistName"]][song["trackName"]] = song["msPlayed"] / 60000

	return history


def find_amount_listened(history, artistName):
	'''
	Finds the total amount of time listened to a given artist

	Inputs:
		history: a dictionary of artists, the return of parse_stream
		artistName: a string, the name of an artist of interest

	Outputs:
		a float, the total number of hours listened to an artist (rounded to 
			two decimal places)
	'''

	total_time_listened = 0

	for key, val in history[artistName].items():
		total_time_listened += val

	return float("{:.2f}".format(total_time_listened / 60))


def artist_top_songs(history, artistName, maxsize = 10):
	'''
	Finds the top songs listened to for a given artist

	Inputs:
		history: a dictionary of artists, the return of parse_stream
		artistName: a string, the name of an artist of interest
		maxsize: an integer, the maximum number of songs to track, 10 by default

	Outputs:
		final: a list of tuples. The first element in the tuple is the number of 
		minutes spent listening to the song, the second element of the 
		tuple is the song name 
	'''

	top = queue.PriorityQueue(maxsize = maxsize)
	final = []

	for key, val in history[artistName].items():
		if not top.full():
			top.put((val, key))
		else:
			bottom = top.get()
			if val > bottom[0]:
				top.put((val, key))
			else:
				top.put(bottom)

	while not top.empty():
		final.append(top.get())

	final.reverse()
	return final


def top_artists(history, maxsize = 10):
	'''
	Finds the top artists listened to

	Inputs:
		history: a dictionary of artists, the return of parse_stream
		maxsize: an integer, the maximum number of artists to track. 10 by default.

	Outputs:
		final: a list of tuples. The first element of the tuple is the number
			of hours spent listening to the artist, the second element is the
			artist name
	'''

	top = queue.PriorityQueue(maxsize = maxsize)
	final = []

	for artistName in history.keys():
		time_listed = find_amount_listened(history, artistName)
		if not top.full():
			top.put((time_listed, artistName))
		else:
			bottom = top.get()
			if time_listed > bottom[0]:
				top.put((time_listed, artistName))
			else:
				top.put(bottom)

	while not top.empty():
		final.append(top.get())

	final.reverse()
	return final

	
