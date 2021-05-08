name = 'Efficionado'
color = {'r': 192, 'g': 192, 'b': 224}

class State:
    categories = None

def highest_eff(dice):
    best_category = None
    best_eff = -1
    for category in game.categories:
        if category in State.categories: continue
        eff = dice.score(category) / game.category_max_score[category]
        if eff > best_eff:
            best_eff = eff
            best_category = category
    return best_category

def play(stage, dice, opponent, new_game):
    if new_game: State.categories = set()
    category = highest_eff(dice)
    if stage != 3 and category not in ['full_house', 'large_straight', 'yahtzee']:
        index = game.categories.index(category)
        if index < 6:
            dice.save_where(lambda value: value == index + 1)
        elif 'of_a_kind' in category:
            save_value = max(range(1, 7), key=lambda i: dice.count(i))
            dice.save_where(lambda value: value == save_value)
        elif 'straight' in category:
            for i in dice.straight(): dice[i].save()
        elif category == 'chance':
            dice.save_where(lambda value: value > 3)
        return {'save_dice': dice.saved()}
    else:
        State.categories.add(category)
        return {'category': category}
