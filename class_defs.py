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
        self.driver = DB_Driver()

    def get_class_table(self):
        
        classes_result = self.driver.get_class_info()
        classes = []
        for result in classes_result:
            class_id = result[0]
            instructor_id = result[1]
            gym_id = result[2]
            class_name = result[3]
            start_time = result[4]
            end_time = result[5]
            classes.append(Class(class_id, instructor_id, gym_id, class_name, start_time, end_time))
        
        print(classes)
    
    

class Administrator(Person):
    pass

class Instructor(Person):
    pass

class Member(Person):
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


class Gym():
    def __init__(self, gym_id, gym_name, gym_open, gym_close, admin_id, address_id):
        self.gym_id = gym_id
        self.gym_name = gym_name
        self.gym_open = gym_open
        self.gym_close = gym_close
        self.admin_id = admin_id
        self.address_id = address_id

class Facilities():
    def __init__(self, facility_id, facility_name, facility_open, facility_close, gym_id):
        self.facility_id = facility_id
        self.facility_name = facility_name
        self.facility_open = facility_open
        self.facility_close = facility_close
        self.gym_id = gym_id

class Login():
    def __init__(self, login_id, username, password):
        self.login_id = login_id
        self.username = username
        self.password = password
