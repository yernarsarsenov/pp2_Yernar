from db.dbConnector import DBConnector
from db.PhoneBook import PhoneBook

db = DBConnector()
db.createTable()

while True:
    print("\n[1] GET ALL USERS")
    print("[2] INSERT / UPDATE USER (upsert)")
    print("[3] INSERT MANY USERS")
    print("[4] SEARCH BY PATTERN")
    print("[5] GET USERS BY LIMIT AND OFFSET")
    print("[6] DELETE USER")
    print("[0] EXIT")

    choice = int(input())
    match choice:
        case 0:
            break
        case 1:
            for user in db.getAllRecords():
                print(user)
        case 2:
            first_name = input("Enter first name: ")
            last_name  = input("Enter last name: ")
            phone      = input("Enter phone: ")
            db.upsertUser(PhoneBook(0, first_name, last_name, phone))
        case 3:
            amount = int(input("How many users? "))
            users = []
            for _ in range(amount):
                first_name = input("Enter first name: ")
                last_name  = input("Enter last name: ")
                phone      = input("Enter phone: ")
                users.append(PhoneBook(0, first_name, last_name, phone))
            incorrect = db.insertManyUsers(users)
            if incorrect:
                print("INCORRECT USERS:")
                for u in incorrect:
                    print(u)
        case 4:
            pattern = input("Enter search pattern: ")
            results = db.searchByPattern(pattern)
            if results:
                for user in results:
                    print(user)
            else:
                print("No results found.")
        case 5:
            limit  = int(input("Enter limit: "))
            offset = int(input("Enter offset: "))
            for user in db.getLimitOffset(limit, offset):
                print(user)
        case 6:
            value = input("Enter name or phone to delete: ")
            db.deleteUser(value)