"""
A Simple Banking System
Andres Preciado

Using Sql Lite this Code system creates a Database of bank accounts
where Accounts can be made, income added, balance kept, transfers,
as well as closing the account.
"""
import random
import sqlite3

conn = sqlite3.connect('card.s3db')     # Create connection to sqlite database
cur = conn.cursor()     # Creates a cursor to allow queries (or querys?) to sqlite database
IIN = '400000'      # Basic Issuer Identification Number for A Simple Banking Number


class Bank(object):

    def __init__(self, card_number=0, pin=0, balance=0):
        """
        Initiates new Bank class object
        :param card_number:
        :param pin:
        :param balance:
        """
        self.card_number = card_number
        self.pin = pin
        self.balance = balance

    def __str__(self):
        """
        :return: Card number
        """
        return self.card_number

    @staticmethod
    def create_database():
        """
        Creates Card Database if no Database exists
        """
        cur.execute(
            """CREATE TABLE IF NOT EXISTS 'card'(  
            number TEXT PRIMARY KEY,  
            pin TEXT,  
            balance INTEGER DEFAULT 0);""")
        conn.commit()

    def add_database(self):
        """
        adds into database
        NOT USED
        """
        sql = """INSERT INTO 'card'(number, pin, balance) values(?, ?, ?)"""
        values = (self.card_number, self.pin, self.balance)
        cur.execute(sql, values)
        conn.commit()

    @classmethod
    def new_account(cls):
        """
        :return: Returns a new Bank Card Number, PIN, and sets balance to $0
        """
        cls.card_number = cls.luhn(IIN + f'{random.randint(000000000, 999999999):09}')
        cls.pin = f'{random.randint(0000, 9999):04}'
        cls.balance = 0
        sql = """INSERT INTO 'card'(number, pin, balance) VALUES(?, ?, ?)"""
        values = (cls.card_number, cls.pin, cls.balance)
        cur.execute(sql, values)
        conn.commit()
        print("\nYour card has been created\n"
              "Your card number:\n"
              + cls.card_number +
              "\nYour card PIN:\n"
              + cls.pin)
        # print(self.card_number)
        # print(self.pin)
        return cls.card_number, cls.pin, cls.balance

    @staticmethod
    def luhn(pre_luhn: str) -> str:
        """
        Calculates the checksum and adds it to the pre_luhn
        :param pre_luhn: Is the 15 digits before checksum
        :return: 16 digit card number
        """
        return pre_luhn + Bank.find_checksum(pre_luhn)

    @staticmethod
    def find_checksum(preluhn: str) -> str:
        """
        Finds the checksum of the 15 digit preluhn
        :param preluhn: 15 digits before checksum
        :return: Checksum
        """
        luhn_list = list(map(int, str(preluhn)))
        double_odd_index: list[int] = [n * 2 if i % 2 else n for i, n in enumerate(luhn_list, 1)]
        sub_nine_double_digit: list[int] = [n - 9 if n > 9 else n for n in double_odd_index]
        checksum = sum(sub_nine_double_digit)
        preluhn = 10 - (checksum % 10) if checksum % 10 != 0 else 0
        return str(preluhn)

    @staticmethod
    def check_checksum(luhn: str) -> bool:
        """
        Checks to see if 16 digit card number passes luhn algorithm
        :param luhn: Full 16 digit card number
        :return: True if card number passes luhn algorithm
        """
        check = True if Bank.find_checksum(luhn[:-1]) == luhn[-1] else False
        return check

    @staticmethod
    def password():
        """
        Asks for card number and pin then checks against database.
        :return: Bank object if found and pin matches, otherwise None
        """
        card_input = input('\nEnter your card number:\n')
        pin_input = input('Enter your PIN:\n')
        try:
            retrieve_login = """SELECT * FROM 'card' 
                                WHERE number = ?"""
            cur.execute(retrieve_login, (card_input,))
            account_data = cur.fetchone()
            if account_data is not None and card_input == account_data[0] and pin_input == account_data[1]:
                account = Bank(account_data[0], account_data[1], account_data[2])
                print('\nYou have successfully logged in!')
                return account
            else:
                print('\nWrong card number or PIN!')
                return None
        except sqlite3.Error as error:
            print("\nSuch a card does not exist.", error)
            return None

    def print_balance(self):
        """
        Prints balance of Bank object
        """
        print(f'\nBalance: ${self.balance}')

    def add_income(self):
        """
        Adds Income to Bank object
        """
        amount_to_add = int(input("\nHow Much Would You Like To Deposit:   "))
        self.balance = self.balance + amount_to_add
        sql = """UPDATE card
                SET balance = ?
                WHERE number = ?"""
        cur.execute(sql, (self.balance, self.card_number))
        conn.commit()
        return

    def close_account(self):
        """
        Erases Bank object and deletes from database
        """
        sql = """DELETE FROM card
                WHERE number =?"""
        cur.execute(sql, (self.card_number,))
        print("Your Account is Closed")
        return

    def do_transfer(self):
        """
        Transfers specified balance to another account
        """
        transfer_number = input("\nWhich Account Would You Like To Transfer to?   ")
        if not Bank.check_checksum(transfer_number):
            print("\nProbably you made a mistake in the card number. Please try again!")
            return
        elif transfer_number == self.card_number:
            print("You can't transfer money to the same account!")
            return
        try:
            sql = """SELECT balance 
                    FROM card
                    WHERE number = ?"""
            cur.execute(sql, (transfer_number,))
            old_balance = cur.fetchone()
            if old_balance is None:
                raise sqlite3.Error
        except sqlite3.Error as error:
            print("Such a card does not exist", error)
            return
        transfer_amount = int(input("\nHow Much Would You Like To Transfer?   "))
        if transfer_amount > self.balance:
            print("Not enough money!")
            return
        new_balance_transfer = old_balance[0] + transfer_amount
        self.balance = self.balance - transfer_amount
        sql = """
                UPDATE card
                SET balance = ?
                WHERE number = ?
            """
        cur.execute(sql, (new_balance_transfer, transfer_number))
        cur.execute(sql, (self.balance, self.card_number))
        conn.commit()
        return


def account_menu_loop() -> str:
    """
    Provides account menu options
    :return: Account menu option chosen
    """
    return input("\n1. Balance\n"
                 "2. Add income\n"
                 "3. Do transfer\n"
                 "4. Close Account\n"
                 "5. Log out\n"
                 "0. Exit\n")


def account_menu(account: Bank):
    """
    Loop for Account Menu
    :param account: Bank Object
    """
    while True:
        menu_select = account_menu_loop()
        if menu_select == '1':  # Balance
            account.print_balance()
        elif menu_select == '2':  # Add income
            account.add_income()
        elif menu_select == '3':  # Do Transfer
            account.do_transfer()
        elif menu_select == '4':  # Close account
            account.close_account()
            del account
            return
        elif menu_select == '5':  # Log out
            return
        elif menu_select == '0':
            bye()


def login() -> str:
    """
    Provides menu options for main bank loop
    :return: Chosen menu option
    """
    return input("\n1. Create an account\n"
                 "2. Log into account\n"
                 "0. Exit\n")


def main_loop():
    """
    Main Bank Loop
    """
    Bank.create_database()
    while True:
        selection = login()
        if selection == '0':
            bye()
        elif selection == '1':
            Bank().new_account()
        elif selection == '2':
            account = Bank.password()
            if account is not None:
                account_menu(account)


def main():
    """
    MAIN
    """
    main_loop()


def bye():
    """
    Closes connection to database and exits program
    """
    cur.close()
    conn.close()
    exit("Bye!")


if __name__ == "__main__":
    main()
