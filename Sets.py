import networkx as nx
import sys

def get_bitmask(color, case, symbol, num):
# calculates the bitmask based on color, case, symbol, number
# 2 bits per characteristic
# order(highest bits to lowest bits): color, case, symbol, number
# each card thus has a unique bitmask
	bitmask = 0
	bitmask |= color << 6
	bitmask |= case << 4
	bitmask |= symbol << 2
	bitmask |= num
	return bitmask


def determine_card(card_list):
# determines the color, case, symbol and number from a card give in the input
# returns the bitmask for that card based on color, case, symbol and number
	bitmask = 0
	# assigns each color a number between 0 and 2 which will be encoded in the bitmask
	color = card_list[0]
	if (color == 'blue'): color = 0
	elif (color == 'yellow'): color = 1
	else: color = 2
	symbol = card_list[1][0]
	# assigns each case a number between 0 and 2 which will be encoded in the bitmask
	ord_sym = ord(symbol)
	if ((ord_sym >= ord('a')) and (ord_sym <= ord('z'))): case = 0
	elif ((ord_sym >= ord('A')) and (ord_sym <= ord('Z'))): case = 1
	else: case = 2 
	# assigns each symbol a number between 0 and 2 which will be encoded in the bitmask
	if (symbol == 'H' or symbol == "h" or symbol == "#"): symbol = 0
	elif (symbol == "A" or symbol == "a" or symbol == "@"): symbol = 1
	else: symbol = 2
	# the number of symbols minus 1 is encoded in the bitmask
	num = len(card_list[1]) - 1
	# the unique bitmask determined with the values above are returned
	return get_bitmask(color, symbol, case, num)


def get_cards(input_set):
# gets the indivial cards from the input
# puts the cards in a dictionary where the key is their unique bitmask
# determines the number of cards from the input as well
	cards = []
	dict_cards = dict()
	for line in input_set:
		card_list = line.split()
		if (len(card_list) == 1): card_num = int(card_list[0])
		elif (len(card_list) != 2): continue
		else:
			bitmask = determine_card(card_list)
			dict_cards[bitmask] = (card_list)
			cards += [bitmask]	
	return card_num, cards, dict_cards


def get_card_characteristics(index, cards):
# given a list of the bitmasks of cards and an index, the color, case, symbol
# and number of the card at the index is returned
	card = cards[index]
	col = (card & 0xC0) >> 6
	case = (card & 0x30) >> 4
	sym = (card & 0x0C) >> 2
	num = (card & 0x03)
	return (col, case, sym, num)


def get_card3(col1, case1, sym1, num1, col2, case2, sym2, num2):
# if two cards are known then the third card needed to form a set is unique 
# the third card can be determined by checking whether the 2 cards share
# a particular characteristic or they don't
# if they don't share the characteristic then the value of the characteristic
# can be found by subtracting the values of the known 2 cards' characteristics
# from 3 as each characteristic can be a value of either 0, 1, 2 which sum to 3
	if (col1 == col2): col3 = col1
	else:	col3 = 3 - col1 - col2

	if (case1 == case2): case3 = case1
	else:	case3 = 3 - case1 - case2

	if (sym1 == sym2): sym3 = sym1
	else:	sym3 = 3 - sym1 - sym2

	if (num1 == num2): num3 = num1
	else:	num3 = 3 - num1 - num2	

	return col3, case3, sym3, num3	


def find_num_of_sets(card_num, cards, dict_cards):
# finds all possible sets from the inputted cards
# returns the number of sets found and a list of the sets
# a python set of all the sets that have been found is used to ensure
# sets are counted 3 times when the order of the cards differ
	found_sets = set()
	found_sets_list = []

	for i in xrange(card_num - 1):
		col1, case1, sym1, num1 = get_card_characteristics(i, cards)
		bitmask1 = get_bitmask(col1, case1, sym1, num1)
		#compares this card to all remaining cards after this card
		for j in xrange((i+1), card_num):
			col2, case2, sym2, num2 = get_card_characteristics(j, cards)
			bitmask2 = get_bitmask(col2, case2, sym2, num2)
			#finds the necessary characteristics for card three
			col3, case3, sym3, num3 = get_card3(col1, case1, sym1, num1, col2, case2, sym2, num2)
			bitmask3 = get_bitmask(col3, case3, sym3, num3)
			# determines if the third card is indeed a card and if so
			# checks if the three cards have already been identified as a set
			# if a valid set that has not been identified before then added
			# to the list containing the found sets and the python set
			if (bitmask3 in dict_cards): 
				if (((bitmask1, bitmask2, bitmask3) not in found_sets) and
					 ((bitmask1, bitmask3, bitmask2) not in found_sets) and
					 ((bitmask2, bitmask3, bitmask1) not in found_sets) and
					 ((bitmask2, bitmask1, bitmask3) not in found_sets) and
					 ((bitmask3, bitmask2, bitmask1) not in found_sets) and
					 ((bitmask3, bitmask1, bitmask2) not in found_sets)):
					found_sets.add((bitmask1, bitmask2, bitmask3))
					found_sets_list += [(bitmask1, bitmask2, bitmask3)]
	return found_sets_list


def is_disjoint(set1, set2):
# determines whether 2 sets are disjoint
	for elem in set2:
		if (set1[0] == elem or set1[1] == elem or set1[2] == elem):
			return False;
	return True


def find_disjoint_sets(found_sets):
# uses python graph data structure in which each node is a set
# edges are created between nodes if the nodes are disjoint sets
# the maximum clique algorithm is used to calculate the largest collection
# of disjoint sets
	#initialize graph
	graph = nx.Graph();
	#add all sets as nodes in the graph
	for i in xrange (len(found_sets)):
		graph.add_node(found_sets[i]);
	#iteraties though each node and adds edges
	for node1 in graph.nodes():
		for node2 in graph.nodes():
			if (node1 == node2): continue
			if (node2 in graph.neighbors(node1)): continue
			else:
				if (is_disjoint(node1, node2)): graph.add_edge(node1, node2)
	#use find_cliques function generator to find the max cliques
	max_clique = []
	for clique in nx.find_cliques(graph):
		if (len(max_clique) < len(clique)):
			max_clique = clique

	return max_clique


def sets():
# takes input from stdin and finds the number of total sets and the 
# largest disjoint set and outputs it
	input_set = []
	for message in sys.stdin.readlines():
		input_set += [message]
 	card_num, cards, dict_cards = get_cards(input_set)
	found_sets_list = find_num_of_sets(card_num, cards, dict_cards)	
	disjoint_sets = find_disjoint_sets(found_sets_list)
	print len(found_sets_list), " "
	print len(disjoint_sets)
	print "\n"
	for elem in disjoint_sets:
		for bitmask in elem:
			print dict_cards[bitmask][0], dict_cards[bitmask][1]
		print "\n"

sets()
