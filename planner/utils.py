import random
from datetime import date

def weighted_random_activity(activities):
    if(len(activities)==0):
        return None
    today = date.today()
    weights = []
    for activity in activities:
        if activity.deadline:
            days_left = (activity.deadline - today).days
            weight = 1 / max(days_left, 1)
        else:
            weight = 0.1
        weights.append(weight)

    total = sum(weights)
    if total == 0:
        weights = [1 for _ in activities]
    else:
        weights = [w / total for w in weights]

    chosen = random.choices(list(activities), weights=weights, k=1)  # k=1 as keyword
    return chosen[0] if chosen else None
