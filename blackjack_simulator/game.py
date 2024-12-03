# blackjack_simulator/game.py

import random
import itertools
from collections import deque
from blackjack_simulator.config import config

class Card:
    """Represents a single playing card."""
    def __init__(self, rank):
        self.rank = rank
        self.value = config['CARD_VALUES'][rank]

    def __str__(self):
        return self.rank

class Deck:
    """Represents the dealer's shoe containing multiple decks."""
    def __init__(self):
        self.cards = deque()
        self.num_decks = config['NUM_DECKS']
        self.create_shoe()

    def create_shoe(self):
        single_deck = [Card(rank) for rank in config['CARD_VALUES'].keys()] * 4
        shoe = single_deck * self.num_decks
        random.shuffle(shoe)
        self.cards = deque(shoe)

    def deal_card(self):
        if len(self.cards) == 0:
            self.create_shoe()
        return self.cards.popleft()

    def needs_reshuffle(self):
        return len(self.cards) < self.num_decks * 52 * (1 - config['DECK_PENETRATION'])

class Hand:
    """Represents a player's hand."""
    def __init__(self, bet):
        self.cards = []
        self.bet = bet
        self.resolved = False
        self.result = None
        self.outcome = None

    def add_card(self, card):
        self.cards.append(card)

    def hand_value(self):
        value = 0
        aces = 0
        for card in self.cards:
            card_value = card.value
            if card.rank == 'A':
                aces += 1
            value += card_value
        while value > 21 and aces:
            value -= 10  # Count Ace as 1 instead of 11
            aces -= 1
        return value

    def is_blackjack(self):
        return self.hand_value() == 21 and len(self.cards) == 2

    def is_busted(self):
        return self.hand_value() > 21

    def can_split(self):
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank

class Player:
    """Represents a player in the game."""
    def __init__(self, player_id, aggressiveness):
        self.id = player_id
        self.bankroll = config['STARTING_BANKROLL']
        self.starting_aggressiveness = aggressiveness
        self.aggressiveness = aggressiveness  # This will change during the game
        self.aggressiveness_history = []  # Record aggressiveness before each round
        self.current_bet = 0
        self.hands = []
        self.eliminated = False
        self.total_bet_amount = 0  # For tracking average bet amount
        self.bet_count = 0         # For tracking the number of bets placed
        self.bet_amounts_per_round = []  # For tracking bet amounts per round

    def place_bet(self, max_bet, round_num, previous_bets=None):
        if previous_bets is None:
            previous_bets = []

        if max_bet is None:
            max_bet = self.bankroll  # Unlimited betting in the last round
        bet_range = max_bet - config['MIN_BET']

        # Adjust aggressiveness based on previous bets if the feature is enabled
        if config['SEE_OTHER_BETS_DURING_BETTING'] and previous_bets:
            # Example strategy: Adjust aggressiveness based on previous bets
            average_previous_bet = sum(bet for _, bet in previous_bets) / len(previous_bets)
            if average_previous_bet > config['MIN_BET'] * 2:
                self.aggressiveness += 0.1  # Increase aggressiveness slightly
                self.aggressiveness = min(self.aggressiveness, 1.0)
            elif average_previous_bet < config['MIN_BET'] * 1.5:
                self.aggressiveness -= 0.1  # Decrease aggressiveness slightly
                self.aggressiveness = max(self.aggressiveness, 0.0)

        bet = config['MIN_BET'] + bet_range * self.aggressiveness
        bet = min(bet, self.bankroll)  # Can't bet more than current bankroll

        # Round bet to nearest multiple of BET_INCREMENT
        bet = int(round(bet / config['BET_INCREMENT'])) * config['BET_INCREMENT']
        bet = max(config['MIN_BET'], bet)  # Ensure bet is at least MIN_BET

        # Adjust bet if it ends with 5 (not allowed)
        if bet % 10 == 5:
            bet += 5  # Increase to next multiple of 10

        # Ensure bet does not exceed bankroll
        bet = min(bet, self.bankroll)

        self.current_bet = bet

        # Update bet tracking
        self.total_bet_amount += bet
        self.bet_count += 1

        # Update bet amounts per round
        self.bet_amounts_per_round.append(bet)

        return bet

    def adjust_aggressiveness(self, max_bankroll, bankroll_range):
        relative_position = (max_bankroll - self.bankroll) / bankroll_range
        # Adjust aggressiveness between 0 and 1
        self.aggressiveness = min(1.0, max(0.0, self.starting_aggressiveness + relative_position * 0.5))

    def is_active(self):
        return not self.eliminated and self.bankroll >= config['MIN_BET']

class Dealer:
    """Represents the dealer."""
    def __init__(self, deck):
        self.hand = Hand(bet=0)
        self.deck = deck

    def play_hand(self):
        while self.hand.hand_value() < 17:
            self.hand.add_card(self.deck.deal_card())

class Game:
    """Manages the overall game logic."""
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.dealer = Dealer(self.deck)
        self.round_num = 0

    def play_round(self, max_bet):
        self.round_num += 1
        betting_order = list(range(len(self.players)))
        # Place bets
        previous_bets = []
        for idx in betting_order:
            player = self.players[idx]
            if not player.is_active():
                continue
            player.place_bet(max_bet, self.round_num, previous_bets)
            # Record this player's bet for the next players
            previous_bets.append((player.id, player.current_bet))

        # Deal initial cards
        self.dealer.hand = Hand(bet=0)
        self.dealer.hand.add_card(self.deck.deal_card())
        self.dealer.hand.add_card(self.deck.deal_card())
        dealer_upcard = self.dealer.hand.cards[0]

        for player in self.players:
            if not player.is_active():
                continue
            player.hands = []
            hand = Hand(bet=player.current_bet)
            hand.add_card(self.deck.deal_card())
            hand.add_card(self.deck.deal_card())
            player.hands.append(hand)

        # Players play their hands
        for idx in betting_order:
            player = self.players[idx]
            if not player.is_active():
                continue
            self.play_player_hands(player, dealer_upcard)

        # Dealer plays hand
        self.dealer.play_hand()
        dealer_total = self.dealer.hand.hand_value()

        # Resolve bets
        for player in self.players:
            if not player.is_active():
                continue
            for hand in player.hands:
                if hand.result == 'surrender':
                    continue
                player_total = hand.hand_value()
                bet = hand.bet

                if player_total > 21:
                    outcome = 'lose'
                    player.bankroll -= bet
                elif dealer_total > 21 or player_total > dealer_total:
                    if hand.is_blackjack():
                        outcome = 'blackjack'
                        player.bankroll += bet * 1.5
                    else:
                        outcome = 'win'
                        player.bankroll += bet
                elif player_total == dealer_total:
                    outcome = 'push'
                    # No change in bankroll
                else:
                    outcome = 'lose'
                    player.bankroll -= bet
                hand.outcome = outcome

        # Clear current bets and hands
        for player in self.players:
            player.current_bet = 0
            player.hands = []

    def play_player_hands(self, player, dealer_upcard):
        for hand in player.hands:
            if hand.resolved:
                continue
            if hand.is_blackjack():
                hand.result = 'blackjack'
                hand.resolved = True
                continue

            while not hand.resolved:
                # Collect other players' hands
                other_players_hands = []
                for other_player in self.players:
                    if other_player == player or not other_player.is_active():
                        continue
                    if other_player.hands:
                        other_hand = other_player.hands[0]
                        other_players_hands.append(other_hand.cards)

                can_split = hand.can_split() and player.bankroll >= hand.bet
                can_double = len(hand.cards) == 2 and player.bankroll >= hand.bet
                action = adjusted_strategy(
                    [card.rank for card in hand.cards],
                    dealer_upcard.rank,
                    [[card.rank for card in h] for h in other_players_hands],
                    can_split,
                    can_double
                )
                if action == 'surrender':
                    hand.result = 'surrender'
                    player.bankroll -= hand.bet / 2
                    hand.resolved = True
                elif action == 'split' and can_split:
                    # Split the hand
                    split_card = hand.cards[0]
                    new_hand1 = Hand(bet=hand.bet)
                    new_hand1.add_card(split_card)
                    new_hand1.add_card(self.deck.deal_card())

                    new_hand2 = Hand(bet=hand.bet)
                    new_hand2.add_card(hand.cards[1])
                    new_hand2.add_card(self.deck.deal_card())

                    player.bankroll -= hand.bet
                    # Update bet tracking for split
                    player.total_bet_amount += hand.bet
                    player.bet_count += 1

                    # Update bet amounts per round
                    player.bet_amounts_per_round[-1] += hand.bet

                    player.hands.remove(hand)
                    player.hands.append(new_hand1)
                    player.hands.append(new_hand2)

                    # For Aces, only one additional card is dealt
                    if split_card.rank == 'A':
                        new_hand1.resolved = True
                        new_hand2.resolved = True
                    break  # Move to next hand
                elif action == 'double' and can_double:
                    additional_bet = hand.bet
                    if player.bankroll >= additional_bet:
                        hand.bet += additional_bet
                        player.bankroll -= additional_bet
                        # Update bet tracking for doubling
                        player.total_bet_amount += additional_bet
                        player.bet_count += 1

                        # Update bet amounts per round
                        player.bet_amounts_per_round[-1] += additional_bet

                        hand.add_card(self.deck.deal_card())
                    else:
                        hand.add_card(self.deck.deal_card())
                    hand.resolved = True
                elif action == 'hit':
                    hand.add_card(self.deck.deal_card())
                    if hand.is_busted():
                        hand.resolved = True
                elif action == 'stand':
                    hand.resolved = True
                else:
                    hand.resolved = True  # Default to stand

def adjusted_strategy(player_hand, dealer_upcard, other_players_hands, can_split, can_double):
    total = hand_value(player_hand)
    dealer_value = config['CARD_VALUES'][dealer_upcard]
    is_pair = len(player_hand) == 2 and player_hand[0] == player_hand[1]
    is_soft = 'A' in player_hand and total <= 21

    # Assess other players' hands
    highest_other_total = max([hand_value(hand) for hand in other_players_hands if hand], default=0)

    # Decision logic adjusted to match or beat other players
    if total < highest_other_total and total < 21:
        # Take risks to beat others
        if can_double and total in [9, 10, 11]:
            return 'double'
        elif can_split and is_pair:
            return 'split'
        else:
            return 'hit'
    else:
        # Use basic strategy
        return basic_strategy(player_hand, dealer_upcard, can_split, can_double)

def basic_strategy(player_hand, dealer_upcard, can_split, can_double):
    total = hand_value(player_hand)
    dealer_value = config['CARD_VALUES'][dealer_upcard]
    is_pair = len(player_hand) == 2 and player_hand[0] == player_hand[1]
    is_soft = 'A' in player_hand and total <= 21

    # Surrender Conditions
    if total == 16 and dealer_value in [9, 10, 11]:
        return 'surrender'
    if total == 15 and dealer_value == 10:
        return 'surrender'

    # Splitting Pairs
    if can_split and is_pair:
        pair_card = player_hand[0]
        if pair_card == 'A':
            return 'split'
        elif pair_card == '8':
            return 'split'
        elif pair_card in ['2', '3', '7'] and dealer_value in range(2, 8):
            return 'split'
        elif pair_card == '6' and dealer_value in range(2, 7):
            return 'split'
        elif pair_card == '9' and dealer_value in [2, 3, 4, 5, 6, 8, 9]:
            return 'split'
        elif pair_card == '4' and dealer_value in [5, 6]:
            return 'split'
        # Do not split 5s and 10s

    # Doubling Down
    if can_double:
        if not is_soft:
            if total == 11:
                return 'double'
            elif total == 10 and dealer_value <= 9:
                return 'double'
            elif total == 9 and dealer_value in range(3, 7):
                return 'double'
        else:
            # Soft doubling
            if total == 18 and dealer_value in range(2, 7):
                return 'double'
            elif total == 17 and dealer_value in range(3, 7):
                return 'double'
            elif total == 16 and dealer_value in range(4, 7):
                return 'double'
            elif total == 15 and dealer_value in range(4, 7):
                return 'double'
            elif total == 14 and dealer_value in range(5, 7):
                return 'double'
            elif total == 13 and dealer_value in range(5, 7):
                return 'double'

    # Hit or Stand
    if is_soft:
        # Soft totals
        if total <= 17:
            return 'hit'
        elif total == 18:
            if dealer_value in [9, 10, 11]:
                return 'hit'
            else:
                return 'stand'
        else:
            return 'stand'
    else:
        # Hard totals
        if total >= 17:
            return 'stand'
        elif total <= 11:
            return 'hit'
        elif 12 <= total <= 16:
            if dealer_value >= 7:
                return 'hit'
            else:
                return 'stand'
        else:
            return 'hit'

def hand_value(hand):
    value = 0
    aces = 0
    for card in hand:
        card_value = config['CARD_VALUES'][card]
        if card == 'A':
            aces += 1
        value += card_value
    while value > 21 and aces:
        value -= 10  # Count Ace as 1 instead of 11
        aces -= 1
    return value

def update_aggressiveness(players):
    active_players = [player for player in players if player.is_active()]
    if not active_players:
        return
    bankrolls = [player.bankroll for player in active_players]
    max_bankroll = max(bankrolls)
    min_bankroll = min(bankrolls)
    bankroll_range = max_bankroll - min_bankroll if max_bankroll != min_bankroll else 1
    for player in active_players:
        player.adjust_aggressiveness(max_bankroll, bankroll_range)

def simulate_tournament(aggressiveness_levels=None, num_simulations_per_combination=None):
    if aggressiveness_levels is None:
        aggressiveness_levels = config['AGGRESSIVENESS_VALUES']
    if num_simulations_per_combination is None:
        num_simulations_per_combination = config['NUM_SIMULATIONS_PER_COMBINATION']  # Use value from config

    num_rounds = len(config['MAX_BETS'])  # Number of rounds determined by length of MAX_BETS

    total_wins = {aggr: 0 for aggr in aggressiveness_levels}    # Integer wins per aggressiveness
    total_games = {aggr: 0 for aggr in aggressiveness_levels}   # Total games played per aggressiveness
    aggressiveness_histories = {aggr: [[] for _ in range(num_rounds)] for aggr in aggressiveness_levels}
    bet_amounts_histories = {aggr: [[] for _ in range(num_rounds)] for aggr in aggressiveness_levels}
    final_bankrolls = {aggr: [] for aggr in aggressiveness_levels}  # Collect final bankrolls

    # Data structure to store statistics per combination and per player
    combination_stats = {}  # Key: combo tuple, Value: {aggr_level: {'total_wins': int, 'total_games': int}}

    # Generate unique combinations of aggressiveness levels
    combinations = list(itertools.combinations_with_replacement(aggressiveness_levels, config['NUM_PLAYERS']))
    total_combinations = len(combinations)
    combination_counter = 0

    for combo in combinations:
        combination_counter += 1
        print(f"Simulating combination {combination_counter} of {total_combinations}: Aggressiveness levels {combo}")

        # Initialize stats for this combination
        if combo not in combination_stats:
            combination_stats[combo] = {}
            for aggr in combo:
                if aggr not in combination_stats[combo]:
                    combination_stats[combo][aggr] = {
                        'total_wins': 0,
                        'total_games': 0,
                    }

        for sim in range(num_simulations_per_combination):
            players = [Player(idx, aggressiveness) for idx, aggressiveness in enumerate(combo)]
            game = Game(players)

            # Increment total games for each player's starting aggressiveness
            for player in players:
                total_games[player.starting_aggressiveness] += 1
                combination_stats[combo][player.starting_aggressiveness]['total_games'] += 1  # Increment per combination

            round_num = 0
            while True:
                round_num += 1
                # Collect data before the round
                for player in players:
                    player.aggressiveness_history.append(player.aggressiveness)

                # Reshuffle shoe if penetration reached
                if game.deck.needs_reshuffle():
                    game.deck.create_shoe()

                # Check if any players have positive bankroll
                active_players = [player for player in game.players if player.is_active()]
                if not active_players:
                    break  # End the tournament

                # Update aggressiveness based on current standings
                update_aggressiveness(game.players)

                # Determine maximum bet for the round
                if round_num <= num_rounds:
                    max_bet = config['MAX_BETS'][round_num - 1]
                else:
                    max_bet = config['MAX_BETS'][-1]  # Use last max bet for tiebreaker rounds

                if max_bet is None:
                    max_bet = max(player.bankroll for player in active_players)
                else:
                    max_bet = min(max_bet, max(player.bankroll for player in active_players))

                if max_bet < config['MIN_BET']:
                    break  # No valid bets can be made

                # Play the round
                game.play_round(max_bet)

                # Elimination after round 3
                if round_num == 3:
                    active_players = [player for player in game.players if player.is_active()]
                    if active_players:
                        bankrolls_round3 = [player.bankroll for player in active_players]
                        min_bankroll = min(bankrolls_round3)
                        min_count = sum(1 for player in active_players if player.bankroll == min_bankroll)
                        if min_count == 1:
                            for player in active_players:
                                if player.bankroll == min_bankroll:
                                    player.eliminated = True

                # Remove bankrupt players
                for player in game.players:
                    if player.bankroll < config['MIN_BET']:
                        player.eliminated = True

                # Check for early victory
                active_players = [player for player in game.players if player.is_active()]
                if len(active_players) == 1:
                    break  # One player left, they win

                # If all scheduled rounds are completed and there's no tie, break
                if round_num >= num_rounds:
                    # Check if there is a tie
                    bankrolls = [player.bankroll for player in game.players if player.is_active()]
                    if not bankrolls:
                        break  # No active players left, end the game
                    max_bankroll = max(bankrolls)
                    tied_players = [player for player in game.players if player.bankroll == max_bankroll]
                    if len(tied_players) == 1:
                        break  # Only one player has the highest bankroll
                    # Else, continue to tiebreaker rounds

            # Collect results
            for player in game.players:
                starting_aggr = player.starting_aggressiveness
                final_bankrolls[starting_aggr].append(player.bankroll)

                # Collect aggressiveness histories and bet amounts
                for idx in range(len(player.aggressiveness_history)):
                    aggr_value = player.aggressiveness_history[idx]
                    if idx < num_rounds:
                        aggressiveness_histories[starting_aggr][idx].append(aggr_value)
                        if idx < len(player.bet_amounts_per_round):
                            bet_amount = player.bet_amounts_per_round[idx]
                            bet_amounts_histories[starting_aggr][idx].append(bet_amount)
                        else:
                            bet_amounts_histories[starting_aggr][idx].append(0)

            # Determine winner
            player_bankrolls = [(player.starting_aggressiveness, player.bankroll) for player in game.players]
            max_bankroll = max(bankroll for aggr, bankroll in player_bankrolls)
            winners = [player for player in game.players if player.bankroll == max_bankroll]
            if len(winners) == 1:
                winner_aggr = winners[0].starting_aggressiveness
                total_wins[winner_aggr] += 1  # Only increment if there is a single winner
                combination_stats[combo][winner_aggr]['total_wins'] += 1  # Increment per combination

    # Report results for each combination and each player
    print("\nResults for Each Combination and Each Player:")
    for combo, player_stats in combination_stats.items():
        combo_str = ', '.join([f"{aggr:.2f}" for aggr in combo])
        print(f"\nCombination ({combo_str}):")
        for aggr_level in sorted(player_stats.keys()):
            stats = player_stats[aggr_level]
            wins = stats['total_wins']
            games = stats['total_games']
            win_percentage = (wins / games * 100) if games > 0 else 0
            print(f"  Player with Aggressiveness {aggr_level:.2f}:")
            print(f"    Wins: {wins}; Games: {games}; Wins Percentage: {win_percentage:.2f}%")

    # Report results for all starting aggressiveness levels
    print("\nResults for All Starting Aggressiveness Levels:")
    for level in sorted(aggressiveness_levels):
        print(f"\nStarting Aggressiveness Level {level}:")
        # Calculate average aggressiveness and bet amounts per round
        average_aggressiveness = []
        average_bet_amounts = []
        for round_num in range(num_rounds):
            aggr_values = aggressiveness_histories[level][round_num]
            bet_values = bet_amounts_histories[level][round_num]
            if aggr_values:
                avg_aggr = sum(aggr_values) / len(aggr_values)
                avg_bet = sum(bet_values) / len(bet_values)
                average_aggressiveness.append(avg_aggr)
                average_bet_amounts.append(avg_bet)
            else:
                average_aggressiveness.append(None)
                average_bet_amounts.append(None)
        for round_num, (avg_aggr, avg_bet) in enumerate(zip(average_aggressiveness, average_bet_amounts), start=1):
            if avg_aggr is not None and avg_bet is not None:
                print(f"  Before Round {round_num}: Aggressiveness: {avg_aggr:.2f}, Average Bet: ${avg_bet:.2f}")
            else:
                print(f"  Before Round {round_num}: No data available")
        # Calculate average final bankroll
        if final_bankrolls[level]:
            avg_final_bankroll = sum(final_bankrolls[level]) / len(final_bankrolls[level])
            print(f"  Average Final Bankroll: ${avg_final_bankroll:.2f}")
        else:
            print("  No final bankroll data available")
        # Report wins, games, and win percentage
        wins = total_wins[level]
        games = total_games[level]
        win_percentage = (wins / games * 100) if games > 0 else 0
        print(f"  Wins: {wins}; Games: {games}; Wins Percentage: {win_percentage:.2f}%")

# If this module is run as main, execute the simulation with default parameters
if __name__ == "__main__":
    simulate_tournament()
