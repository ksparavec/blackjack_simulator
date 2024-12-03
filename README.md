# Blackjack Tournament Simulator

Welcome to the **Blackjack Tournament Simulator**! This simulator allows you to model and analyze blackjack tournaments with customizable parameters, providing insights into player strategies and outcomes.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Configurable Parameters](#configurable-parameters)
- [Usage](#usage)
- [Simulation Details](#simulation-details)
- [Output Interpretation](#output-interpretation)
- [Contributing](#contributing)
- [License](#license)

## Introduction

This simulator models a blackjack tournament where multiple players compete against a dealer and each other. Players have adjustable aggressiveness levels that influence their betting strategies. The simulator allows you to run multiple simulations with different configurations to study how various factors affect the tournament outcomes.

## Features

- Simulate blackjack tournaments with customizable rules and settings.
- Configure player aggressiveness levels and observe their impact on performance.
- Optionally allow players to see other players' bets during the betting phase.
- Collect and report detailed statistics on player performance and strategies.
- Analyze the influence of betting strategies on tournament outcomes.

## Requirements

Make sure you have recent version of Python 3 installed. 

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/ksparavec/blackjack_simulator
   ```

2. **Navigate to the Project Directory**

   ```bash
   cd blackjack_simulator
   ```

## Configuration

The simulator's behavior can be customized using the `config.yaml` file located in the project directory. This file allows you to adjust various parameters to suit your simulation needs.

### Configurable Parameters

Below is a detailed explanation of each configurable parameter:

- **`MAX_BETS`**: A list defining the maximum bet allowed in each round of the tournament. The list length determines the number of scheduled rounds.

  ```yaml
  MAX_BETS: [300, 350, 400, 450, 500, None]
  ```

  - **Type**: List of integers or `None`.
  - **Default**: `[300, 350, 400, 450, 500, None]`.
  - **Explanation**: Each element represents the maximum bet for that round. Use `None` for unlimited betting in the final round(s).

- **`STARTING_BANKROLL`**: The initial amount of money each player has at the start of the tournament.

  ```yaml
  STARTING_BANKROLL: 1000
  ```

  - **Type**: Integer.
  - **Default**: `1000`.
  - **Explanation**: Sets the initial bankroll for all players.

- **`MIN_BET`**: The minimum allowable bet in the game.

  ```yaml
  MIN_BET: 10
  ```

  - **Type**: Integer.
  - **Default**: `10`.
  - **Explanation**: Players cannot bet less than this amount.

- **`BET_INCREMENT`**: The increment in which bets can be placed.

  ```yaml
  BET_INCREMENT: 10
  ```

  - **Type**: Integer.
  - **Default**: `10`.
  - **Explanation**: Bets must be in multiples of this increment.

- **`NUM_DECKS`**: The number of standard decks used in the dealer's shoe.

  ```yaml
  NUM_DECKS: 6
  ```

  - **Type**: Integer.
  - **Default**: `6`.
  - **Explanation**: Defines how many decks are combined in the shoe.

- **`DECK_PENETRATION`**: The fraction of the shoe used before reshuffling.

  ```yaml
  DECK_PENETRATION: 0.75
  ```

  - **Type**: Float between `0` and `1`.
  - **Default**: `0.75`.
  - **Explanation**: When this percentage of the shoe is dealt, the shoe is reshuffled.

- **`NUM_PLAYERS`**: The number of players in the tournament.

  ```yaml
  NUM_PLAYERS: 3
  ```

  - **Type**: Integer.
  - **Default**: `3`.
  - **Explanation**: Sets how many players compete in the tournament.

- **`NUM_SIMULATIONS_PER_COMBINATION`**: The number of simulations to run for each combination of aggressiveness levels.

  ```yaml
  NUM_SIMULATIONS_PER_COMBINATION: 100
  ```

  - **Type**: Integer.
  - **Default**: `10`.
  - **Explanation**: Determines the robustness of the statistical results.

- **`AGGRESSIVENESS_VALUES`**: A list of aggressiveness levels to simulate.

  ```yaml
  AGGRESSIVENESS_VALUES: [0.0, 0.1, 0.2, ..., 1.0]
  ```

  - **Type**: List of floats between `0.0` and `1.0`.
  - **Default**: `[0.0, 0.1, 0.2, ..., 1.0]`.
  - **Explanation**: Each value represents a different player aggressiveness level, where `0.0` is least aggressive and `1.0` is most aggressive.

- **`SEE_OTHER_BETS_DURING_BETTING`**: Enables or disables players seeing other players' bets during the betting phase.

  ```yaml
  SEE_OTHER_BETS_DURING_BETTING: True
  ```

  - **Type**: Boolean (`True` or `False`).
  - **Default**: `False`.
  - **Explanation**: When `True`, players can adjust their bets based on the bets already placed by others.

#### Example `config.yaml`

```yaml
MAX_BETS: [100, 200, 500]
STARTING_BANKROLL: 1000
MIN_BET: 10
BET_INCREMENT: 10
NUM_DECKS: 6
DECK_PENETRATION: 0.75
NUM_PLAYERS: 3
NUM_SIMULATIONS_PER_COMBINATION: 100
AGGRESSIVENESS_VALUES: [0.0, 0.25, 0.5, 0.75, 1.0]
SEE_OTHER_BETS_DURING_BETTING: True
```

**Note**: Parameters not specified in `config.yaml` will use their default values from `config.py`.

## Usage

1. **Configure the Simulation**

   - Modify the `config.yaml` file to set your desired simulation parameters.
   - Ensure that all parameters are correctly formatted and valid.

2. **Run the Simulator**

   ```bash
   python blackjack_simulator/game.py
   ```

   - The simulator will execute based on the configurations provided.
   - Progress updates and results will be displayed in the console.

3. **Review the Output**

   - The simulator will output detailed statistics for each aggressiveness level and combination.
   - Analyze the results to gain insights into player strategies and tournament outcomes.

## Simulation Details

- **Tournament Structure**

  - The number of rounds is determined by the length of the `MAX_BETS` list.
  - After the scheduled rounds, if there is a tie, tiebreaker rounds are played with the last maximum bet value.
  - Players are eliminated under certain conditions, such as having the lowest bankroll after specific rounds.

- **Player Aggressiveness**

  - Aggressiveness levels influence betting amounts.
  - Players adjust their aggressiveness based on their relative position in bankroll compared to others.
  - Optionally, players can adjust their bets if they can see other players' bets during the betting phase.

- **Betting Strategy**

  - Bets are calculated based on aggressiveness, bankroll, and game constraints.
  - Bets must be within `MIN_BET` and the maximum allowed bet for the round.
  - Bets are adjusted to be in increments of `BET_INCREMENT`.

- **Playing Strategy**

  - Players follow an adjusted basic strategy for hitting, standing, doubling, splitting, or surrendering.
  - The strategy considers the player's hand, the dealer's upcard, and optionally other players' hands.
  - The goal is to maximize the chance of winning against both the dealer and other players.

## Output Interpretation

- **Combination Results**

  - Displays statistics for each combination of aggressiveness levels.
  - Shows wins, games played, and win percentages for each player in the combination.

- **Aggressiveness Level Results**

  - Provides aggregated results for each starting aggressiveness level across all simulations.
  - Includes average aggressiveness, average bet amounts per round, average final bankroll, and win percentages.

- **Understanding Win Percentages**

  - **Wins**: Number of times a player with a specific aggressiveness level won the tournament.
  - **Games**: Total number of games played by players with that aggressiveness level.
  - **Win Percentage**: `(Wins / Games) * 100`, indicating the success rate.

## Contributing

Contributions are welcome! If you'd like to enhance the simulator or fix issues, please:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes with clear messages.
4. Submit a pull request detailing your changes.

## License

This project is licensed under the [MIT License](LICENSE).

---

**Disclaimer**: This simulator is intended for educational and analytical purposes only. It does not encourage or promote gambling. Always gamble responsibly and be aware of the risks involved.
