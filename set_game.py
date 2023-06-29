import numpy as np
import random
import math

def generate_deck():
	'''
	generates a deck of set cards

	inputs: n/a
	outputs: deck: a list of tuples representing cards
	'''

	deck = []

	for first_e in range(3):
		for second_e in range(3):
			for third_e in range(3):
				for fourth_e in range(3):
					deck.append((first_e, second_e, third_e, fourth_e))

	return deck


def check_set(potential_set):
	'''
	checks the validity of a potential set

	import: potential_set, a list of 3 tuples
	export: boolean, whether the input is a valid set or not
	'''

	for i in range(4):
		set_check = set()
		for j in potential_set:
			set_check.add(j[i])
		if len(set_check) != 1 and len(set_check) != 3:
			return False

	return True	

def complete_set(card_one, card_two):
	'''
	finds the third card to complete the set

	inputs:
		card_one: first tuple to check
		card_two: second tuple to check

	returns
		card_three: tuple card that completes the set
	'''

	card_three = []

	for i in range(4):
		if card_one[i] == card_two[i]:
			card_three.append(card_one[i])
		else:
			diff_card = {0, 1, 2} - {card_one[i]} - {card_two[i]}
			card_three.append(diff_card.pop())

	return tuple(card_three)


def generate_players(num_players):
	'''
	determines skill level for each player

	inputs: 
		num_plays: a list of integers representing the
		number of players in the game

	outputs: players, dict of player dicts, with skill assigned
	'''

	players = {}
	
	for i in range(num_players):
		mean, st_dev = np.random.random(2)
		players[i] = {}
		players[i]["mean"] = mean
		players[i]["std_dev"] = st_dev
		players[i]["sets"] = []

	return players


def player_turn(players):
	'''
	determines who will find the next set

	input:
		players, a list of dicts

	outputs:
		player, an int of the player whose turn it is
	'''

	winning_roll = -math.inf
	current_player = list(players.keys())[0]
	for player in players:
		roll = np.random.normal(loc = players[player]["mean"], scale = players[player]["std_dev"])
		if roll > winning_roll:
			winning_roll = roll
			current_player = player

	return current_player


def deal_card(deck):
	'''
	deals a card to the table by picking a random card
	to deal, and then removing the card from the
	remaining deck cards

	inputs
		deck: an undealt list deck of remaining set cards

	outputs:
		card: a tuple representing a random set card
	'''

	card = deck.pop(random.randint(0, len(deck)-1))
	return card


def find_set(table):
	'''
	finds a set on the current table of dealt set cards.
	if there are no sets on the table, returns false

	inputs:
		table, a list of tuples representing the current 
		table of dealt cards

	outputs:
		if a set exists, returns the set
		else returns False
	'''

	for card_one in range(len(table)):
		for card_two in range(card_one+1, len(table)):
			card_three = complete_set(table[card_one], table[card_two])
			if card_three in table:
				found_set = [table[card_one], table[card_two], tuple(card_three)]
				return found_set

	return False

def winner(players):
	'''
	determines winner of set game

	inputs:
		player dicts

	outputs:
		tuple (player name, number of sets)
	'''

	winning_sets = 0
	winner = ""

	explainer_string = ""

	for player in players:
		if len(players[player]["sets"]) > winning_sets:
			winning_sets = len(players[player]["sets"])
			winner = str(player)
		explainer_string += str(player) + " had " + str(len(players[player]["sets"])) + " sets. "

	return winner + " was the winner, with " + str(winning_sets) + " sets. " + explainer_string

def play_game(num_players):
	'''
	put it all together! plays a game of set

	inputs:
		a number of players

	output: a winner
	'''

	deck = generate_deck()
	players = generate_players(num_players)
	table = []
	[table.append(deal_card(deck)) for _ in range(12)]

	while len(table) > 0:
		while len(table) < 12: ##number of cards on table in standard set game
			if len(deck) > 0:
				table.append(deal_card(deck))
			else:
				break
		turn = player_turn(players)
		found_set = find_set(table)
		if not found_set:
			if len(table) < 12:
				return winner(players)
			elif len(deck) > 0:
				[table.append(deal_card(deck)) for _ in range(3)]
			else:
				return winner(players)
		else:
			players[turn]["sets"].append(found_set)
			table = [card for card in table if card not in found_set]

	return winner(players)




