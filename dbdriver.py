import psycopg2

# basic set up code
class DB_Driver():
    def __init__(self):
        self.client = connect_to_postgres_db()
        self.cursor = get_cursor(self.client)


    # Administrator queries
    
    def get_class_info(self) -> list:
        #SQL to return all the classes
        self.cursor.execute("SELECT * FROM Class")
        result = self.cursor.fetchall()
        return result
    
    def add_class(self) -> list:
        # SQL for admin to add a class
        # somehow read in new information???
        self.cursor.execute("UPDATE ")
        result = self.cursor.fetchall()
        return result
    
    def delete_class(self) -> list:
        # SQL for admin to delete a class
        # somehow define what the admin wants to delete??
        self.cursor.execute("DELETE FROM CLASS WHERE ")
        result = self.cursor.fetchall()
        return result
    
    def get_instructor_info(self) -> list:
        # SQL for admin to get instructor info
        self.cursor.execute("SELECT name FROM Class JOIN PERSON ON Class.instructorID = Person.userID")
        result = self.cursor.fetchall()
        return result
    
    def get_facilities_list(self) -> list: # make sure this gets pushed 
        # SQL to get all facilities from facilities table
        self.cursor.execute("SELECT * FROM Facilities")
        result = self.cursor.fetchall()
        return result
    


def connect_to_postgres_db():
    print("connecting to the db")
    client = psycopg2.connect(dbname = "group13", user = "group13", password = "V5ukP3C2", host = "bastion.cs.virginia.edu", port = "5432")
    return client

def get_cursor(client):
    print("create cursor")
    cursor = client.cursor()
    return cursor


# after this, remember in the test file to print the query, execute that query, and then fetchall
# example from test.py
# print("SELECT * FROM Person")
# cursor.execute("SELECT * FROM Person")
# result = cursor.fetchall()
# print(result)


# Administrator Queries
# connect_to_postgres_db()
# get_cursor()






# Instructor Queries



# Member Queries

# View their enrolled classes

# Enroll in a class

# update (upgrade) membership type


# update personal info

# update their address
# update phone
# update email
# update name


# update username (must be unique amongst all usernames present in DB, which should already be set up for that)
# update password

