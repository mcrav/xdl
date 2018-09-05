from .utils import get_reagent_combinations

dangerous_combinations = {
    frozenset((67641, 16853853)): 'Acetone and LiAlH4 boom fucking boom!',
    # Alcohols and LiALH4,
}

def procedure_is_safe(steps, reagents):
    safe = True
    combinations = get_reagent_combinations(steps, reagents)
    for combo in combinations:
        if combo in dangerous_combinations:
            print(f'SAFETY WARNING: {dangerous_combinations[combo]}')
            safe = False
    return safe