from class_defs import Person
from dbdriver import DB_Driver


def login():
    username = input("Username: ")
    password = input("Password: ")

    driver = DB_Driver()

    result = driver.get_login_details(username, password)

    user = Person(
        result['userID'],
        result['email'],
        result['name'],
        result['memType'],        
        result['phone'],
        result['addressID'],
        result['loginID']        
                  )

    return user

if __name__ == "__main__":
    user = login()
    print(user)