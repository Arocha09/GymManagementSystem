# TO complete this class we need to finish the routes for the
# admin, and instructor pages. We also need to endure that all pages offered work and no broken links

from flask import Flask, render_template, request, redirect, url_for, session, flash
from dbdriver import DB_Driver
import login
from class_defs import Member, Person, Administrator, Class, Instructor, Address, Login

app = Flask(__name__)
app.secret_key = 'dev'  # Replace with a strong secret in prod

db = DB_Driver()

@app.route("/")
def home():
    return redirect(url_for("log_in"))

@app.route("/login", methods = ['POST', 'GET'])
def log_in():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = login.login(username, password)
        if user is not None:
            user_struct = user.view_personal_info()
            session["user_id"] = user_struct["userID"]
            session["username"] = user_struct["name"]
            session["memType"] = user_struct["memType"]

            if user_struct["memType"] in ['monthly', 'yearly']:
                return redirect(url_for('member_dashboard'))
            elif user_struct["memType"] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user_struct["memType"] == 'instructor':
                return redirect(url_for('instructor_dashboard'))
        else:
            error = "Invalid credentials. Please try again."

    return render_template("login.html", error=error)


def get_logged_in_user():
    if 'user_id' not in session:
        return None
    else:
        user_id = session["user_id"]
        result = db.view_personal_info(user_id)
        if session.get('memType') == 'admin':
            if result and result['memType'] == "admin":
                return Administrator(
                    result['userID'],
                    result['email'],
                    result['name'],
                    result['memType'],
                    result['phone'],
                    result['addressID'],
                    result['loginID']
                )
        elif session.get('memType') == 'instructor':
            if result and result['memType'] == "instructor":
                return Instructor(
                    result['userID'],
                    result['email'],
                    result['name'],
                    result['memType'],
                    result['phone'],
                    result['addressID'],
                    result['loginID']
                )
        elif session.get('memType') in ['monthly', 'yearly']:
            if result and result['memType'] == "monthly" or result['memType'] == 'yearly':
                return Member(
                    result['userID'],
                    result['email'],
                    result['name'],
                    result['memType'],
                    result['phone'],
                    result['addressID'],
                    result['loginID']
                )
    return None
    
# Admin Routes

#TODO: Test
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('memType') != 'admin':
        return redirect(url_for('home'))
    
    return render_template('admin/admin_dashboard.html')

#TODO: Test
@app.route('/admin/gyms')
def manage_gyms():
    admin = get_logged_in_user()
    gyms = admin.get_gyms()
    return render_template('admin/manage_gyms.html', gyms=gyms)

@app.route('/admin/members')
def manage_members():
    admin = get_logged_in_user()
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    raw = admin.driver.get_member_info()
    users = [{
        'id':    row[0],
        'email': row[1],
        'name':  row[2],
        'role':  row[3]
    } for row in raw]

    return render_template('admin/manage_members.html', users=users)

@app.route('/admin/members/add', methods=['GET', 'POST'])
def add_user():
    admin = get_logged_in_user()
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        email    = request.form['email']
        name     = request.form['name']
        memtype  = request.form['role']      # “monthly” or “yearly”
        phone    = request.form['phone']
        st_name  = request.form['st_name']
        city     = request.form['city']
        state    = request.form['state']
        zip_code = request.form['zip']
        username = request.form['username']
        password = request.form['password']

        # This uses your existing DB_Driver.add_member
        admin.driver.add_member(
            email, name, memtype, phone,
            st_name, city, state, zip_code,
            username, password
        )
        flash('Member added successfully!', 'success')
        return redirect(url_for('manage_members'))

    return render_template('admin/add_user.html')

@app.route('/admin/members/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    admin = get_logged_in_user()
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        updates = {
            'email':   request.form['email'],
            'name':    request.form['name'],
            'memType': request.form['role'],
            'phone':   request.form['phone']
        }
        # Update the Person row
        admin.driver.update_personal_info(user_id, updates)
        flash('Member updated successfully!', 'success')
        return redirect(url_for('manage_members'))

    # GET: load current info
    user = admin.driver.view_personal_info(user_id)
    return render_template('admin/edit_user.html', user=user)

@app.route('/admin/members/delete/<int:user_id>')
def delete_user(user_id):
    admin = get_logged_in_user()
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    admin.driver.delete_member(user_id)
    flash('Member deleted successfully!', 'success')
    return redirect(url_for('admin/manage_members'))


@app.route('/admin/instructors')
def manage_instructors():
    admin = get_logged_in_user()
    # TODO: Implement
    # #members = admin.get_members() 
    # return render_template('manage_users.html', users=)  # your logic here
    pass

#TODO: Test
@app.route('/admin/classes')
def manage_classes():
    admin = get_logged_in_user()
    classes = admin.get_class_table()
    return render_template('admin/manage_classes.html', classes=classes)  # your logic here

@app.route('/classes', methods=['GET', 'POST'])
def add_class():
    #TODO: Finish implementation
    admin = get_logged_in_user()
    if not admin:
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Get form data

        instructor = request.form.get('instructor')
        gym_id = request.form.get('gym_id')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        class_name = request.form.get('class_name')

        admin.driver.add_class(instructor, gym_id, class_name, start_time, end_time)

        
        return redirect(url_for('add_class'))

    # For GET requests, just show the form
    return render_template('admin/manage_classes.html', admin=admin)


@app.route('/admin/facilities')
def manage_facilities():
    pass 
    #TODO: Implement
    # return render_template('manage_facilities.html', facilities=...)  # your logic here


#Instructor Routes

@app.route('/instructor')
def instructor_dashboard():
    print(session)
    if 'user_id' not in session or session['memType'] != 'instructor':
        return redirect(url_for('home'))
    
    instructor = get_logged_in_user()
    instructor.view_personal_info()
    classes = instructor.get_class_table()
    return render_template('instructor/instructor_dashboard.html', classes=classes)

# @app.route('/instructor/classes')
# def view_classes():
#     instructor = get_logged_in_user()
#     classes = instructor.get_class_table()
#     return render_template('admin/manage_classes.html', classes=classes)


# @app.route('/instructor/enrollments')
# def view_enrollments():
#     instructor = get_logged_in_user()
#     #TODO: the get_enrollments needs to be coded
#     enrollments = instructor.get_enrollments() 
#     return render_template('instructor/view_enrollments.html', enrollments=enrollments)

@app.route('/instructor/classes_and_enrollments')
def view_classes_and_enrollments():
    if not session.get("user_id"):
        return redirect(url_for('home'))
    instructor = get_logged_in_user()
    enrollments = instructor.get_enrollments()  # uses your code above

    return render_template('instructor/classes_and_enrollments.html', classes=enrollments)





#Member Routes

@app.route('/member', methods=['GET', 'POST'])
def member_dashboard():
    # Check if user is logged in and is a member
    if 'user_id' not in session or session.get('memType') not in ['monthly', 'yearly']:
        return redirect(url_for('home'))
    
    member = get_logged_in_user()
    if member:
        classes = member.view_my_classes()
        return render_template("member/member_info.html", info=member.view_personal_info(), classes=classes)
    return render_template("user_info.html", info= None)

@app.route('/enroll', methods=['POST'])
def enroll():
    if 'user_id' not in session or session.get('memType') not in ['monthly', 'yearly']:
        return redirect(url_for('log_in'))
    
    class_id = request.form.get('class_id')
    member_id = session['user_id']
    
    db.add_member_to_class(member_id, class_id)
    
    return redirect(url_for('member_dashboard'))

@app.route("/classes")
def all_classes():
    result = db.get_class_info()
    classes = []
    for item in result:
        c = Class(item['classid'],
                  item['instructorid'],
                  item['gymid'],
                  item['classname'],
                  item['starttime'],
                  item['endtime'])
        classes.append(c)
    return render_template('member/all_classes.html',
                         classes=classes,
                        )



#Classes Routes
@app.route('/classes/edit/<int:class_id>', methods=['GET', 'POST'])
def edit_class(class_id):
    user = get_logged_in_user()
    gym_classes = user.get_class_table()

    gym_class = next((c for c in gym_classes if c.class_id == class_id), None)
    if not gym_class:
        flash('Class not found.', 'danger')
        return redirect(url_for('manage_classes'))

    if request.method == 'POST':
        gym_class['name'] = request.form['name']
        gym_class['instructor'] = request.form['instructor']
        gym_class['start'] = request.form['start_time']
        gym_class['end'] = request.form['end_time']
        
        #TODO: Write the edit class file in dbdriver.
        db.edit_class()
        flash('Class updated successfully!', 'success')
        return redirect(url_for('manage_classes'))

    return render_template('classes/edit_class.html', gym_class=gym_class)



@app.route('/classes/delete/<int:class_id>', methods=['GET'])
def delete_class(class_id):
    global gym_classes
    gym_classes = [c for c in gym_classes if c.class_id != class_id]
    db.delete_class(class_id=class_id)
    flash('Class deleted successfully.', 'success')
    return redirect(url_for('manage_classes'))



#Login and Register Routes

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))



# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         name = request.form.get('name')
#         phone = request.form.get('phone')
#         st_name = request.form.get('st_name')
#         city = request.form.get('city')
#         state = request.form.get('state')
#         zip_code = request.form.get('zip')  # renamed to avoid shadowing Python's zip()
#         username = request.form.get('username')
#         password = request.form.get('password')
#         mem_type = request.form.get('memType')

#         # Basic validation
#         if not all([email, name, phone, st_name, city, state, zip_code, username, password, mem_type]):
#             return render_template('register.html', error="All fields are required.")

#         try:
#             # Create address and insert into DB
#             address = Address(
#                 address_id=None,  # or None if auto-incremented
#                 st_name=st_name,
#                 city=city,
#                 state=state,
#                 zip=zip_code
#             )
#             address_id = address.add_address()

#             # Create login and insert into DB
#             login = Login(
#                 login_id=None,  # or None if auto-incremented
#                 username=username,
#                 password=password
#             )
#             login_id = login.add_login()

#             # Create user and insert into DB
#             new_user = Person(
#                 user_id=None,  # or None if auto-incremented
#                 email=email,
#                 name=name,
#                 memtype=mem_type,
#                 phone=phone,
#                 address_id=address_id,
#                 login_id=login_id
#             )
#             new_user.add_person()  # Assuming you have this method defined

#             return redirect(url_for('home'))

#         except Exception as e:
#             # Log the error if needed
#             print(f"Registration error: {e}")
#             return render_template('register.html', error="An error occurred while creating your account. Please try again.")

#     return render_template('register.html')

@app.route('/my_enrollments')
def my_enrollments():
    member = get_logged_in_user()
    if not member: return redirect(url_for('home'))
    classes = member.view_my_classes()
    return render_template('member/my_enrollments.html', classes=classes)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        st_name = request.form.get('st_name')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zip')  # renamed to avoid shadowing Python's zip()
        username = request.form.get('username')
        password = request.form.get('password')
        mem_type = request.form.get('memType')

        # Basic validation
        if not all([email, name, phone, st_name, city, state, zip_code, username, password, mem_type]):
            return render_template('register.html', error="All fields are required.")

        try:
            # Call the add_member method to handle address, login, and person creation
             # Assuming you have an instance of the Person class
            db.add_member(email, name, mem_type, phone, st_name, city, state, zip_code, username, password)

            return redirect(url_for('home'))

        except Exception as e:
            # Log the error if needed
            print(f"Registration error: {e}")
            return render_template('register.html', error="An error occurred while creating your account. Please try again.")

    return render_template('register.html')



if __name__ == '__main__':
    app.run(debug=True)
