class Account:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
    
    def withdraw(self, amount):
        if(amount > self.balance):
            return "Insufficient Funds"
        else:
            self.balance -= amount
            return self.balance
        
init_balance, withdrawal_amount = map(int, input().split())

account = Account("user", init_balance)

print(account.withdraw(withdrawal_amount))