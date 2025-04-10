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
        return result # this method is ALSO necessary for instructors
    
    # SQL for admin to add a class with all the right information
    def add_class(self, instructor_id: int, gym_id: int, class_name: str, start_time: str, end_time: str) -> None:
        try:
            self.cursor.execute(
                """
                INSERT INTO Class (instructorID, gymID, className, startTime, endTime)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (instructor_id, gym_id, class_name, start_time, end_time)
            )
            self.client.commit()
            print("Class successfully added.")
        except Exception as e:
            self.client.rollback()
            print("Error adding class:", e)

    
    # SQL for admin to delete a class based on class_id
    def delete_class(self, class_id: int) -> None:
        try:
            self.cursor.execute(
                "DELETE FROM Class WHERE classId = %s",
                (class_id,)
            )
            self.client.commit()
            print(f"Class {class_id} deleted successfully.")
        except Exception as e:
            self.client.rollback()
            print(f"Error deleting class {class_id}:", e)

    

    
    def get_instructor_info(self) -> list:
        # SQL for admin to get instructor info
        self.cursor.execute("SELECT * FROM Person WHERE memtype = 'instructor'")
        result = self.cursor.fetchall()
        return result
    
    # SQL for admin to add an instructor
    def add_instructor(self, email: str, name: str, phone: str, st_name: str, city: str, state: str, zip_code: str, username: str, password: str) -> None:
        try:
            self.cursor.execute(
                "INSERT INTO Login (Username, Password) VALUES (%s, %s) RETURNING loginID",
                (username, password)
            )
            login_id = self.cursor.fetchone()[0] # add to login table first

            self.cursor.execute(
                "INSERT INTO Address (StName, City, State, Zip) VALUES (%s, %s, %s, %s) RETURNING addressID",
                (st_name, city, state, zip_code)
            )
            address_id = self.cursor.fetchone()[0] # add to address table

            self.cursor.execute(
                """
                INSERT INTO Person (email, name, memType, phone, addressID, loginID)
                VALUES (%s, %s, 'instructor', %s, %s, %s)
                """,
                (email, name, phone, address_id, login_id)
            ) # add to person table as an instructor

            self.client.commit()
            print("Instructor successfully added.")
        except Exception as e:
            self.client.rollback()
            print("Error adding instructor:", e)

    # SQL to delete an instructor
    def delete_instructor(self, user_id: int) -> None:
        try:
            self.cursor.execute(
                "DELETE FROM Person WHERE userID = %s AND memType = 'instructor'",
                (user_id,)
            )
            self.client.commit()
            print(f"Instructor {user_id} deleted successfully.")
        except Exception as e:
            self.client.rollback()
            print(f"Error deleting instructor {user_id}:", e)

    
    def get_member_info(self) -> list:
        # SQL for admin to get member info
        self.cursor.execute("SELECT * FROM Person WHERE memtype = 'monthly' OR memtype = 'yearly'")
        result = self.cursor.fetchall()
        return result
    
    def add_member(self) -> list:
        # SQL for admin to add a member
        self.cursor.execute ("UPDATE Person SET memtype = 'monthly' AND") # could also use insert statement here, also need to specify whether monthly or yearly
        result = self.cursor.fetchall()
        return result
    
    def delete_member(self) -> list:
        # SQL for admin to delete a member
        # somehow define what the admin wants to delete??
        self.cursor.execute("DELETE FROM Person WHERE memtype = 'monthly' OR 'yearly' ")
        result = self.cursor.fetchall()
        return result
    
    def change_gym_open_hours(self) -> list:
        # SQL for admin to change gym opening hours
        self.cursor.execute ("UPDATE gymOpen TO ")
        result = self.cursor.fetchall()
        return result
    
    def change_gym_close_hours(self) -> list:
        # SQL for admin to change gym closing hours
        self.cursor.execute ("UPDATE gymClose TO ")
        result = self.cursor.fetchall()
        return result
    
    
    def get_facilities_list(self) -> list:
        # SQL to get all facilities from facilities table
        self.cursor.execute("SELECT * FROM Facilities")
        result = self.cursor.fetchall()
        return result # also necessary for all instructors
    
    def add_facility(self) -> list:
        # SQL to add a facility
        self.cursor.execute("INSERT INTO Facilities ______")
        result = self.cursor.fetchall()
        return result
    
    def delete_facility(self) -> list:
        # SQL to delete a facility
        self.cursor.execute("DELETE FROM Facilities ______")
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

