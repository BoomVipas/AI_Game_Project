import random

class GameState:
    def __init__(self, size=8, players=None, scores=None, coins=None, board=None):
        # Initialize the game state with board size, player positions, scores, coins, and the board itself.
        self.size = size
        if players is None:
            self.players = {'A': (0, 0), 'B': (size - 1, size - 1)}
        else:
            self.players = dict(players)
        if scores is None:
            self.scores = {'A': 0, 'B': 0}
        else:
            self.scores = dict(scores)
        if coins is None:
            self.coins = self.place_coins()
        else:
            self.coins = list(coins)
        self.board = [['.' for _ in range(size)] for _ in range(size)] if board is None else [row[:] for row in board]
        self.update_board()

    def place_coins(self):
        # Randomly place a certain number of coins on the board at the start of the game.
        num_coins = random.randint(15, 24)
        available_positions = [(i, j) for i in range(self.size) for j in range(self.size) if (i, j) not in self.players.values()]
        random.shuffle(available_positions)
        coins = []
        for _ in range(num_coins):
            coin_pos = available_positions.pop()
            coins.append(coin_pos)
        return coins

    def update_board(self):
        # Update the board's display based on the current positions of players and coins.
        for i in range(self.size):
            for j in range(self.size):
                if (i, j) in self.coins:
                    self.board[i][j] = '*'
                else:
                    self.board[i][j] = '.'
        for key, pos in self.players.items():
            self.board[pos[0]][pos[1]] = key

    def print_board(self):
        # Print the current state of the board, showing player positions and coins.
        print("Board state:")
        for row in self.board:
            print(' '.join(row))
        print(f"Scores: {self.scores}\n")

    def available_moves(self, player):
        # Determine available moves for a player based on their current position.
        pos = self.players[player]
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        moves = []
        for dx, dy in directions:
            nx, ny = pos[0] + dx, pos[1] + dy
            if 0 <= nx < self.size and 0 <= ny < self.size and self.board[nx][ny] in ['.', '*']:
                moves.append((nx, ny))
        return moves

    def make_move(self, player, move):
        # Move a player to a new position and update the game state accordingly.
        new_state = GameState(size=self.size, players=self.players.copy(), scores=self.scores.copy(), coins=self.coins.copy(), board=[row[:] for row in self.board])
        new_state.players[player] = move
        if move in new_state.coins:
            new_state.coins.remove(move)
            new_state.scores[player] += 1
        new_state.update_board()
        return new_state

    def is_terminal(self):
        # Check if the game has reached a terminal state where no more moves are possible.
        return not self.coins or all(not self.available_moves(p) for p in ['A', 'B'])

    def utility_function(self, player):
        # Evaluate the utility of the current game state for the specified player.
        opponent = 'B' if player == 'A' else 'A'
        player_dist = self.distance_to_nearest_coin(player)
        opponent_dist = self.distance_to_nearest_coin(opponent)
        return (self.scores[player] - self.scores[opponent]) + (1 / (player_dist + 0.1) - 1 / (opponent_dist + 0.1))

    def distance_to_nearest_coin(self, player):
        # Calculate the Manhattan distance from the specified player to the nearest coin.
        player_pos = self.players[player]
        if not self.coins:
            return float('inf')
        return min(abs(player_pos[0] - coin[0]) + abs(player_pos[1] - coin[1]) for coin in self.coins)

    def calculate_dynamic_depth(self):
        # Adjust the depth of the Minimax search based on the number of coins left to optimize performance.
        num_coins = len(self.coins)
        if num_coins > 15:
            return 4
        elif num_coins > 10:
            return 3
        elif num_coins > 5:
            return 2
        else:
            return 1

    def minimax(self, depth, player, alpha, beta, maximizingPlayer):
        # The Minimax algorithm with alpha-beta pruning.
        if depth == 0 or self.is_terminal():
            return self.utility_function(player), None

        opponent = 'B' if player == 'A' else 'A'
        best_move = None

        if maximizingPlayer:
            max_eval = float('-inf')
            for move in self.available_moves(player):
                new_state = self.make_move(player, move)
                eval, _ = new_state.minimax(depth - 1, opponent, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in self.available_moves(player):
                new_state = self.make_move(player, move)
                eval, _ = new_state.minimax(depth - 1, opponent, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

if __name__ == "__main__":
    game_state = GameState()
    game_state.print_board()
    print("Who do you think will win? (A/B): ")
    user_bet = input().strip().upper()
    current_player = 'A'

    while not game_state.is_terminal():
        dynamic_depth = game_state.calculate_dynamic_depth()  # Adjust Minimax depth dynamically
        score, move = game_state.minimax(dynamic_depth, current_player, float('-inf'), float('inf'), current_player == 'A')
        if move:
            game_state = game_state.make_move(current_player, move)
            print(f"Player {current_player} moves to {move}")
            game_state.print_board()
            current_player = 'B' if current_player == 'A' else 'A'
        else:
            print(f"No valid moves for {current_player}, switching turns.")
            current_player = 'B' if current_player == 'A' else 'A'

    print("Game Over")
    print(f"Final scores: {game_state.scores}")
    winner = 'A' if game_state.scores['A'] > game_state.scores['B'] else 'B'
    print("Winner:", winner)
    if user_bet == winner:
        print("\nCongratulations! Your bet was correct!\n")
    else:
        print("\nSorry, your bet was incorrect.\n")
    print("Made with love, from Vipas\n")
