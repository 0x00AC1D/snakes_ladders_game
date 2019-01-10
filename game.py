from random import randint

def pint_input(msg):
    """insists on positive integer input"""
    while True:
        try:
            pint = int(input(msg))
            if pint <= 0:
                print("Yo, it should be a POSITIVE integer! Try again.")
                continue
            break
        except Exception:
            print("Yo, it should be an INTEGER! Try again.")

    return pint

class ExplodingDice:
    def __init__(self, sides, explosion_threshold):
        self.sides = sides
        self.explosion_threshold = explosion_threshold

    def roll(self):
        rolls = []
        roll = self.explosion_threshold

        while roll >= self.explosion_threshold:
            roll = randint(1,self.sides)
            rolls.append(roll)

        return rolls

class Unit:
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.position = 0

class Board:
    def __init__(self, size=100, event_ratio=4):
        self.size = size
        self.event_ratio = event_ratio

    def gen_snakes_ladders(self, size, event_ratio):
        magic_fields = [i + randint(0, event_ratio) for i in range(event_ratio, size - event_ratio, event_ratio)]
        min_diff = round(size**0.5) + 1
        snakes, ladders = {}, {}

        for field in magic_fields:
            end_field = -1

            while end_field not in range(size):
                end_field = randint(min_diff, min_diff*4) * (1, -1)[randint(0, 1)] + field

            (snakes, ladders)[end_field - field > 0][field] = end_field

        return snakes, ladders

class Player:
    def __init__(self, name, units=2):
        self.name = name
        self.units = {i:Unit(i, self) for i in range(units)}

    def input_unit_indices(self, rolls):
        while True:
            try:
                unit_indices = list(map(int, input("Enter unit number for each roll delimited by space: ").split(" ")))
                rolen = len(rolls)
                if len(unit_indices) == rolen:
                    if max(unit_indices) in range(len(self.units)) and min(unit_indices) in range(len(self.units)):
                        break
                    else:
                        print(f"Only choose out of {', '.join(list(map(str, range(len(self.units)))))}")
                else:
                    print(f"Yo, there {['are', 'is'][rolen==1]} {rolen} number{['s', ''][rolen==1]} " +
                          f"and {rolen - 1} space{['s', ''][rolen==1]} to be input. Try again!\n")

            except Exception:
                print(f"Yo, only write NUMBERS within ({', '.join(list(map(str, range(len(self.units)))))}) delimited by space.\n")

        return unit_indices

class Game:
    def __init__(self):
        print("Welcome to snake-ladder game.")
        self.dice = ExplodingDice(6, 6)
        self.player_names = []
        players = pint_input("How many players are to play?: ")
        self.players = [self.gen_player() for _ in range(players)]
        self.all_units = [unit for player in self.players for unit in player.units.values()]
        self.friendly_mode = input("Friendly mode? (without kicking units back to start)(y/n): ").lower() == "y"

        if input("Load board from json? (y/n): ").lower() == "y":
            path = input("Enter relative, or absolute path of the json: ")
            self.board = self.load_json_board(path)
        else:
            self.board = self.gen_board()

        self.magic_fields = {**self.board.snakes, **self.board.ladders}

    def gen_player(self):
        while True:
            name = input("Enter player's name: ")
            if name and name not in self.player_names:
                self.player_names.append(name)
                return Player(name)
            print("The name must be unique! Try again!")

    def gen_board(self):
        board_size = pint_input("How high to get to win?: ")
        board_event_ratio = pint_input("One in how many fields should trigger special event?: ")
        board = Board(board_size, board_event_ratio)
        board.snakes, board.ladders = board.gen_snakes_ladders(board.size, board.event_ratio)
        return board

    def load_json_board(self, path):
        """expected json format: 
        {'size': x,
         'snakes': {"start": end: int},
         'ladders': {"start": end: int}}"""
        import json

        with open(path) as json_file:
            json_board = json.load(json_file)

        board = Board(json_board["size"])
        board.snakes = {int(k): v for k, v in json_board["snakes"].items()}
        board.ladders = {int(k): v for k, v in json_board["ladders"].items()}

        return board

    def print_game_info(self):
        print(f"\nWe have {len(self.players)} players: {', '.join([player.name for player in self.players])}.")
        print(f"Each with {len(self.players[0].units)} units to start with.")
        print(f"Friendly mode is {['OFF', 'ON'][self.friendly_mode]}.")
        if self.friendly_mode:
            print("If you step on a field, occupied by an enemy unit, enemy is sent back to start.")
        print("Unit choosing eg. rolls: 6, 4 - '1 1' to use both rolls for unit number 1.")
        print(f"First to reach {self.board.size} wins.")
        print("Game starts, good luck and have fun.")

    def kick_enemies(self, player, new_pos):
        if not self.friendly_mode:
            for unit in self.all_units:
                if unit.position == new_pos and unit.owner != player:
                    unit.position = 0
                    print(f"{unit.owner.name}'s unit_{unit.name} has been kicked from {new_pos} back to 0.")

    def print_board(self):
        width = len(str(self.board.size + 1)) + 1
        for i in range(self.board.size+1):
            print("{:<{width}}".format(str(self.magic_fields.get(i, i)), width=width), end="")
            if not i % (80 // width):
                print()
        print()

    def eval_move(self, player, unit, roll):
        old_pos = unit.position
        unit.position += roll
        visited = [unit.position]

        self.kick_enemies(player, unit.position)

        while unit.position in self.board.snakes.keys() or unit.position in self.board.ladders.keys():
            if unit.position in self.board.snakes.keys():
                unit.position = self.board.snakes.get(unit.position)
                print("You have stepped on a snake.")
            elif unit.position in self.board.ladders.keys():
                unit.position = self.board.ladders.get(unit.position)
                print("You have found a ladder.")

            self.kick_enemies(player, unit.position)

            if unit.position in visited: # prevent infinite cycle
                print(f"unit_{unit.name} has visited {unit.position} twice.")
                break

            visited.append(unit.position)
            print(f"unit_{unit.name} is now on field {unit.position}.")
        print(f"{player.name}'s unit_{unit.name} moved from {old_pos} to {unit.position}.")

    def game_loop(self):
        self.print_game_info()
        run = True

        while run:
            for player in self.players:
                rolls = self.dice.roll()
                print(f"\nIt's {player.name}'s turn.")
                self.print_board()
                print(f"You have rolled {', '.join(list(map(str, rolls)))}.")

                for unit in player.units.values():
                    print(f"unit_{unit.name} is on {unit.position}.")

                unit_indices = player.input_unit_indices(rolls)

                for unit_index, roll in zip(unit_indices, rolls):
                    unit = player.units[unit_index]
                    self.eval_move(player, unit, roll)

                    if unit.position >= self.board.size:
                        input(f"Player {player.name} has won the game! Congratulations!\n" + 
                               "Thank you for playing the game!")
                        return

if __name__ == "__main__":
    game = Game()
    game.game_loop()