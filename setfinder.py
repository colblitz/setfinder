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
		self.features = features

	def get_feature(self, n):
		return self.features[n]

	def __repr__(self):
		return "".join([str(f) for f in self.features])

	def __eq__(self, other):
		return self.features == other.features

	def __hash__(self):
		return hash(sum(a*b for a,b in zip(RBASE, self.features)))

def generate_deck():
	d = [Card(c) for c in itertools.product(RTYPES, repeat=NFEATURES)]
	random.shuffle(d)
	return d

d = generate_deck()
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
	print cards, " is a set"
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
	return Card(features)

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

	def remove_update(self, card):
		for m in self.by_card[card]:
			del self.by_missing[m]
		del self.by_card[card]

	def make_set(self, card):
		pset = [card]
		for c in self.by_missing[card]:
			pset += c
			self.remove_update(c)
		return self.found(pset)

	def get_set(self, board):
		self.start_time()
		print "board:"
		print board
		if not self.by_missing:
			self.generate_missing(board)
			print self.by_missing.keys()
			print self.by_card
			for c in board:
				print c
				if c in self.by_missing:
					print self.by_missing[c]
					return make_set(c)
		# got new cards
		elif board[-1] not in self.by_card:
			l = len(board)
			for i in range(l-NTYPES, l):
			# for card in board[:-(NTYPES+1):-1]:
				card = board[i]
				# is a card that finishes a set
				if card in self.by_missing:
					return make_set(card)
				else:
					for others in itertools.combinations(board[:i], NTYPES-2):
						self.add_missing([card] + list(others))


		# for card in board[::-1]:
		# 	if card in self.by_missing:

		# 		return


		# 	for m in self.by_missing:
		# 		print m, " - ", self.by_missing[m]
		# 	for c in self.by_card:
		# 		print c, " - ", self.by_card[c]
		return self.found([])

	def add_missing(self, almost):
		missing = ref_get_missing(almost)
		self.by_missing[missing] = list(almost)
		for c in almost:
			if c not in self.by_card:
				self.by_card[c] = []
			self.by_card[c].append(missing)

	def generate_missing(self, board):
		print "generating missing"
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
			next_set = self.player.get_set(self.board)
			# print "Found set: " + str(next_set)
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



