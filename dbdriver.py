import psycopg2

# basic set up code
class DB_Driver():
    def __init__(self):
        self.client = connect_to_postgres_db()
        self.cursor = get_cursor(self.client)

    # generic
    def view_personal_info(self, user_id: int) -> dict:
        try:
            self.cursor.execute(
                """
                SELECT userID, email, name, memType, phone, addressID, loginID
                FROM Person
                WHERE userID = %s
                """,
                (user_id,)
            )
            result = self.cursor.fetchone()
            if result is None:
                print(f"No user found with ID {user_id}")
                return {}

            keys = ['userID', 'email', 'name', 'memType', 'phone', 'addressID', 'loginID']
            return dict(zip(keys, result)) # save as dict

        except Exception as e:
            print(f"Error retrieving personal info for user {user_id}:", e)
            return {}
    
    def update_personal_info(self, user_id: int, updates: dict) -> None:
        try:
            allowed_fields = ['email', 'name', 'memType', 'phone', 'addressID', 'loginID']
            for column in updates:
                if column not in allowed_fields:
                    raise ValueError(f"Invalid field: {column}")

            set_clause = ", ".join([f"{k} = %s" for k in updates])
            values = list(updates.values()) + [user_id]

            query = f"UPDATE Person SET {set_clause} WHERE userID = %s"
            self.cursor.execute(query, values)
            self.client.commit()
            print(f"Updated info for user {user_id}")
        except Exception as e:
            self.client.rollback()
            print("Error updating personal info:", e)





    # Administrator queries
    
    # SQL to return all classes (admin and instructors only)
    def get_class_info(self) -> list:
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

    

    # SQL to get all instructor info (admin only)
    def get_instructor_info(self) -> list:
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

    # SQL for admin to get member info (admin only, for now)
    def get_member_info(self) -> list:
        self.cursor.execute("SELECT * FROM Person WHERE memtype = 'monthly' OR memtype = 'yearly'")
        result = self.cursor.fetchall()
        return result
    
    # SQL to add member (admin only)
    def add_member(self, email: str, name: str, memtype: str, phone: str, st_name: str, city: str, state: str, zip_code: str, username: str, password: str) -> None:
        try:
            if memtype not in ('monthly', 'yearly'):
                raise ValueError("Membership type must be 'monthly' or 'yearly'")

            self.cursor.execute(
                "INSERT INTO Login (Username, Password) VALUES (%s, %s) RETURNING loginID",
                (username, password)
            )
            login_id = self.cursor.fetchone()[0] # add login

            self.cursor.execute(
                "INSERT INTO Address (StName, City, State, Zip) VALUES (%s, %s, %s, %s) RETURNING addressID",
                (st_name, city, state, zip_code)
            )
            address_id = self.cursor.fetchone()[0] # add user address

            self.cursor.execute(
                """
                INSERT INTO Person (email, name, memType, phone, addressID, loginID)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (email, name, memtype, phone, address_id, login_id)
            ) # add previous info into Person

            self.client.commit()
            print("Member successfully added.")
        except Exception as e:
            self.client.rollback()
            print("Error adding member:", e)

    # SQL to delete member (admin only)
    def delete_member(self, user_id: int) -> None:
        try:
            self.cursor.execute(
                """
                DELETE FROM Person 
                WHERE userID = %s AND (memType = 'monthly' OR memType = 'yearly')
                """,
                (user_id,)
            )
            self.client.commit()
            print(f"Member {user_id} deleted successfully.")
        except Exception as e:
            self.client.rollback()
            print(f"Error deleting member {user_id}:", e)

    # SQL to change gym opening hours (admin only)
    def change_gym_open_hours(self, gym_id: int, new_open_time: str) -> None:
        try:
            self.cursor.execute(
                "UPDATE Gym SET gymOpen = %s WHERE gymID = %s",
                (new_open_time, gym_id)
            )
            self.client.commit()
            print(f"Gym {gym_id} open time updated to {new_open_time}.")
        except Exception as e:
            self.client.rollback()
            print(f"Error updating open hours for gym {gym_id}:", e)

    # SQL to change gym close hours (admin only)
    def change_gym_close_hours(self, gym_id: int, new_close_time: str) -> None:
        try:
            self.cursor.execute(
                "UPDATE Gym SET gymClose = %s WHERE gymID = %s",
                (new_close_time, gym_id)
            )
            self.client.commit()
            print(f"Gym {gym_id} close time updated to {new_close_time}.")
        except Exception as e:
            self.client.rollback()
            print(f"Error updating close hours for gym {gym_id}:", e)

    # SQL to get all facilities (admin and instructors)
    def get_facilities_list(self) -> list:
        self.cursor.execute("SELECT * FROM Facilities")
        result = self.cursor.fetchall()
        return result # also necessary for all instructors
    
    # SQL to add facility (admin only)
    def add_facility(self, facility_name: str, open_time: str, close_time: str, gym_id: int) -> None:
        try:
            self.cursor.execute(
                """
                INSERT INTO Facilities (facilityName, facilityOpen, facilityClose, gymID)
                VALUES (%s, %s, %s, %s)
                """,
                (facility_name, open_time, close_time, gym_id)
            )
            self.client.commit()
            print("Facility successfully added.")
        except Exception as e:
            self.client.rollback()
            print("Error adding facility:", e)

    # SQL to delete facility (admin only)
    def delete_facility(self, facility_id: int) -> None:
        try:
            self.cursor.execute(
                "DELETE FROM Facilities WHERE facilityID = %s",
                (facility_id,)
            )
            self.client.commit()
            print(f"Facility {facility_id} deleted successfully.")
        except Exception as e:
            self.client.rollback()
            print(f"Error deleting facility {facility_id}:", e)


    # Instructor queries (note that there are some admin queries also for instructors)

    # SQL to add a member to a class (instructors, maybe admins as well)
    def add_member_to_class(self, member_id: int, class_id: int) -> None:
        try:
            self.cursor.execute(
                """
                INSERT INTO EnrollmentList (id, classId)
                VALUES (%s, %s)
                """,
                (member_id, class_id)
            )
            self.client.commit()
            print(f"Member {member_id} added to class {class_id}.")
        except Exception as e:
            self.client.rollback()
            print(f"Error adding member {member_id} to class {class_id}:", e)

    # SQL to delete a member from a class (instructors, maybe admins as well)
    def remove_member_from_class(self, member_id: int, class_id: int) -> None:
        try:
            self.cursor.execute(
                """
                DELETE FROM EnrollmentList
                WHERE id = %s AND classId = %s
                """,
                (member_id, class_id)
            )
            self.client.commit()
            print(f"Member {member_id} removed from class {class_id}.")
        except Exception as e:
            self.client.rollback()
            print(f"Error removing member {member_id} from class {class_id}:", e)
    
    def get_instructor_classes(self, instructor_id: int) -> list:
        try:
            self.cursor.execute(
                """
                SELECT * FROM Class
                WHERE instructorID = %s
                """,
                (instructor_id,)
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving classes for instructor {instructor_id}:", e)
            return []



    

    

    


def connect_to_postgres_db():
    print("connecting to the db")
    client = psycopg2.connect(dbname = "group13", user = "group13", password = "V5ukP3C2", host = "bastion.cs.virginia.edu", port = "5432")
    return client

def get_cursor(client):
    print("create cursor")
    cursor = client.cursor()
    return cursor




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

