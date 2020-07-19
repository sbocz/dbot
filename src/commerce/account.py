from datetime import datetime


class Account:
    """Account data object"""
    account_id: int
    interest_date: datetime
    value: int

    def __init__(self, account_id: int, value: int, interest_date: datetime):
        self.value = value
        self.interest_date = interest_date
        self.account_id = account_id

    def get_id(self) -> int:
        """Return account's ID"""
        return self.account_id

    def get_interest_date(self) -> datetime:
        """Retrieve the last interest paid date"""
        return self.interest_date

    def set_interest_date(self, interest_date: datetime):
        """Update the last interest paid date"""
        self.interest_date = interest_date

    def get_value(self) -> int:
        """Retrieves account's value"""
        return self.value

    def set_value(self, value: int):
        """Sets account's value"""
        self.value = value

    @staticmethod
    def from_dict(dictionary):
        """Constructs an Account from a disctionary"""
        return Account(int(dictionary['account_id']), int(dictionary['value']), datetime.fromtimestamp(int(float(dictionary['interest_date']))))
