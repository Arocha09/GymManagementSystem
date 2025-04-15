## maybe adding OAuth and password hashing to improve security

from class_defs import Person
from dbdriver import DB_Driver


def login(username, password):

    driver = DB_Driver()

    result = driver.get_login_details(username, password)

    if result == None:
        return None

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