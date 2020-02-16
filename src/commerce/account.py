from datetime import datetime


class Account:
    account_id: int
    interest_date: datetime
    value: int

    def __init__(self, account_id: int, value: int, interest_date: datetime):
        self.value = value
        self.interest_date = interest_date
        self.account_id = account_id

    def get_id(self) -> int:
        return self.account_id

    def get_interest_date(self) -> datetime:
        return self.interest_date

    def set_interest_date(self, interest_date: datetime):
        self.interest_date = interest_date

    def get_value(self) -> int:
        return self.value

    def set_value(self, value: int):
        self.value = value

    @staticmethod
    def from_dict(d):
        return Account(int(d['account_id']), int(d['value']), datetime.fromtimestamp(int(float(d['interest_date']))))
