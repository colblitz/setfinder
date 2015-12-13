import itertools
import random
import time

class Card(object):
	def __init__(self, features):
		self.features = features

	def get_feature(self, n):
		return self.features[n]

	def __repr__(self):
		return "".join([str(f) for f in self.features])

	def __eq__(self, other):
		return self.features == other.features

NFEATURES = 4
NTYPES = 3
NSTART = 12

RFEATURES = range(NFEATURES)
RTYPES = range(NTYPES)

def generate_deck():
	d = [Card(c) for c in itertools.product(RTYPES, repeat=NFEATURES)]
	random.shuffle(d)
	return d

d = generate_deck()
# print d
# print len(d)

def ref_is_set(cards):
	for f in RFEATURES:
		s = {}
		for c in cards:
			s[c.get_feature(f)] = True
		if len(s) != NTYPES and len(s) != 1:
			return False
	return True

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

class Player(object):
	def __init__(self):
		self.time = 0

	def get_set(self, board):
		raise NotImplementedError("get_set not implemented for " + type(self).__name__)

	def get_time(self):
		return self.time

class BaselinePlayer(Player):
	def __init__(self):
		self.time = 0
		self.start = 0

	def get_set(self, board):
		self.start = time.time()
		for pset in itertools.combinations(board, NTYPES):
			if ref_is_set(pset):
				return self.found(pset)
		return self.found([])

	def found(self, pset):
		self.time += time.time() - self.start
		return pset

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
n = 1000
for x in xrange(n):
	g = Game(BaselinePlayer())
	t += g.play_game()
print t
print t/n
