import random
import copy

class Pacman:
    def __init__(self, position):
        self.position = position


class Ghost:
    def __init__(self, position):
        self.position = position
    




class Game:
    def __init__(self):
        self.score = 0
        self.ghosts = []
        self.generate_board()


    def generate_board(self):
        self.board = [['.' for i in range(18)] for j in range(9)]
        positions = [(i, j) for i in range(9) for j in range(18)]

        for _ in range(2):  # set two 'G's
            i, j = random.choice(positions)
            self.board[i][j] = 'J'
            self.ghosts.append(Ghost((i, j)))
            positions.remove((i, j))

        i, j = random.choice(positions)  # set one 'P'
        self.board[i][j] = 'P'
        self.pacman = Pacman((i, j))
        positions.remove((i, j))

        for _ in range(15):  # set fifteen 'X's
            i, j = random.choice(positions)
            self.board[i][j] = 'X'
            positions.remove((i, j))
    
    def move_pacman(self, direction):
        self.score -= 1
        i, j = self.pacman.position
        self.board[i][j] = ' '
        if direction == 'up':
            if i == 0 or self.board[i - 1][j] == 'X':
                self.board[i][j] = 'P'
                return
            i -= 1
        elif direction == 'down':
            if i == 8 or self.board[i + 1][j] == 'X':
                self.board[i][j] = 'P'
                return
            i += 1
        elif direction == 'left':
            if j == 0 or self.board[i][j - 1] == 'X':
                self.board[i][j] = 'P'
                return
            j -= 1
        elif direction == 'right':
            if j == 17 or self.board[i][j + 1] == 'X':
                self.board[i][j] = 'P'
                return
            j += 1
        self.pacman.position = (i, j)
        if self.board[i][j] == '.':
            self.score += 10
        self.board[i][j] = 'P'

    def move_ghost(self, index, direction):
        i, j = self.ghosts[index].position
        char = self.board[i][j]
        if char == 'J':
            self.board[i][j] = '.'
        elif char == 'G':
            self.board[i][j] = ' '
        if direction == 'up':
            if i == 0 or self.board[i - 1][j] in ['X', 'G', 'J']:
                self.board[i][j] = char
                return
            i -= 1
        elif direction == 'down':
            if i == 8 or self.board[i + 1][j] in ['X', 'G', 'J']:
                self.board[i][j] = char
                return
            i += 1
        elif direction == 'left':
            if j == 0 or self.board[i][j - 1] in ['X', 'G', 'J']:
                self.board[i][j] = char
                return
            j -= 1
        elif direction == 'right':
            if j == 17 or self.board[i][j + 1] in ['X', 'G', 'J']:
                self.board[i][j] = char
                return
            j += 1
        if self.board[i][j] == '.':
            self.board[i][j] = 'J'
        else:
            self.board[i][j] = 'G'
        self.ghosts[index].position = (i, j)

    def move_ghosts(self, directions=None):
        if directions == None:
            for index in range(len(self.ghosts)):
                directions = ['up', 'down', 'left', 'right']
                self.move_ghost(index, random.choice(directions))
        else:
            for index, direction in enumerate(directions):
                self.move_ghost(index, direction)

    def is_game_over(self):
        # True for lose and False for win and None for continue
        for ghost in self.ghosts:
            if ghost.position == self.pacman.position:
                return True
            
        count = 0
        for row in self.board:
            for char in row:
                if char in ['.', 'J']:
                    count += 1
        if count == 0:
            return False    
        
        return None
    
    def bfs_to_foods(self):
        pacman_pos = self.pacman.position
        queue = [(pacman_pos, 0)]
        visited = set()

        while queue:
            (x, y), dist = queue.pop(0)  # remove the first element

            if self.board[x][y] == '.':  # if this is a food
                return dist

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # for each neighboring position
                nx, ny = x + dx, y + dy

                if (0 <= nx < len(self.board) and 0 <= ny < len(self.board[0]) and # if the position is within the board
                    self.board[nx][ny] != 'X' and  # and it's not a wall
                    (nx, ny) not in visited):  # and it's not visited
                    queue.append(((nx, ny), dist + 1))
                    visited.add((nx, ny))

        return -1  # if there's no food


    def e_utility(self):
        """Return the estimated utility of the current state"""
        if(self.is_game_over() == False):
            return float('inf')
        if(self.is_game_over()):
            return -float('inf')
        pacman_x = self.pacman.position[0]
        pacman_y = self.pacman.position[1]
        ghost1_x = self.ghosts[0].position[0]
        ghost1_y = self.ghosts[0].position[1]
        ghost2_x = self.ghosts[1].position[0]
        ghost2_y = self.ghosts[1].position[1]
        dis_ghost1 = abs(pacman_x - ghost1_x) + abs(pacman_y - ghost1_y)
        dis_ghost2 = abs(pacman_x - ghost2_x) + abs(pacman_y - ghost2_y)
        return 10 * self.score + 2 * dis_ghost1 + 2 * dis_ghost2 - 5 * self.bfs_to_foods()
    
    def minimax(self, depth, alpha=-float('inf'), beta=float('inf'), is_max=True):
        if depth == 0 or self.is_game_over() != None:
            return self.e_utility(), None
        
        if is_max:
            best_score = -float('inf')
            best_move = None
            shuffled_directions = ['up', 'down', 'left', 'right']
            random.shuffle(shuffled_directions)
            for direction in shuffled_directions:
                game = copy.deepcopy(self)
                game.move_pacman(direction)
                score, _ = game.minimax(depth - 1, alpha, beta, False)
                if score > best_score:
                    best_score = score
                    best_move = direction
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            return best_score, best_move
        else:
            best_score = float('inf')
            for direction1 in ['up', 'down', 'left', 'right']:
                for direction2 in ['up', 'down', 'left', 'right']:
                    game = copy.deepcopy(self)
                    game.move_ghost(0, direction1)
                    game.move_ghost(1, direction2)
                    score, _ = game.minimax(depth - 1, alpha, beta, True)
                    if score < best_score:
                        best_score = score
                    beta = min(beta, best_score)
                    if beta <= alpha:
                        break
            return best_score, None
    
    def play(self):
        while self.is_game_over() == None:
            self.print_board()
            _ ,direction = self.minimax(depth=4, alpha=-float('inf'), beta=float('inf'), is_max=True)
            self.move_pacman(direction)
            if self.is_game_over() != None:
                break
            directions = ['up', 'down', 'left', 'right']
            random.shuffle(directions)
            self.move_ghosts()
            print('Score:', self.score)
        
        self.print_board()
        if self.is_game_over():
            print('You lose!')
        else:
            print('You win!')
        print('Score:', self.score)


    def print_board(self):
        for row in self.board:
            print(*row)
        print()

game = Game()
game.play()