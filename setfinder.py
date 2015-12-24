import itertools
import random
import time

NFEATURES = 4
NTYPES = 3
NTYPESSUM = NTYPES * (NTYPES-1) / 2
NSTART = 12

RFEATURES = range(NFEATURES)
RTYPES = range(NTYPES)

RBASE = [NTYPES**i for i in RFEATURES]
print RBASE

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
		# print self.features
		# print other.features
		return self.features == other.features

	def __hash__(self):
		# print "features: ", self.features, " --> ", sum(a*b for a,b in zip(RBASE, self.features))
		return hash(self.get_number())

	def __cmp__(self, other):
		# return cmp(other.get_number(), self.get_number())
		return cmp(self.get_number(), other.get_number())

def generate_deck():
	d = [Card(c) for c in itertools.product(RTYPES, repeat=NFEATURES)]
	random.shuffle(d)
	return d

d = generate_deck()
# print sorted(d)
# print d
# print len(d)

def get_random_card():
	return Card([random.randint(0, NTYPES-1) for f in range(NFEATURES)])

def ref_is_set(cards):
	for f in RFEATURES:
		s = {}
		for c in cards:
			s[c.get_feature(f)] = True
		if len(s) != NTYPES and len(s) != 1:
			return False
	# print cards, " is a set"
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
		# if c1.get_feature(f) == c2.get_feature(f):
		# 	features.append(c1.get_feature(f))
		# else:
		# 	features.append(NTYPESSUM - c1.get_feature(f) - c2.get_feature(f))
	# print "ref get missing:", features
	return Card(features)

def ref_get_set(cards):
	for pset in itertools.combinations(cards, NTYPES):
		if ref_is_set(pset):
			return pset
	return []

def ref_print_all_sets(cards):
	for pset in itertools.combinations(cards, NTYPES):
		if ref_is_set(pset):
			print pset

# for n in xrange(100):
#   c1 = get_random_card()
#   c2 = get_random_card()
#   c3 = ref_get_missing([c1, c2])
#   if not ref_is_set([c1, c2, c3]):
#     print "got this wrong: ", c1, c2, c3



# print 1.0/79

# n = 0.0
# t = 10000000
# start = time.time()
# for x in xrange(t):
# 	c = random.sample(d, NTYPES)
# 	if ref_is_set(c):
# 		n += 1
# end = time.time()

# print n / t
# print end-start, "s"



# a = range(100000)
# start = time.time()
# for x in xrange(1000):
# 	b = random.sample(a, 1000)
# print time.time() - end

# for x in xrange(1000):
# 	b = []
# 	for y in xrange(1000):
# 		b.append(random.choice(a))

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
		for c in self.by_card:
			print c, ": ", sorted(self.by_card[c])

	def print_by_missing(self):
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
		print "remove update with cards: ", cards
		# self.print_by_missing()
		# self.print_by_card()
		remove_from_missing = {}
		for c in cards:
			if c in self.by_card:
				for m in self.by_card[c]:
					remove_from_missing[m] = 1

		# print " "
		print "removing: ", sorted(remove_from_missing.keys())
		for r in remove_from_missing.keys():
			if r in self.by_missing:
				if len(self.by_missing[r]) == 1:
					del self.by_missing[r]
				else:
					self.by_missing[r].pop(0)
		for c in cards:
			if c in self.by_card:
				del self.by_card[c]
		print " "
		self.print_by_missing()
		self.print_by_card()
		# print "removing: ", card
		# print "missing: ", sorted(self.by_missing.keys())
		# print "by card: ", sorted(self.by_card.keys())
		# print "missing to removes: ", sorted(self.by_card[card])
		# for m in self.by_card[card]:
		# 	del self.by_missing[m]
		# del self.by_card[card]

	def make_set(self, card):
		pset = [card]
		print "make set: ", self.by_missing[card]
		# get first cards that make set
		#self.by_missing[card][0]
		pset += self.by_missing[card][0]
		print "pset: ", pset
		self.remove_update(pset)
		# for c in self.by_missing[card]:
		# 	print c
		# 	pset = pset + [c]
		# 	self.remove_update(c)
		print "returning ----------------------------------------------------------------"
		return self.found(pset)

	def get_set(self, board):
		print "----------------------------------------------------------------"
		print "getting set"
		# print board
		# print sorted(self.by_card.keys())
		self.start_time()
		# print "board:"
		# print board
		if not self.by_missing:
			self.generate_missing(board)
			# print self.by_missing
			# print self.by_card
			# print self.by_card
			# print "keys: ", self.by_missing.keys()
			# for k in self.by_missing.keys():
			# 	print type(k)
			# 	print k.__hash__()
			for c in board:
				# print "card features: ", c.features
				# print "card: ", c
				# print type(c)

				# print c in self.by_missing
				if c in self.by_missing:
					# print self.by_missing[c]
					# print "found candidate: ", c
					return self.make_set(c)
		# got new cards
		elif board[-1] not in self.by_card:
			print "sets:"
			ref_print_all_sets(board)
			print "-----"

			l = len(board)
			for i in range(l):
				card = board[i]
				if card in self.by_missing:
					print "card finishes a set", card
					return self.make_set(card)
				# not in self.by_missing
				if card not in self.by_card:
					print "card not in by_card, add to missing and by_card", card
					for others in itertools.combinations(board[:i], NTYPES-2):
						self.add_missing([card] + list(others))
				else:
					print "card already in by_card", card


			#######################################################################
			# TODO: check if set entirely within old card
			# print "last not in by_card"
			# print "sets: "
			# ref_print_all_sets(board)
			# print "----"
			# l = len(board)
			# for i in range(l-NTYPES, l):
			# # for card in board[:-(NTYPES+1):-1]:
			# 	card = board[i]
			# 	print "card: ", card
			# 	print sorted(self.by_missing.keys())
			# 	# is a card that finishes a set
			# 	if card in self.by_missing:
			# 		print "new card finishes a set"
			# 		return self.make_set(card)
			# 	else:
			# 		print "new card doesn't finish set"
			# 		for others in itertools.combinations(board[:i], NTYPES-2):
			# 			self.add_missing([card] + list(others))


		# for card in board[::-1]:
		# 	if card in self.by_missing:

		# 		return


		# 	for m in self.by_missing:
		# 		print m, " - ", self.by_missing[m]
		# 	for c in self.by_card:
		# 		print c, " - ", self.by_card[c]
		return self.found([])

	def add_missing(self, almost):
		# print almost
		almost = list(almost)
		# print almost
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
		# print "generating missing"
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
			# self.print_state()
			print "---------------------------------------------------------"
			print "Player finding set from board: ", sorted(self.board)
			next_set = self.player.get_set(self.board)
			print "Player found set: " + str(next_set)
			if len(next_set) == 0:
				if not self.no_sets():
					print "player wrongly said no set"
					break
				else:
					self.deal(3)
					continue
			if not ref_is_set(next_set):
				print "player got wrong set: " + str(next_set)
				break
			else:
				self.remove_cards(next_set)
				if len(self.board) < NSTART:
					self.deal(3)
		return self.player.get_time()
		# self.print_state()

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
	g = Game(RecencyPlayer())
	t += g.play_game()
print t
print t/n

a = {}
b = 0
for n in xrange(5):
	b = get_random_card()
	a[b] = n
print a
print b
print b in a

c = Card([1, 2, 3, 4])
a[c] = 5

d = Card([1, 2, 3, 4])
print c == d
print d in a

