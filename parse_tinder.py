import json
import datetime
import re


def count_matches(filename):
	'''
	Returns information regarding the number of user's lifetime matches

	Input:
		filename: a string, the name of the tinder json file

	Output:
		a string, contains information about lifetime reviews.
	'''

	with open(filename, "r") as f:
		tinder = json.loads(f.read())
		matches = 0
		likes = 0
		passes = 0
		earliest = datetime.date(2050, 12, 31)
		latest = datetime.date(2010, 1, 1)
		DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

		for i, val in tinder["Usage"]["matches"].items():
			matches += val
			day = DATE.findall(i)
			day = [int(i) for i in day[0]]
			day = datetime.date(day[0], day[1], day[2])
			if day < earliest:
				earliest = day
			if day > latest:
				latest = day

		for i, val in tinder["Usage"]["swipes_likes"].items():
			likes += val

		for i, val in tinder["Usage"]["swipes_passes"].items():
			passes += val

	return "Between {} and {}, you received {} matches on {} likes and {} passes, which is a match rate of {:.2f}%, and a swipe ratio of {:.2f}".\
		format(earliest, latest, matches, likes, passes, matches/likes*100, passes/likes)





