from dbdriver import DB_Driver


class Person():
    
    def __init__(self, user_id, email, name, memtype, phone, address_id, login_id):
        self.userid = user_id
        self.email = email
        self.name = name
        self.memtype = memtype
        self.phone = phone
        self.addressid = address_id
        self.loginid = login_id


    def get_og_class_table(self):
        driver = DB_Driver()
        classes_result = driver.get_og_class_info()
        classes = []
        for result in classes_result:
            c = Class(
                class_id      = result['classid'],
                instructor_id = result['instructorid'],
                gym_id      = result['gymid'],
                class_name    = result['classname'],
                start_time    = result['starttime'],
                end_time      = result['endtime']
            )
            classes.append(c)
        driver.close()
        return classes
    
    def get_class_table(self):
        driver = DB_Driver()
        classes_result = driver.get_class_info()
        driver.close()
        return classes_result


    def get_personal_info(self):
        return 
    def view_personal_info(self):
        driver = DB_Driver()
        info = driver.view_personal_info(self.userid)
        driver.close()
        return info

    def update_personal_info(self, updates: dict):
        driver = DB_Driver()
        driver.update_personal_info(self.userid, updates)
        for key, value in updates.items():
            setattr(self, key.lower(), value)  # sync local object!

        driver.close()
    
    def update_login_info(self, new_username=None, new_password=None):
        driver = DB_Driver()
        driver.update_login_info(self.loginid, new_username, new_password)
        if new_username:
            self.username = new_username
        if new_password:
            self.password = new_password
        driver.close()
    def get_classes_with_instructors(self):
        driver = DB_Driver()
        classes_result = driver.get_classes_with_instructors()
        classes =[]        
        for result in classes_result:
            classes.append({
                'class_id': result[0],
                'class_name': result[1],
                'instructor_name': result[2],
                'start_time': result[3],
                'end_time': result[4]
            })
        driver.close()
        return classes

    

class Administrator(Person):
    def get_gyms(self):
        driver = DB_Driver()
        result = driver.get_gym_list(self.userid)
        gym_list = []
        for res in result:
            gym = Gym(  
                    gym_id = res[0], 
                    gym_name = res[1], 
                    gym_open= res[2], 
                    gym_close= res[3], 
                    admin_id = res[4], 
                    address_id= res[5]
                    )
            gym_list.append(gym)
        driver.close()
        return gym_list
    
    def get_instructors(self):
        driver = DB_Driver()
        result = driver.get_instructor_info()
        instructor_list = []
        for res in result:
            instructor = Person(
                user_id=res[0],
                email=res[1],
                name=res[2],
                memtype=res[3],
                phone=res[4],
                address_id=res[5],
                login_id=res[6]
            )
            instructor_list.append(instructor)
        driver.close()
        return instructor_list
    
    def add_class(self, class_name, instructor_id, gym_id, start_time, end_time):
        driver = DB_Driver()
        driver.add_class(class_name, instructor_id, gym_id, start_time, end_time)
        driver.close()
    
    def delete_class(self, class_id):
        driver = DB_Driver()
        driver.delete_class(class_id)
        driver.close()

class Instructor(Person):
    def add_member_to_class(self, member_id, class_id):
        driver = DB_Driver()
        driver.add_member_to_class(member_id, class_id)
        driver.close()


    def remove_member_from_class(self, member_id, class_id):
        driver = DB_Driver()
        driver.remove_member_from_class(member_id, class_id)
        driver.close()
    

    def view_my_classes(self):
        driver = DB_Driver()
        results = driver.get_instructor_classes(self.userid)
        classes = []
        for (
            class_id,
            instructor_id,
            instructor_name,
            gym_name,
            class_name,
            start_time,
            end_time
        ) in results:
            classes.append(
                Class(
                    class_id=class_id,
                    instructor_id=instructor_id,
                    instructor_name=instructor_name,
                    gym_name=gym_name,
                    class_name=class_name,
                    start_time=start_time,
                    end_time=end_time
                )
            )

        print("Your Classes:")
        for c in classes:
            # Only show class ID, name, instructor name, gym name, times
            print(f"{c.class_id}: “{c.class_name}” with {c.instructor_name} @ {c.gym_name} "
                    f"({c.start_time}–{c.end_time})")
        
        driver.close()

        return classes


    
    def get_enrollments(self):
        classes = self.view_my_classes()
        class_ids = [c.class_id for c in classes ]
        class_names = [c.class_name for c in classes]
        enrollments = self.driver.get_enrollment_lists(class_ids, class_names)

        return enrollments
    pass

    def get_enrollments_by_class(self, class_id):
        driver = DB_Driver()
        enrollment = driver.get_enrollment_by_class(class_id=class_id)
        driver.close()
        return enrollment


class Member(Person):
    def view_my_classes(self):
        driver = DB_Driver()
        results = driver.get_enrolled_classes(self.userid)
        classes = []
        for result in results:
            class_id = result[0]
            instructor_id = result[1]
            gym_id = result[2]
            class_name = result[3]
            start_time = result[4]
            end_time = result[5]
            classes.append(Class(class_id, instructor_id, gym_id, class_name, start_time, end_time))

        print("You are enrolled in:")
        for c in classes:
            print(c)
        driver.close()
        return classes

    def enroll_in_class(self, class_id):
        driver = DB_Driver()
        driver.enroll_in_class(self.userid, class_id)
        driver.close()

    def unenroll_from_class(self, class_id):
        driver = DB_Driver()
        driver.unenroll_from_class(self.userid, class_id)
        driver.close()

    def change_membership_type(self, new_type):
        driver = DB_Driver()
        driver.change_membership_type(self.userid, new_type)
        self.memtype = new_type  # update local attribute to be consistent
        driver.close()
    pass

class Class():
    def __init__(self, class_id, instructor_id, gym_id, class_name, start_time, end_time):
        self.class_id = class_id
        self.instructor = instructor_id
        self.gym_id = gym_id
        self.class_name = class_name
        self.start_time = start_time
        self.end_time = end_time
    def __repr__(self):
        return (
            f"Class(class_id={self.class_id}, name='{self.class_name}', "
            f"instructor={self.instructor}, gym={self.gym_id}, "
            f"start='{self.start_time}', end='{self.end_time}')"
        )
    
    def get_instructor_name(self):
        driver = DB_Driver()
        name = driver.get_instructor_name(self.instructor)
        driver.client.close()
        return name
        

class EnrollmentList():
    def __init__(self, user_id, class_id):
        self.user_id = user_id
        self.class_id = class_id


class Address():
    def __init__(self, address_id, st_name, city, state, zip):
        self.address_id = address_id
        self.st_name = st_name
        self.city = city
        self.state = state
        self.zip = zip
        
    
    def add_address(self):
        driver = DB_Driver()
        address_id = driver.add_address(self.st_name, self.city, self.state, self.zip)
        driver.close()
        return address_id
    


class Gym():
    def __init__(self, gym_id, gym_name, gym_open, gym_close, admin_id, address_id):
        self.gym_id = gym_id
        self.gym_name = gym_name
        self.gym_open = gym_open
        self.gym_close = gym_close
        self.admin_id = admin_id
        self.address_id = address_id

    def get_gym_keys():
        return ['gymID', 'gymName', 'gymOpen', 'gymClose', 'adminID', 'addressID']
    
    

class Facilities():
    def __init__(self, facility_id, facility_name, facility_open, facility_close, gym_id):
        self.facility_id = facility_id
        self.facility_name = facility_name
        self.facility_open = facility_open
        self.facility_close = facility_close
        self.gym_id = gym_id
    

    def get_facilities_list(self):
        driver = DB_Driver()
        facilities_result = driver.get_facilities_list()
        facilities = []
        for result in facilities_result:
            facility_id = result[0]
            facility_name = result[1]
            facility_open_time = result[2]
            facility_close_time = result[3]
            facility_gym_id = result[4]
            facilities.append(Facilities(facility_id, facility_name, facility_open_time, facility_close_time, facility_gym_id))
        
        driver.close()
        print(facilities)

class Login():
    def __init__(self, login_id, username, password):
        self.login_id = login_id
        self.username = username
        self.password = password
        self.driver = DB_Driver()
    
    def add_login(self):
        driver = DB_Driver()

        login_id = driver.add_login(self.username, self.password)
        driver.close()

        return login_id
