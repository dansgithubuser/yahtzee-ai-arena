name = 'Yahtzeebot'
color = {'r': 255, 'g': 64, 'b': 32}

class State:
    categories = None

def play(stage, dice, opponent, new_game):
    if new_game: State.categories = set()
    if stage != 3:
        save_value = max(range(1, 7), key=lambda i: dice.count(i))
        for die in dice:
            if die.value == save_value:
                die.save()
        return {'save_dice': dice.saved()}
    else:
        _, category = dice.score_best(avoid=State.categories)
        State.categories.add(category)
        return {'category': category}
