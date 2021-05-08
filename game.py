import random

class Die:
    def __init__(self, value=None):
        if value:
            self.value = value
        self.saved = False

    def __eq__(self, value):
        return self.value == value

    def roll(self):
        self.value = random.randint(1, 6)

    def save(self):
        self.saved = True

    def unsave(self):
        self.saved = False

class Dice:
    def __init__(self, values=None):
        if values:
            self.dice = [Die(i) for i in values]
        else:
            self.dice = [Die() for i in range(5)]

    def __str__(self):
        return ''.join([
            f'{{{die.value}}}' if die.saved else f'[{die.value}]'
            for die in self.dice
        ])

    def __getitem__(self, i):
        return self.dice[i]

    def values(self):
        return [die.value for die in self.dice]

    def roll(self):
        for die in self.dice:
            if not die.saved:
                die.roll()
        return self.values()

    def saved(self):
        return [i for i, die in enumerate(self.dice) if die.saved]

    def sum(self):
        return sum(self.values())

    def count(self, value):
        return self.dice.count(value)

    def score(self, category):
        return getattr(self, f'score_{category}')()

    def score_best(self, avoid=[]):
        return max(
            (self.score(category), category)
            for category in categories
            if category not in avoid
        )

    def score_aces(self):
        return 1 * self.count(1)

    def score_twos(self):
        return 2 * self.count(2)

    def score_threes(self):
        return 3 * self.count(3)

    def score_fours(self):
        return 4 * self.count(4)

    def score_fives(self):
        return 5 * self.count(5)

    def score_sixes(self):
        return 6 * self.count(6)

    def score_three_of_a_kind(self):
        for die in self.dice[:3]:
            if self.count(die.value) >= 3:
                return self.sum()
        return 0

    def score_four_of_a_kind(self):
        for die in self.dice[:2]:
            if self.count(die.value) >= 4:
                return self.sum()
        return 0

    def score_full_house(self):
        if self.score_yahtzee(): return 25
        s = sorted(die.value for die in self.dice)
        if s[0] != s[1]: return 0
        if s[3] != s[4]: return 0
        if s[2] not in [s[1], s[3]]: return 0
        return 25

    def score_small_straight(self):
        if self.score_yahtzee(): return 30
        run = 0
        for i in range(1, 7):
            if self.count(i):
                run += 1
                if run >= 4: return 30
            else:
                run = 0
        return 0

    def score_large_straight(self):
        if self.score_yahtzee(): return 40
        run = 0
        for i in range(1, 7):
            if self.count(i):
                run += 1
                if run >= 5: return 40
            else:
                run = 0
        return 0

    def score_yahtzee(self):
        if self.count(self.dice[0].value) == 5: return 50
        return 0

    def score_chance(self):
        return self.sum()

categories = [
    'aces',
    'twos',
    'threes',
    'fours',
    'fives',
    'sixes',
    'three_of_a_kind',
    'four_of_a_kind',
    'full_house',
    'small_straight',
    'large_straight',
    'yahtzee',
    'chance',
]

category_max_score = {
    'aces': 5,
    'twos': 10,
    'threes': 15,
    'fours': 20,
    'fives': 25,
    'sixes': 30,
    'three_of_a_kind': 30,
    'four_of_a_kind': 30,
    'full_house': 25,
    'small_straight': 30,
    'large_straight': 40,
    'yahtzee': 50,
    'chance': 30,
}
