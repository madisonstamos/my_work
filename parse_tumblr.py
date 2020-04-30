import json
import datetime
import re
import random


def load_file(file_name):
	'''
	Loads your tumblr file

	Input:
		file_name: a .json file with your tumblr data

	Output:
		tumblr: a json loaded file from the load_file function
	'''

	with open(file_name, "r") as f:
		tumblr = json.loads(f.read())
		tumblr = tumblr[0]["data"]

	return tumblr


def parse_date(date_str):
	'''
	Helper to get a datetime object from an unformatted date str

	Input:
		date_str: an unformatted date str

	Output:
		day: a datetime object
	'''
	DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
	
	day = DATE.findall(date_str)
	day = [int(i) for i in day[0]]
	day = datetime.date(day[0], day[1], day[2])

	return day


def extract_crushes_str(tumblr):
	'''
	Find out who tumblr thinks you're crushing on and who's crushing on you

	Input:
		tumblr: a json loaded file from the load_file function

	Output:
		crushes_str: a str with relevant info about tumblr crushes
	'''

	crushes = tumblr["crushes"]
	crushes_str = "Tumblr thinks your top {} crushes are on the following users:"\
		.format(len(crushes))

	for crush in crushes[:-1]:
		crushes_str += " {},".format(crush["blog_name"])
	crushes_str += " and {}. ".format(crushes[-1]["blog_name"])

	return crushes_str


def extract_crushers_str(tumblr):
	'''
	Find out who tumblr thinks is crushing on you

	Input:
		tumblr: a json loaded file from the load_file function

	Output:
		crushers_str: a str with relevant info about tumblr crushes
	'''

	crushers = tumblr["crushers"]
	crushers_str = ""

	for blog in crushers:
		blog_name = list(blog.keys())[0]
		if len(blog[blog_name]) > 0:
			crushers_str += "For your blog named {}, Tumblr thinks the following users are crushing on you:"\
			.format(blog_name)
			for crusher in blog[blog_name][:-1]:
				crushers_str += " {},".format(crusher["blog_name"])
			crushers_str += " and {}. ".format(blog[blog_name][-1]["blog_name"])

	return crushers_str


def parse_dashboard(tumblr):
	'''
	Serves relevant information about your tumblr dashboard and posts you've 
	been served on it.

	Input:
		tumblr: a json loaded file from the load_file function

	Output:
		dash_str: a str with relevant info about your tumblr file
	'''

	dash = tumblr["dashboard"]
	dash_str = "Tumblr has kept track of the last {} posts you've seen. "\
		.format(len(dash))

	earliest = parse_date(dash[0]["serve_time"])
	latest = earliest

	for post in dash:
		day = parse_date(post["serve_time"])

		if day < earliest:
			earliest = day
		if day > latest:
			latest = day

	dash_str += "These posts range from {} to {}. ".format(earliest, latest)

	return dash_str


def easter_egg_blog(tumblr):
	'''
	Easter egg about previous blog name

	Input:
		tumblr: a json loaded file from the load_file function

	Output:
		easter_egg: str with prev blog name, if applicable
	'''

	easter = tumblr["blog_names"]
	easter_egg = ""

	for blog in easter:
		if len(blog["prev_used_blog_name"]) > 0:
			cur_name = blog["current_blog_name"]
			old_name = random.choice(blog["prev_used_blog_name"])

			easter_egg += "By the way, remember when your blog called {} was called {}? "\
			.format(cur_name, old_name)
			break

	return easter_egg


def ads_summary(tumblr):
	'''
	Summary stats about ads seen

	Input:
		tumblr: a json loaded file from the load_file function

	Output:
		ads_str: a str with information about ads tumblr keeps on you
	'''

	ads = tumblr["ads_analytics"]
	gem_ads = tumblr["gemini_analytics"]
	cli_ads = tumblr["client_side_ad_analytics"]

	earliest = parse_date(ads[0]["serve_time"])
	num_seen = 0
	interacted = 0
	all_served = len(ads) + len(gem_ads) + len(cli_ads)
	

	for ad_class in [ads, gem_ads, cli_ads]:
		for ad in ad_class:
			if ad["serve_time"] != "\\N":
				day = parse_date(ad["serve_time"])
				if day < earliest:
					earliest = day
			if ad["viewed"] == "true":
				num_seen += 1
			if ad["interacted"] == "true":
				interacted += 1

	ads_str = "Since {}, Tumblr has kept track of the ads they've served you. "\
	.format(earliest)
	ads_str += "This doesn't just include the {} ads you actually saw, but also"\
	.format(num_seen)
	ads_str += " another {} that you never viewed. ".format(all_served-num_seen)
	ads_str += "Of those, you interacted with {} of them, or about {:.2f}%. "\
	.format(interacted, interacted/num_seen*100)

	return ads_str


def top_tags(tumblr):
	'''
	Collects the top tag you used across your blogs.

	Inputs:
		tumblr: a json loaded file from the load_file function

	Outputs:
		tag_str: a str with info about your top tag
	'''

	tags = tumblr["most_used_tags"]
	top_count = 0

	for tag in tags:
		if int(tag["tag_count"]) > top_count:
			top_count = int(tag["tag_count"])
			top_blog = tag["blog_name"]
			top_tag = tag["tag"]

	tag_str = "You use the tag '{}' on your {} blog a lot; {} to be exact."\
	.format(top_tag, top_blog, top_count)

	return tag_str


def last_active(tumblr):
	'''
	Parses all tumblr sessions

	Inputs:
		tumblr: a json loaded file from the load_file function	

	Output:
		act_str: a str with info about your last active session
	'''

	sessions = tumblr["last_active_times"]
	earliest = parse_date(sessions[0])
	act_str = "Tumblr has also stored every time you were active on their site"

	for session in sessions:
		day = parse_date(session)
		if day < earliest:
			earliest = day

	act_str += " since {}, or {} active sessions."\
	.format(earliest, len(sessions))

	return act_str


def interests(tumblr):
	'''
	Generates a str summary about your inferred interests

	Inputs:
		tumblr: a json loaded file from the load_file function

	Outputs:
		int_str: a str with summary info about inferred interests
	'''

	interests = tumblr["user_interest_profiles"]
	int_str = "Tumblr has also used your behavior on their site to infer interests about you. "
	int_str += "From these behaviors, they have inferred {} interests about you. "\
	.format(len(interests))
	int_str += "Here is a sample of those inferred interests: "

	int_sample = random.sample(interests, min(5, len(interests)))
	for interest in int_sample[:-1]:
		int_str += "{}, ".format(interest["interest"])
	int_str += "and {}.".format(int_sample[-1]["interest"])

	return int_str


def summary_info(file_name):
	'''
	Returns relevant summary info from your tumblr data.

	Input:
		file_name: a .json file with your tumblr data

	Output:
		summary_str: a str with relevant info about your tumblr data
	'''

	tumblr = load_file(file_name)
	join_time = tumblr["registration_time"].split(" ")[0]
	last_post = tumblr["last_post_time"].split("T")[0]
	unfollows = tumblr["unfollows"]

	summary_str = "According to your data, you joined Tumblr on {}"\
		.format(join_time)
	summary_str += ", and you last posted on {}. ".format(last_post)
	summary_str += "Over the course of this time, you have unfollowed {} users. "\
	.format(len(unfollows))
	summary_str += last_active(tumblr) + "\n \n"

	summary_str += parse_dashboard(tumblr)
	summary_str += ads_summary(tumblr) 
	summary_str += interests(tumblr) + "\n \n"

	summary_str += easter_egg_blog(tumblr)
	summary_str += extract_crushes_str(tumblr)
	summary_str += extract_crushers_str(tumblr)
	summary_str += top_tags(tumblr)

	return summary_str






