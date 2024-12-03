# blackjack_simulator/config.py

import yaml
import os

class Config:
    """Handles configuration loading and default constants."""
    DEFAULTS = {
        'MAX_BETS': [300, 350, 400, 450, 500, None],
        'STARTING_BANKROLL': 1000,
        'MIN_BET': 10,
        'BET_INCREMENT': 10,
        'NUM_DECKS': 6,
        'DECK_PENETRATION': 0.75,
        'NUM_PLAYERS': 3,
        'NUM_SIMULATIONS_PER_COMBINATION': 10,
        'AGGRESSIVENESS_VALUES': [round(x * 0.1, 1) for x in range(0, 11)],
        'CARD_VALUES': {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
            '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10,
            'K': 10, 'A': 11
        },
        'SEE_OTHER_BETS_DURING_BETTING': False
    }

    def __init__(self, config_file=None):
        self.config = self.DEFAULTS.copy()
        self.load_config(config_file)

    def load_config(self, config_file):
        if config_file is None:
            # Check if 'config.yaml' exists in the current directory
            config_file = os.path.join(os.getcwd(), 'config.yaml')
            if not os.path.exists(config_file):
                return  # Use default configuration
        try:
            with open(config_file, 'r') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    self.config.update(user_config)
        except Exception as e:
            print(f"Error loading configuration file: {e}")
            # Use default configuration

    def __getitem__(self, item):
        return self.config.get(item)

# Create a singleton instance of Config
config = Config()
