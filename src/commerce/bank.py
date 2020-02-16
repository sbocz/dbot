import logging
import os
from datetime import datetime

from dotenv import load_dotenv

from src.commerce.account import Account
from src.utility import read_json_from_file, write_json_to_file

load_dotenv()
log = logging.getLogger('discord')
ACCOUNTS_FILE = os.path.join(os.getenv('BRAIN_PATH'), 'accounts.json')
CURRENCY = '𝔻'
HOURS_FOR_INTEREST = 24
INTEREST_VALUE = 20


class Bank:
    def __init__(self):
        self.accounts = self.load_accounts(ACCOUNTS_FILE)

    @staticmethod
    def load_accounts(filename):
        account_dict_list = read_json_from_file(filename)
        accounts = []
        for account_dict in account_dict_list:
            account = Account.from_dict(account_dict)
            accounts.append(account)
        return accounts

    def save_accounts(self):
        log.info("Saving bank accounts")
        account_list = []
        for account in self.accounts:
            d = account.__dict__.copy()
            d['interest_date'] = account.interest_date.timestamp()
            account_list.append(d)
        write_json_to_file(ACCOUNTS_FILE, account_list)

    def pay_interest(self):
        for account in self.accounts:
            # Check if it is time to pay out interest
            if (datetime.today() - account.interest_date).seconds >= (HOURS_FOR_INTEREST * 60 * 60):
                account.value += INTEREST_VALUE
                account.interest_date = datetime.today()
        self.save_accounts()

    def create_account(self, account_id, value):
        account = Account(account_id, value, datetime.today())
        self.accounts.append(account)
        self.save_accounts()
        return account

    def get_accounts(self):
        return self.accounts

    def get_account(self, account_id: int) -> Account:
        return next(filter(lambda x: x.account_id == account_id,  self.accounts), None)

    def make_payment(self, payer_account_id: int, value: int, payee_account_id: int = None):
        if value < 1:
            raise ValueError(f'Transactions must be for 1{CURRENCY} or more.')
        payer = self.get_account(payer_account_id)
        if payer is None:
            raise ValueError(f'Payer must be provided on transactions.')
        if payer.value < value:
            raise ValueError(f'Payer only has a balance of {payer.value}. They cannot pay {value}.')
        # At this point the transaction can happen
        payee = self.get_account(payee_account_id)
        payer.value -= value
        if payee is not None:
            payee.value += value
        self.save_accounts()

    def receive_payment(self, payee_account_id: int, value: int):
        if value < 1:
            raise ValueError(f'Payments must be for 1{CURRENCY} or more.')
        payee = self.get_account(payee_account_id)
        if payee is None:
            raise ValueError(f'Payee must be provided to receive payments.')
        # At this point the payment can be received
        payee.value += value
        self.save_accounts()
