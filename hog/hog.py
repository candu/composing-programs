"""The Game of Hog."""

from dice import four_sided, six_sided, make_test_dice
from ucb import main, trace, log_current_line, interact

GOAL_SCORE = 100 # The goal of Hog is to score 100 points.

######################
# Phase 1: Simulator #
######################

# Taking turns

def roll_dice(num_rolls, dice=six_sided):
    """Roll DICE for NUM_ROLLS times.  Return either the sum of the outcomes,
    or 1 if a 1 is rolled (Pig out). This calls DICE exactly NUM_ROLLS times.

    num_rolls:  The number of dice rolls that will be made; at least 1.
    dice:       A zero-argument function that returns an integer outcome.
    """
    # These assert statements ensure that num_rolls is a positive integer.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'
    total = 0
    had_one = False
    for i in range(num_rolls):
        roll = dice()
        if roll == 1:
            had_one = True
        total += roll
    if had_one:
        return 1
    return total

def take_bacon(opponent_score):
    return max(opponent_score % 10, opponent_score // 10) + 1

def take_turn(num_rolls, opponent_score, dice=six_sided):
    """Simulate a turn rolling NUM_ROLLS dice, which may be 0 (Free bacon).

    num_rolls:       The number of dice rolls that will be made.
    opponent_score:  The total score of the opponent.
    dice:            A function of no args that returns an integer outcome.
    """
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    assert opponent_score < 100, 'The game should be over.'
    if num_rolls == 0:
        return take_bacon(opponent_score)
    return roll_dice(num_rolls, dice)

# Playing a game

def select_dice(score, opponent_score):
    """Select six-sided dice unless the sum of SCORE and OPPONENT_SCORE is a
    multiple of 7, in which case select four-sided dice (Hog wild).

    >>> select_dice(4, 24) == four_sided
    True
    >>> select_dice(16, 64) == six_sided
    True
    >>> select_dice(0, 0) == four_sided
    True
    """
    total_score = score + opponent_score
    if total_score % 7 == 0:
        return four_sided
    return six_sided

def other(who):
    """Return the other player, for a player WHO numbered 0 or 1.

    >>> other(0)
    1
    >>> other(1)
    0
    """
    return 1 - who

def play(strategy0, strategy1, goal=GOAL_SCORE):
    """Simulate a game and return the final scores of both players, with
    Player 0's score first, and Player 1's score second.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    strategy0:  The strategy function for Player 0, who plays first.
    strategy1:  The strategy function for Player 1, who plays second.
    """
    who = 0  # Which player is about to take a turn, 0 (first) or 1 (second)
    score0, score1 = 0, 0
    while max(score0, score1) < goal:
        if who == 0:
            dice = select_dice(score0, score1)
            num_rolls = strategy0(score0, score1)
            points = take_turn(num_rolls, score1, dice)
            score0 += points
            who = 1
        else:
            dice = select_dice(score1, score0)
            num_rolls = strategy1(score1, score0)
            points = take_turn(num_rolls, score0, dice)
            score1 += points
            who = 0
        if score0 == 2 * score1 or score1 == 2 * score0:
            # swine swap
            score0, score1 = score1, score0
    return score0, score1

#######################
# Phase 2: Strategies #
#######################

# Basic Strategy

BASELINE_NUM_ROLLS = 5
BACON_MARGIN = 8

def always_roll(n):
    """Return a strategy that always rolls N dice.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    >>> strategy = always_roll(5)
    >>> strategy(0, 0)
    5
    >>> strategy(99, 99)
    5
    """
    def strategy(score, opponent_score):
        return n
    return strategy

# Experiments

def make_averaged(fn, num_samples=1000):
    """Return a function that returns the average_value of FN when called.

    To implement this function, you will have to use *args syntax, a new Python
    feature introduced in this project.  See the project description.

    >>> dice = make_test_dice(3, 1, 5, 6)
    >>> averaged_dice = make_averaged(dice, 1000)
    >>> averaged_dice()
    3.75
    >>> make_averaged(roll_dice, 1000)(2, dice)
    6.0

    In this last example, two different turn scenarios are averaged.
    - In the first, the player rolls a 3 then a 1, receiving a score of 1.
    - In the other, the player rolls a 5 and 6, scoring 11.
    Thus, the average value is 6.0.
    """
    def averaged(*args):
        return sum(fn(*args) for i in range(num_samples)) / num_samples
    return averaged

def max_scoring_num_rolls(num_iters, dice=six_sided):
    """Return the number of dice (1 to 10) that gives the highest average turn
    score by calling roll_dice with the provided DICE.  Print all averages as in
    the doctest below.  Assume that dice always returns positive outcomes.

    >>> dice = make_test_dice(3)
    >>> max_scoring_num_rolls(1000, dice)
    1 dice scores 3.0 on average
    2 dice scores 6.0 on average
    3 dice scores 9.0 on average
    4 dice scores 12.0 on average
    5 dice scores 15.0 on average
    6 dice scores 18.0 on average
    7 dice scores 21.0 on average
    8 dice scores 24.0 on average
    9 dice scores 27.0 on average
    10 dice scores 30.0 on average
    10
    """
    best_score = 0
    best = 0
    averaged = make_averaged(roll_dice, num_iters)
    for num_dice in range(1, 11):
        score = averaged(num_dice, dice)
        print('%d dice scores %.1f on average' % (num_dice, score))
        if score > best_score:
            best_score = score
            best = num_dice
    return best

def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""
    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    else:
        return 1

def average_win_rate(num_iters, strategy, baseline=always_roll(BASELINE_NUM_ROLLS)):
    """Return the average win rate (0 to 1) of STRATEGY against BASELINE."""
    win_rate_as_player_0 = 1 - make_averaged(winner, num_iters)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner, num_iters)(baseline, strategy)
    return (win_rate_as_player_0 + win_rate_as_player_1) / 2 # Average results

def run_experiments(num_iters):
    """Run a series of strategy experiments and report results."""
    if False: # Change to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(num_iters, six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)
        four_sided_max = max_scoring_num_rolls(num_iters, four_sided)
        print('Max scoring num rolls for four-sided dice:', four_sided_max)

    if False: # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(num_iters, always_roll(8)))

    if False: # Change to True to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(num_iters, bacon_strategy))

    if False: # Change to True to test swap_strategy
        print('swap_strategy win rate:', average_win_rate(num_iters, swap_strategy))

    if True: # Change to True to test final_strategy
        print('final_strategy win rate:', average_win_rate(num_iters, final_strategy))

    "*** You may add additional experiments as you wish ***"

# Strategies

def bacon_strategy(score, opponent_score):
    """This strategy rolls 0 dice if that gives at least BACON_MARGIN points,
    and rolls BASELINE_NUM_ROLLS otherwise.

    >>> bacon_strategy(0, 0)
    5
    >>> bacon_strategy(70, 50)
    5
    >>> bacon_strategy(50, 70)
    0
    """
    bacon = take_bacon(opponent_score)
    if bacon >= BACON_MARGIN:
      return 0
    return BASELINE_NUM_ROLLS

def swap_strategy(score, opponent_score):
    """This strategy rolls 0 dice when it would result in a beneficial swap and
    rolls BASELINE_NUM_ROLLS if it would result in a harmful swap. It also rolls
    0 dice if that gives at least BACON_MARGIN points and rolls
    BASELINE_NUM_ROLLS otherwise.

    >>> swap_strategy(23, 60) # 23 + (1 + max(6, 0)) = 30: Beneficial swap
    0
    >>> swap_strategy(27, 18) # 27 + (1 + max(1, 8)) = 36: Harmful swap
    5
    >>> swap_strategy(50, 80) # (1 + max(8, 0)) = 9: Lots of free bacon
    0
    >>> swap_strategy(12, 12) # Baseline
    5
    """
    bacon = take_bacon(opponent_score)
    if opponent_score == 2 * (score + bacon):
      return 0
    elif (score + bacon) == 2 * opponent_score:
      return BASELINE_NUM_ROLLS
    if bacon >= BACON_MARGIN:
      return 0
    return BASELINE_NUM_ROLLS

def make_distribution(fn, num_samples=1000):
    """Return a function that returns the observed probability distribution of
    FN when called.  The return value is a mapping d = {x: p(x)}.

    >>> dice = make_test_dice(3, 3, 5, 6)
    >>> dist_dice = make_distribution(dice, 1000)
    >>> list(sorted(dist_dice().items()))
    [(3, 0.5), (5, 0.25), (6, 0.25)]
    """
    def distribution(*args):
      d = {}
      for i in range(num_samples):
        x = fn(*args)
        if x not in d:
          d[x] = 0
        d[x] += 1
      for x in d:
        d[x] /= num_samples
      return d
    return distribution

def compute_score(score, opponent_score, x):
    """Compute the new score if this player scores x points.

    >>> compute_score(15, 10, 5)
    10
    >>> compute_score(15, 40, 5)
    40
    >>> compute_score(23, 26, 5)
    28
    """
    new_score = score + x
    if new_score == 2 * opponent_score:
      return opponent_score
    if opponent_score == 2 * new_score:
      return opponent_score
    # NOTE: if we leave our opponent with 1 point less than half our score on
    # their turn, their obvious best move is to roll 10 dice.
    if new_score == 2 * (opponent_score + 1):
      return opponent_score + 1
    # NOTE: if we leave our opponent with <bacon> less than half our score on
    # their turn, their obvious best move is to roll 0 dice and take bacon.
    new_bacon = take_bacon(new_score)
    if new_score == 2 * (opponent_score + new_bacon):
      return opponent_score + new_bacon
    return new_score

def compute_expected_score(score, opponent_score, d):
    """Compute the new expected score if this player performs an action
    with probability distribution d.

    >>> compute_expected_score(10, 0, {32: 1.0})
    42.0
    >>> compute_expected_score(15, 40, {5: 0.25, 1: 0.75})
    22.0
    >>> compute_expected_score(15, 10, {5: 0.5, 1: 0.5})
    13.0
    """
    expected_score = 0
    for x, p in d.items():
      partial_score = compute_score(score, opponent_score, x)
      expected_score += partial_score * p
    return expected_score

FOUR_SIDED_VALUE = 3

def compute_four_sided_p(score, opponent_score, d):
    """Compute the probability of leaving the opponent with four-sided dice.

    >>> compute_four_sided_p(12, 15, {1: 1.0})
    1.0
    >>> compute_four_sided_p(12, 15, {1: 0.75, 5: 0.25})
    0.75
    >>> compute_four_sided_p(12, 15, {1: 0.25, 5: 0.25, 8: 0.25, 10: 0.25})
    0.5
    """
    four_sided_p = 0
    for x, p in d.items():
      if (score + x + opponent_score) % 7 == 0:
        four_sided_p += p
    return four_sided_p

def compute_heuristic_score(score, opponent_score, d):
    expected_score = compute_expected_score(score, opponent_score, d)
    four_sided_p = compute_four_sided_p(score, opponent_score, d)
    return expected_score + four_sided_p * FOUR_SIDED_VALUE

d_dist = make_distribution(roll_dice, 10000)
d_four_sided = None
d_six_sided = None

def build_distribution_tables():
    print('building distribution tables...')
    global d_four_sided
    global d_six_sided
    d_four_sided = [None] * 11
    d_six_sided = [None] * 11
    for num_rolls in range(1, 11):
        print('%d rolls...' % (num_rolls, ))
        d_four_sided[num_rolls] = d_dist(num_rolls, four_sided)
        d_six_sided[num_rolls] = d_dist(num_rolls, six_sided)
    print('done.')

def get_distribution(num_rolls, dice):
    if d_four_sided is None or d_six_sided is None:
      build_distribution_tables()
    if dice == four_sided:
        return d_four_sided[num_rolls]
    elif dice == six_sided:
        return d_six_sided[num_rolls]
    else:
        return d_dist(num_rolls, dice)

def final_strategy(score, opponent_score):
    """This strategy models the probability distribution of scores for each
    possible move, then uses those distributions to compute the move with the
    best expected score.

    We apply some additional heuristics that were found to improve
    average win rates:

    - it is better to force the opponent to roll four-sided dice;
    - it is bad to leave the opponent with one point less than half your score;
    - it is bad to leave the opponent with <bacon> less than half your score.
    """
    bacon = take_bacon(opponent_score)
    # NOTE: a 0-roll move is the same as taking "bacon" with probability 1
    best_new_score = compute_expected_score(score, opponent_score, {bacon: 1})
    best_num_rolls = 0
    dice = select_dice(score, opponent_score)
    for num_rolls in range(1, 11):
        d = get_distribution(num_rolls, dice)
        new_score = compute_expected_score(score, opponent_score, d)
        if new_score > best_new_score:
            best_new_score = new_score
            best_num_rolls = num_rolls
    return best_num_rolls


##########################
# Command Line Interface #
##########################

# Note: Functions in this section do not need to be changed.  They use features
#       of Python not yet covered in the course.

def get_int(prompt, min):
    """Return an integer greater than or equal to MIN, given by the user."""
    choice = input(prompt)
    while not choice.isnumeric() or int(choice) < min:
        print('Please enter an integer greater than or equal to', min)
        choice = input(prompt)
    return int(choice)

def interactive_dice():
    """A dice where the outcomes are provided by the user."""
    return get_int('Result of dice roll: ', 1)

def make_interactive_strategy(player):
    """Return a strategy for which the user provides the number of rolls."""
    prompt = 'Number of rolls for Player {0}: '.format(player)
    def interactive_strategy(score, opp_score):
        if player == 1:
            score, opp_score = opp_score, score
        print(score, 'vs.', opp_score)
        choice = get_int(prompt, 0)
        return choice
    return interactive_strategy

def roll_dice_interactive():
    """Interactively call roll_dice."""
    num_rolls = get_int('Number of rolls: ', 1)
    turn_total = roll_dice(num_rolls, interactive_dice)
    print('Turn total:', turn_total)

def take_turn_interactive():
    """Interactively call take_turn."""
    num_rolls = get_int('Number of rolls: ', 0)
    opp_score = get_int('Opponent score: ', 0)
    turn_total = take_turn(num_rolls, opp_score, interactive_dice)
    print('Turn total:', turn_total)

def play_interactive():
    """Interactively call play."""
    strategy0 = make_interactive_strategy(0)
    strategy1 = make_interactive_strategy(1)
    score0, score1 = play(strategy0, strategy1)
    print('Final scores:', score0, 'to', score1)

@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions.

    This function uses Python syntax/techniques not yet covered in this course.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--interactive', '-i', type=str,
                        help='Run interactive tests for the specified question')
    parser.add_argument('--run_experiments', '-r', action='store_true',
                        help='Runs strategy experiments')
    parser.add_argument('--num_iters', '-n', type=int,
                        help='Set number of iterations for win rate',
                        default=1000)
    args = parser.parse_args()

    if args.interactive:
        test = args.interactive + '_interactive'
        if test not in globals():
            print('To use the -i option, please choose one of these:')
            print('\troll_dice', '\ttake_turn', '\tplay', sep='\n')
            exit(1)
        try:
            globals()[test]()
        except (KeyboardInterrupt, EOFError):
            print('\nQuitting interactive test')
            exit(0)
    elif args.run_experiments:
        run_experiments(args.num_iters)
