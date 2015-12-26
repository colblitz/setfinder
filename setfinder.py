import itertools
import random
import time

NFEATURES = 5
NTYPES = 4
NTYPESSUM = NTYPES * (NTYPES-1) / 2
NSTART = 12

RFEATURES = range(NFEATURES)
RTYPES = range(NTYPES)

RBASE = [NTYPES**i for i in RFEATURES]
# print RBASE

class Card(object):
	def __init__(self, features):
		self.features = list(features)

	def get_feature(self, n):
		return self.features[n]

	def get_number(self):
		return sum(a*b for a,b in zip(RBASE, self.features))

	def __repr__(self):
		return "".join([str(f) for f in self.features[::-1]])

	def __eq__(self, other):
		return self.features == other.features

	def __hash__(self):
		return hash(self.get_number())

	def __cmp__(self, other):
		return cmp(self.get_number(), other.get_number())

def generate_deck():
	d = [Card(c) for c in itertools.product(RTYPES, repeat=NFEATURES)]
	random.shuffle(d)
	return d

d = generate_deck()
print "number of cards: ", len(d)

def get_random_card():
	return Card([random.randint(0, NTYPES-1) for f in range(NFEATURES)])

def ref_is_set(cards):
	for f in RFEATURES:
		s = {}
		for c in cards:
			s[c.get_feature(f)] = True
		if len(s) != NTYPES and len(s) != 1:
			return False
	return True

def ref_get_missing(cards):
	features = []
	for f in range(NFEATURES):
		existing = [c.get_feature(f) for c in cards]
		sexisting = set(existing)
		if len(sexisting) == 1:
			features.append(existing[0])
		elif len(sexisting) == len(existing):
			features.append(NTYPESSUM - sum(existing))
		else:
			return None
	return Card(features)

def ref_get_set(cards):
	for pset in itertools.combinations(cards, NTYPES):
		if ref_is_set(pset):
			return pset
	return []

def ref_print_all_sets(cards):
	for pset in itertools.combinations(cards, NTYPES):
		if ref_is_set(pset):
			print "  -  ", pset

##################################################
#### Players

class Player(object):
	def __init__(self):
		self.time = 0
		self.start = 0

	def get_set(self, board):
		raise NotImplementedError("get_set not implemented for " + type(self).__name__)

	def start_time(self):
		self.start = time.time()

	def get_time(self):
		return self.time

	def found(self, pset):
		self.time += time.time() - self.start
		return pset

class BaselinePlayer(Player):
	def __init__(self):
		super(BaselinePlayer, self).__init__()

	def get_set(self, board):
		self.start_time()
		for pset in itertools.combinations(board, NTYPES):
			if ref_is_set(pset):
				return self.found(pset)
		return self.found([])

class RecencyPlayer(Player):
	def __init__(self):
		super(RecencyPlayer, self).__init__()
		self.by_missing = {}
		self.by_card = {}

	def print_by_card(self):
		print "*"
		for c in self.by_card:
			print c, ": ", sorted(self.by_card[c])

	def print_by_missing(self):
		print "*"
		print len(self.by_missing)
		l = 0
		for m in self.by_missing.keys():
			l += len(self.by_missing[m])
		print l
		i = 0
		s = ""
		for c in self.by_missing.keys():
			s += "%s: %s  " % (str(c), str(self.by_missing[c]))
			i += 1
			if i == 5:
				print s
				i = 0
				s = ""
		print s

	def remove_update(self, cards):
		# print "        -----------------before remove"
		# print "set: ", cards
		# self.print_by_missing()
		# self.print_by_card()

		# for m in self.by_missing:
		# 	for pair in self.by_missing[m]:
		# 		for c in cards:
		# 			if c in pair:




		remove_from_missing = {}
		for c in cards:
			if c in self.by_card:
				for m in self.by_card[c]:
					remove_from_missing[m] = 1
		# print "removing: ", sorted(remove_from_missing.keys())
		for m in remove_from_missing.keys():
			if m in self.by_missing:
				new_others = []
				for other in self.by_missing[m]:
					keep = True
					for c in cards:
						if c in other:
							keep = False
					# print "cards: ", cards, " others: ", other
					# print "for m: ", m, " - keep: ", keep
					if keep:
						new_others.append(other)
				if new_others:
					self.by_missing[m] = new_others
				else:
					del self.by_missing[m]

				# for pair in se
				# 	# m is key to by_missing
				# 	if m in self.by_missing:
				# 		new_pairs = []
				# 		for pair in self.by_missing[m]:
				# 			if c not in pair:
				# 				new_pairs.append(pair)
				# 		if new_pairs:
				# 			self.by_missing[m] = new_pairs

		for c in cards:
			if c in self.by_missing:
				del self.by_missing[c]
			if c in self.by_card:
				del self.by_card[c]
		# print "        -----------------after remove"
		# self.print_by_missing()
		# self.print_by_card()
		# print "        -------------------------------------------------------------------"

	def make_set(self, card):
		# print "making set with ", card
		pset = [card]
		# get first cards that make set
		pset += self.by_missing[card][0]
		self.remove_update(pset)
		# print "returning ", pset
		return self.found(pset)

	def get_set(self, board):
		# print "####################################################################################"
		# print " ### board: ", board
		self.start_time()
		# ref_print_all_sets(board)
		# l = len(board)
		for i in range(len(board)):
			# print ref_print_all_sets(board)
			card = board[i]
			# first check if it makes a set
			if card in self.by_missing:
				return self.make_set(card)
			if card not in self.by_card:
				# print "adding combinations for ", card
				for others in itertools.combinations(board[:i], NTYPES-2):
					self.add_missing([card] + list(others))
			else:
				pass
		# self.print_by_missing()
		# self.print_by_card()
		# print "returning none"
		return self.found([])


		# print "####################################################################################"
		# if not self.by_missing:
		# 	print "generate"
		# 	self.generate_missing(board)
		# 	for c in board:
		# 		if c in self.by_missing:
		# 			print "found set"
		# 			return self.make_set(c)
		# # got new cards
		# elif board[-1] not in self.by_card:
		# 	l = len(board)
		# 	for i in range(l):
		# 		card = board[i]
		# 		print "card: ", card
		# 		if card in self.by_missing:
		# 			print "card in mising, make set"
		# 			return self.make_set(card)
		# 		# not in self.by_missing
		# 		if card not in self.by_card:
		# 			print "card not in missing, add to thing"
		# 			for others in itertools.combinations(board[:i], NTYPES-2):
		# 				self.add_missing([card] + list(others))
		# 		else:
		# 			print "what"
		# 			pass

		# print "------------------------------------------------------------------------"
		# print board
		# ref_print_all_sets(board)
		# self.print_by_missing()
		# self.print_by_card()
		# print "------------------------------------------------------------------------"
		# return self.found([])

	def add_missing(self, almost):
		almost = list(almost)
		missing = ref_get_missing(almost)
		if missing in self.by_missing:
			self.by_missing[missing].append(almost)
		else:
			self.by_missing[missing] = [almost]
		for c in almost:
			if c not in self.by_card:
				self.by_card[c] = []
			self.by_card[c].append(missing)

	def generate_missing(self, board):
		for almost in itertools.combinations(board, NTYPES-1):
			self.add_missing(almost)

##################################################
#### Game

class Game(object):
	def __init__(self, player):
		self.player = player
		self.new_game()

	def new_game(self):
		self.deck = generate_deck()
		self.board = []

	def start_game(self):
		self.deal(NSTART)

	def deal(self, n):
		for x in xrange(min(n, len(self.deck))):
			self.board.append(self.deck.pop())

	def print_state(self):
		print "(%d) Board: %s" % (len(self.deck), str(self.board))

	def remove_cards(self, cards):
		for c in cards:
			self.board.remove(c)

	def play_game(self):
		self.new_game()
		self.start_game()
		while not self.is_done():
			print "getting set from board of length: ", len(self.board), ", ", len(self.deck), " cards left"
			next_set = self.player.get_set(self.board)
			if len(next_set) == 0:
				if not self.no_sets():
					print "######## ERROR: player wrongly said no set"
					break
				else:
					self.deal(3)
					continue
			if not ref_is_set(next_set):
				print "######## ERROR: player got wrong set: " + str(next_set)
				break
			else:
				# print "player returned set: ", next_set
				self.remove_cards(next_set)
				if len(self.board) < NSTART:
					self.deal(3)
		return self.player.get_time()

	def no_sets(self):
		if len(self.board) < NTYPES:
			return True
		for pset in itertools.combinations(self.board, NTYPES):
			if ref_is_set(pset):
				return False
		return True

	def is_done(self):
		return len(self.deck) == 0 and self.no_sets()

t = 0.0
n = 1
for x in xrange(n):
	g = Game(BaselinePlayer())
	t += g.play_game()
print "base ---------------------------------------------------------------------"
print t
print t/n

t = 0.0
for x in xrange(n):
	g = Game(RecencyPlayer())
	t += g.play_game()
print "recency ------------------------------------------------------------------"
print t
print t/n


# a = {}
# b = 0
# for n in xrange(5):
# 	b = get_random_card()
# 	a[b] = n
# print a
# print b
# print b in a

# c = Card([1, 2, 3, 4])
# a[c] = 5

# d = Card([1, 2, 3, 4])
# print c == d
# print d in a