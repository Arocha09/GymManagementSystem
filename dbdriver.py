import psycopg2

# To complete/improve this class I think we should always return an object on the retrieval queries.
# Also consider using commit and rollback on some of these methods so that once we go to modify the 
# database with large amounts of data we dont screw it up.


# basic set up code
class DB_Driver():
    def __init__(self):
        self.client = connect_to_postgres_db()
        self.cursor = get_cursor(self.client)

    # generic for all 3
    def get_personal_info(self, user_id):
        try:
            self.cursor.execute(
                    """
                    SELECT *
                    FROM Person
                    WHERE userID = %s
                    """,
                    (user_id,)
                )
            result = self.cursor.fetchone()
            if result is None:
                print(f"No user found with ID {user_id}")
                return {}
            # fetchall
            keys = [
                'userID',
                'email',
                'name',
                'memType',
                'phone',
                'addressID',
                'loginID'
                ]
            return dict(zip(keys, result)) # save as dict
        
        except Exception as e:
            print(f"Error retrieving personal info for user {user_id}:", e)
            return {}
    def view_personal_info(self, user_id: int) -> dict:
        try:
            self.cursor.execute(
                    """
                    SELECT
                    p.userID,
                    p.email,
                    p.name,
                    p.memType,
                    p.phone,
                    a.StName
                        || ', '
                        || a.City
                        || ', '
                        || a.State
                        || ' '
                        || a.Zip
                        AS full_address
                    FROM Person p
                    LEFT JOIN Address a
                    ON p.addressID = a.addressID
                    WHERE p.userID = %s
                    """,
                    (user_id,)
                )
            result = self.cursor.fetchone()
            if result is None:
                print(f"No user found with ID {user_id}")
                return {}
            # fetchall
            keys = [
                'userID',
                'email',
                'name',
                'memType',
                'phone',
                'full_address'
                ]
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
    
    def update_login_info(self, login_id: int, new_username: str = None, new_password: str = None) -> None:
        try:
            if new_username:
                self.cursor.execute("SELECT loginID FROM Login WHERE Username = %s", (new_username,))
                if self.cursor.fetchone():
                    print("Username already taken.")
                    return # check unique username

                self.cursor.execute("UPDATE Login SET Username = %s WHERE loginID = %s", (new_username, login_id)) # otherwise change username

            if new_password:
                self.cursor.execute("UPDATE Login SET Password = %s WHERE loginID = %s", (new_password, login_id)) # change password

            self.client.commit()
            print("Login info successfully updated.")
        except Exception as e:
            self.client.rollback()
            print("Error updating login info:", e)

    def get_login_details(self, username, password):
        self.cursor.execute("SELECT loginid FROM login WHERE username = %s AND password = %s", (username, password))
        login_result = self.cursor.fetchall()
        if len(login_result) == 0 :
            return None
        login_keys = ['loginid', 'username', 'password']
        login = dict(zip(login_keys, login_result))
        self.cursor.execute("SELECT * FROM Person WHERE loginid = %s", (login['loginid']))

        person_result = self.cursor.fetchall()
        person_keys = ['userID', 'email', 'name', 'memType', 'phone', 'addressID', 'loginID']
        return dict(zip(person_keys, person_result[0]))
    
    



    

    # Member queries

    # SQL to view classes the member is enrolled in (member only)
    def get_enrolled_classes(self, member_id: int) -> list:
        try:
            self.cursor.execute(
                """
                SELECT c.*
                FROM Class c
                JOIN EnrollmentList e ON c.classId = e.classId
                WHERE e.id = %s
                """,
                (member_id,)
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving enrolled classes for member {member_id}:", e)
            return []
        

    def get_classes_with_instructors(self):
        self.cursor.execute("""
            SELECT Class.classid, Class.classname, Person.name, Class.starttime, Class.endtime
            FROM Class
            JOIN Person ON Class.instructorid = Person.userid
        """)
        result = self.cursor.fetchall()
        print(result)
        return result

    
    # SQL to enroll in a class (member only)
    def enroll_in_class(self, member_id: int, class_id: int) -> None:
        try:
            # get start and end time
            self.cursor.execute(
                "SELECT startTime, endTime FROM Class WHERE classId = %s",
                (class_id,)
            )
            new_class = self.cursor.fetchone()
            if not new_class:
                print("Class does not exist.")
                return

            new_start, new_end = new_class

            # use the existing method to get all enrolled classes
            existing_classes = self.get_enrolled_classes(member_id)

            # check for time conflict
            for _, _, _, _, start, end in existing_classes:
                if not (new_end <= start or new_start >= end):
                    print("Time conflict! Enrollment blocked.")
                    return

            # insert into EnrollmentList
            self.cursor.execute(
                "INSERT INTO EnrollmentList (id, classId) VALUES (%s, %s)",
                (member_id, class_id)
            )
            self.client.commit()
            print(f"Member {member_id} successfully enrolled in class {class_id}.")
        except Exception as e:
            self.client.rollback()
            print(f"Error enrolling member {member_id} in class {class_id}:", e)
    
    # SQL for unenrolling from a class (member only)
    def unenroll_from_class(self, member_id: int, class_id: int) -> None:
        try:
            self.cursor.execute(
                """
                DELETE FROM EnrollmentList
                WHERE id = %s AND classId = %s
                """,
                (member_id, class_id)
            )
            if self.cursor.rowcount == 0:
                print(f"No enrollment found for member {member_id} in class {class_id}.")
            else:
                self.client.commit()
                print(f"Member {member_id} successfully unenrolled from class {class_id}.")
        except Exception as e:
            self.client.rollback()
            print(f"Error unenrolling member {member_id} from class {class_id}:", e)


    # SQL to change membership type (members only, for now)
    def change_membership_type(self, member_id: int, new_type: str) -> None:
        try:
            if new_type not in ('monthly', 'yearly'):
                raise ValueError("Invalid membership type")

            self.cursor.execute(
                "UPDATE Person SET memType = %s WHERE userID = %s",
                (new_type, member_id)
            )
            self.client.commit()
            print(f"Membership type changed to {new_type} for user {member_id}")
        except Exception as e:
            self.client.rollback()
            print("Error changing membership type:", e)








    # Administrator queries
    
    # SQL to return all classes (admin and instructors only)
    # this method is ALSO necessary for instructors
    
    def get_class_info(self) -> list:
        self.cursor.execute("""
            SELECT
                c.classId,
                c.instructorID,
                g.gymName   AS gymname,
                c.className,
                c.starTtime,
                c.endTime
            FROM Class AS c
            JOIN Gym   AS g
            ON c.gymID = g.gymID;
        """)
        rows = self.cursor.fetchall()
        keys = ['classid', 'instructorid', 'gymname', 'classname', 'starttime', 'endtime']
        return [dict(zip(keys, r)) for r in rows]

    
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

    # SQL to edit a class
    def edit_class(self, class_id: int, instructor_id: int, gym_id: int, class_name: str, start_time: str, end_time: str) -> None:
        try:
            self.cursor.execute(
                """
                UPDATE Class
                   SET instructorID = %s,
                       gymID = %s,
                       className = %s,
                       startTime = %s, 
                       endTime = %s
                 WHERE classID = %s
                """
                ,
                (instructor_id, gym_id, class_name, start_time, end_time, class_id)
            )
            self.client.commit()
            print("Class successfully added.")
        except Exception as e:
            self.client.rollback()
            print("Error adding class:", e)

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
    
    def get_gym_list(self, admin_id):
        try:
            self.cursor.execute(f"SELECT * FROM Gym WHERE adminid = {admin_id}")
            result = self.cursor.fetchall()
            
            
        
            return result
        except Exception as e:
            self.client.rollback()
            print(f"Error getting gyms for {admin_id}:", e)
            


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

    # SQL to get gym by id (admin only)
    def get_gym_by_id(self, gym_id: int) -> dict:

        try:
            self.cursor.execute(
                """
                SELECT gymid, gymname, gymopen, gymclose, adminid, addressid
                FROM gym
                WHERE gymid = %s
                """,
                (gym_id,)
            )
            row = self.cursor.fetchone()
            if not row:
                return {}
            keys = ['gymid', 'gymname', 'gymopen', 'gymclose', 'adminid', 'addressid']
            return dict(zip(keys, row))
        except Exception as e:
            print(f"Error retrieving gym {gym_id}:", e)
            return {}

    # SQL to add gym (admin only)
    def add_gym(self,
                gymname: str,
                gymopen: str,
                gymclose: str,
                adminid: int,
                addressid: int) -> None:
        try:
            self.cursor.execute(
                """
                INSERT INTO gym (gymname, gymopen, gymclose, adminid, addressid)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (gymname, gymopen, gymclose, adminid, addressid)
            )
            self.client.commit()
            print("Gym added successfully.")
        except Exception as e:
            self.client.rollback()
            print("Error adding gym:", e)

    # SQL to update gym (admin only)
    def update_gym(self,
                   gym_id: int,
                   gymname: str,
                   gymopen: str,
                   gymclose: str,
                   addressid: int) -> None:
        try:
            self.cursor.execute(
                """
                UPDATE gym
                   SET gymname   = %s,
                       gymopen   = %s,
                       gymclose  = %s,
                       addressid = %s
                 WHERE gymid = %s
                """,
                (gymname, gymopen, gymclose, addressid, gym_id)
            )
            self.client.commit()
            print(f"Gym {gym_id} updated successfully.")
        except Exception as e:
            self.client.rollback()
            print(f"Error updating gym {gym_id}:", e)

    # SQL to delete gym (admin only)
    def delete_gym(self, gym_id: int) -> None:
        try:
            self.cursor.execute(
                "DELETE FROM gym WHERE gymid = %s",
                (gym_id,)
            )
            self.client.commit()
            print(f"Gym {gym_id} deleted.")
        except Exception as e:
            self.client.rollback()
            print(f"Error deleting gym {gym_id}:", e)

    # SQL to get all facilities (admin and instructors)
    def get_facilities_list(self) -> list:
        self.cursor.execute("SELECT * FROM Facilities")
        result = self.cursor.fetchall()
        return result # also necessary for all instructors
    
    # SQL to get facility by id (admin only)
    def get_facility_by_id(self, facility_id: int) -> dict:
        try:
            self.cursor.execute(
                """
                SELECT facilityID, facilityName, facilityOpen, facilityClose, gymID
                FROM Facilities
                WHERE facilityID = %s
                """,
                (facility_id,)
            )
            row = self.cursor.fetchone()
            if row is None:
                return {}

            keys = ['id', 'name', 'open', 'close', 'gym_id']
            return dict(zip(keys, row))

        except Exception as e:
            print(f"Error retrieving facility {facility_id}:", e)
            return {}
        
    # SQL to update facility (admin only)
    def update_facility(self,
                        facility_id: int,
                        name: str,
                        open_time: str,
                        close_time: str,
                        gym_id: int) -> None:

        try:
            self.cursor.execute(
                """
                UPDATE Facilities
                   SET facilityName = %s,
                       facilityOpen = %s,
                       facilityClose = %s,
                       gymID = %s
                 WHERE facilityID = %s
                """,
                (name, open_time, close_time, gym_id, facility_id)
            )
            self.client.commit()
            print(f"Facility {facility_id} updated successfully.")
        except Exception as e:
            self.client.rollback()
            print(f"Error updating facility {facility_id}:", e)

    
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
                SELECT
                c.classId,
                p.name        AS instructor_name,
                g.gymName     AS gymname,
                c.className,
                c.startTime,
                c.endTime
                FROM Class AS c
                JOIN Person AS p
                ON c.instructorID = p.userID
                AND p.memType = 'instructor'
                JOIN Gym   AS g
                ON c.gymID = g.gymID
                WHERE c.instructorID = %s
                """,
                (instructor_id,)
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving classes for instructor {instructor_id}:", e)
        return []


    
    def get_enrollment_by_class(self, class_id):
        try:
            self.cursor.execute(
                """
                    SELECT Person.name, Person.email FROM Person 
                    JOIN enrollmentlist ON Person.userID = enrollmentlist.id
                    WHERE enrollmentlist.classid = %s
                   """, (class_id,)
                    )
            
            members = self.cursor.fetchall()
            dictionary = []
            print(members)
            for member in members:
                name = member[0]  # person name
                email = member[1]  # person email   
                dictionary.append({
                    "student_name": name,
                    "student_email": email
                })
            
            return dictionary
        except Exception as e:
            print(f"Error retrieving enrollments for class {class_id}: {e}")
            return []


    def get_enrollment_lists(self, ids, names):
        try:
            enrollment_list = []
            for x in range(len(ids)):
                self.cursor.execute(
                    """
                    SELECT Person.name, Person.email FROM Person 
                    JOIN enrollmentlist ON Person.userID = enrollmentlist.userID
                    WHERE enrollmentlist.class_id = %s
                    """, (ids[x],)
                    )
                members = self.cursor.fetchall()
                cl = names[x]

                dictionary = {
                    "class_name": cl,
                    "members": []
                }

                for member in members:
                    name = member[0]  # person name
                    email = member[1]  # person email
                    dictionary["members"].append({
                        "student_name": name,
                        "student_email": email
                })

                enrollment_list.append(dictionary)

            return enrollment_list
        except Exception as e:
            print(f"Error retrieving enrollments for classes {ids}: {e}")
            return []
        

        #Login/Register
    def add_login(self, username, password):
        try:
            self.cursor.execute("""
                INSERT INTO login (username, password)
                VALUES (%s, %s)
                RETURNING loginid;
                """, (username, password))

            login_id = self.cursor.fetchone()[0]
            self.client.commit()

            return login_id

        except Exception as e:
            self.client.rollback()
            print(f"Failed to add login Username: {username} Password: {password}: {e}")
            return None


    
    #address
    def add_address(self, st_name, city, state, zip):
        try:
            self.cursor.execute("""
                INSERT INTO address (stname, city, state, zip)
                VALUES (%s, %s, %s, %s)
                RETURNING addressid;
                """, (st_name, city, state, zip))

            address_id = self.cursor.fetchone()[0]
            self.client.commit()

            return address_id

        except Exception as e:
            self.client.rollback()  # Undo the transaction if it failed
            print(f"Failed to add address: {st_name} {city} {state} {zip}: {e}")
            return None
        
    def close(self):
        self.cursor.close()
        self.client.close()




    

    

    


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

