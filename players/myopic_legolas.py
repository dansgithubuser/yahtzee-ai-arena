name = 'Myopic Legolas'
color = {'r': 255, 'g': 255, 'b': 128}

class State:
    categories = None

def play(stage, dice, opponent, new_game):
    if new_game: State.categories = set()
    if stage != 3:
        best_saves = []
        best_score = -1
        for i in range(32):
            for j, die in enumerate(dice):
                die.saved = i & (1 << j)
            dice.roll()
            score, _ = dice.score_best(avoid=State.categories)
            if score > best_score:
                best_score = score
                best_saves = dice.saved()
        return {'save_dice': best_saves}
    else:
        _, category = dice.score_best(avoid=State.categories)
        State.categories.add(category)
        return {'category': category}
