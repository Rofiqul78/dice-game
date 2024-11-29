import sys
import random
import hmac
import hashlib
import os
import binascii

class Dice:
    def __init__(self, values):
        self.values = values

    def roll(self):
        return random.choice(self.values)

class DiceParser:
    @staticmethod
    def parse(args):
        if len(args) < 4:
            raise ValueError("At least 3 dice configurations are required.\nUsage: python game.py 2,2,4,4,9,9 6,8,1,1,8,6 7,5,3,7,5,3")
        
        dice = []
        for arg in args[1:]:
            values = arg.split(',')
            if len(values) != 6 or not all(v.isdigit() for v in values):
                raise ValueError("Each dice configuration must contain 6 integers.\nUsage: python game.py 2,2,4,4,9,9 6,8,1,1,8,6 7,5,3,7,5,3")
            dice.append(Dice([int(v) for v in values]))
        
        return dice

class RandomGenerator:
    @staticmethod
    def generate_secure_random_key():
        return os.urandom(32)

    @staticmethod
    def generate_secure_random_number(n):
        while True:
            number = int.from_bytes(os.urandom(4), 'big')
            if number < (1 << 32) - (1 << 32) % n:
                return number % n

    @staticmethod
    def generate_hmac(key, message):
        return hmac.new(key, message.encode(), hashlib.sha3_256).hexdigest()

class FairRandomProtocol:
    def __init__(self, n):
        self.n = n
        self.computer_key = RandomGenerator.generate_secure_random_key()
        self.user_key = RandomGenerator.generate_secure_random_key()
        self.computer_number = RandomGenerator.generate_secure_random_number(n)
        self.user_number = None
        self.hmac = RandomGenerator.generate_hmac(self.computer_key, str(self.computer_number))

    def getUserNumber(self):
        while True:
            try:
                user_number = int(input(f"Select a number between 0 and {self.n-1}: "))
                if 0 <= user_number < self.n:
                    self.user_number = user_number
                    return user_number
                else:
                    print(f"Please enter a valid number between 0 and {self.n-1}.")
            except ValueError:
                print("Invalid input. Please enter an integer.")

    def calculateResult(self):
        total = (self.computer_number + self.user_number) % self.n
        return total

    def showProof(self):
        print(f"User HMAC: {self.hmac}")
        user_number = self.getUserNumber()
        total = self.calculateResult()
        print(f"User selected number: {user_number}, Total: {total}")
        print(f"Computer number: {self.computer_number}")
        print(f"User Key: {binascii.hexlify(self.user_key).decode()}")
        print(f"Computer Key: {binascii.hexlify(self.computer_key).decode()}")
        return total

class ProbabilityCalculator:
    @staticmethod
    def calculate_probabilities(dice_list):
        probabilities = {}
        for i, dice1 in enumerate(dice_list):
            for j, dice2 in enumerate(dice_list):
                win_count = 0
                for val1 in dice1.values:
                    for val2 in dice2.values:
                        if val1 > val2:
                            win_count += 1
                total_combinations = len(dice1.values) * len(dice2.values)
                probabilities[(i, j)] = win_count / total_combinations
        return probabilities

class TableGenerator:
    @staticmethod
    def generate(probabilities, dice_count):
        table = "Probability Table (Winning Probabilities for Each Dice Pair):\n"
        table += " " * 5 + "".join([f"D{j+1: <5}" for j in range(dice_count)]) + "\n"
        for i in range(dice_count):
            row = f"D{i+1}  " + "".join([f"{probabilities[(i, j)]:.2f} " for j in range(dice_count)]) + "\n"
            table += row
        return table

class Game:
    def __init__(self, args):
        try:
            self.dice_list = DiceParser.parse(args)
        except ValueError as e:
            print(e)
            sys.exit(1)

    def start(self):
        print("Welcome to the Generalized Dice Game!")
        while True:
            print("\nAvailable Dice:")
            for i, dice in enumerate(self.dice_list):
                print(f"{i+1}. {dice.values}")

            choice = input("Select a dice by number (or type 'help' for probabilities, 'exit' to quit): ").strip().lower()

            if choice == 'exit':
                print("Thank you for playing!")
                break
            elif choice == 'help':
                probabilities = ProbabilityCalculator.calculate_probabilities(self.dice_list)
                table = TableGenerator.generate(probabilities, len(self.dice_list))
                print(table)
            elif choice.isdigit() and 1 <= int(choice) <= len(self.dice_list):
                user_dice = self.dice_list[int(choice) - 1]
                computer_dice = random.choice([dice for dice in self.dice_list if dice != user_dice])

                print(f"You selected dice: {user_dice.values}")
                print(f"Computer selected dice: {computer_dice.values}")

                print("Rolling the dice...")
                user_roll = user_dice.roll()
                computer_roll = computer_dice.roll()

                print(f"Your roll: {user_roll}")
                print(f"Computer's roll: {computer_roll}")

                protocol = FairRandomProtocol(6)
                total = protocol.showProof()

                print("Final Result:")
                if total > computer_roll:
                    print("You win!")
                elif total < computer_roll:
                    print("Computer wins!")
                else:
                    print("It's a tie!")

                if input("Play again? (y/n): ").strip().lower() != 'y':
                    print("Thank you for playing!")
                    break
            else:
                print("Invalid choice. Please select a valid dice or type 'help' or 'exit'.")

if __name__ == "__main__":
    game = Game(sys.argv)
    game.start()
