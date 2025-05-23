# TO complete this class we need to finish the routes for the
# admin, and instructor pages. We also need to endure that all pages offered work and no broken links

from flask import Flask, render_template, request, redirect, url_for, session, flash
from dbdriver import DB_Driver
import login
from class_defs import Member, Person, Administrator, Class, Instructor, Address, Login
from datetime import datetime, timedelta

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
        result = db.get_personal_info(user_id)
        print(result)
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
    
def generate_time_options(start, end, interval_minutes):
    time_format_24 = "%H:%M"
    time_format_12 = "%I:%M %p"

    start_time = datetime.strptime(start, time_format_24)
    end_time = datetime.strptime(end, time_format_24)
    options = []

    while start_time <= end_time:
        time_24 = start_time.strftime(time_format_24)
        time_12 = start_time.strftime(time_format_12)
        options.append((time_24, time_12))
        start_time += timedelta(minutes=interval_minutes)

    return options
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
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    raw = db.get_gym_list(session["user_id"])
    gyms = []
    for gym in raw:
        gymid, gymname, gymopen, gymclose, _, addressid = gym

        
        addr = db.get_address_by_id(addressid)
        location = f"{addr.get('stname')}, {addr.get('city')}, {addr.get('state')} {addr.get('zip')}"

        gyms.append({
            'id':       gymid,
            'name':     gymname,
            'address': location,
            'open_time':   gymopen,
            'close_time': gymclose
        })


    return render_template('admin/manage_gyms.html', gyms=gyms) 

@app.route('/admin/gyms/add', methods=['GET','POST'])
def add_gym():
    admin = get_logged_in_user()
    if not admin or session['memType']!='admin':
        return redirect(url_for('home'))

    if request.method=='POST':
        db.add_gym_with_address(
            request.form['st_name'],
            request.form['city'],
            request.form['state'],
            request.form['zip'],
            request.form['name'],       
            request.form['open_time'],  
            request.form['close_time'], 
            admin.userid
        )
        flash('Gym & address added.', 'success')
        return redirect(url_for('manage_gyms'))
    
    time_options = generate_time_options("00:00", "23:30", 30)

    return render_template('admin/add_gym.html', time_options=time_options)


@app.route('/admin/gyms/edit/<int:gym_id>', methods=['GET','POST'])
def edit_gym(gym_id):
    admin = get_logged_in_user()
    if not admin or session.get('memType')!='admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        st_name  = request.form['st_name']
        city     = request.form['city']
        state    = request.form['state']
        zip_code = request.form['zip']
        name       = request.form['name']
        open_time  = request.form['open_time']
        close_time = request.form['close_time']

        db.update_gym_with_address(
            gym_id,
            name, open_time, close_time,
            st_name, city, state, zip_code
        )

        flash('Gym updated!', 'success')
        return redirect(url_for('manage_gyms'))
    gym = db.get_gym_by_id(gym_id)
    address = db.get_address_by_id(gym['addressid'])
    time_options = generate_time_options("00:00", "23:30", 30)

    return render_template('admin/edit_gym.html', gym=gym,address=address,time_options=time_options,)


@app.route('/admin/gyms/delete/<int:gym_id>')
def delete_gym(gym_id):
    admin = get_logged_in_user()
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    db.delete_gym(gym_id)
    flash('Gym deleted successfully!', 'success')
    return redirect(url_for('manage_gyms'))


@app.route('/admin/manage_members')
def manage_members():
    admin = get_logged_in_user()
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    raw = db.get_member_info()
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
        memtype  = request.form['role']      
        phone    = request.form['phone']
        st_name  = request.form['st_name']
        city     = request.form['city']
        state    = request.form['state']
        zip_code = request.form['zip']
        username = request.form['username']
        password = request.form['password']

        db.add_member(
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
    if not admin or session['memType']!='admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        personal = {
            'email':  request.form['email'],
            'name':   request.form['name'],
            'memType': request.form['role'],
            'phone':  request.form['phone']
        }
        address = {
            'st_name':   request.form['st_name'],
            'city':      request.form['city'],
            'state':     request.form['state'],
            'zip_code':  request.form['zip']
        }
        db.update_member(user_id, personal, address)
        flash('Member and address updated.', 'success')
        return redirect(url_for('manage_members'))
    user = db.get_personal_info(user_id)
    db.cursor.execute(
        "SELECT stname,city,state,zip FROM address WHERE addressid=%s",
        (user['addressID'],)
    )
    st,ct,stt,zipc = db.cursor.fetchone()
    return render_template('admin/edit_user.html',
                           user=user,
                           address={'st_name':st,'city':ct,'state':stt,'zip':zipc})

@app.route('/admin/members/delete/<int:user_id>')
def delete_user(user_id):
    admin = get_logged_in_user()
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    db.delete_member(user_id)
    flash('Member deleted successfully!', 'success')
    return redirect(url_for('manage_members'))


@app.route('/admin/instructors')
def manage_instructors():
    admin = get_logged_in_user()
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    # Returns list of tuples: (userID, email, name, memType, phone, addressID, loginID)
    raw = db.get_instructor_info()
    users = [{
        'id':    row[0],
        'email': row[1],
        'name':  row[2],
        'phone': row[4]
    } for row in raw]

    return render_template('admin/manage_instructors.html', users=users)

@app.route('/admin/instructors/add', methods=['GET', 'POST'])
def add_instructor():
    admin = get_logged_in_user()
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        email    = request.form['email']
        name     = request.form['name']
        phone    = request.form['phone']
        st_name  = request.form['st_name']
        city     = request.form['city']
        state    = request.form['state']
        zip_code = request.form['zip']
        username = request.form['username']
        password = request.form['password']

        db.add_instructor(
            email, name, phone,
            st_name, city, state, zip_code,
            username, password
        )
        flash('Instructor added successfully!', 'success')
        return redirect(url_for('manage_instructors'))

    return render_template('admin/add_instructor.html')


@app.route('/admin/instructors/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_instructor(user_id):
    admin = get_logged_in_user()
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        updates = {
            'email': request.form['email'],
            'name':  request.form['name'],
            'phone': request.form['phone']
        }
        db.update_personal_info(user_id, updates)
        flash('Instructor updated successfully!', 'success')
        return redirect(url_for('manage_instructors'))

    user = db.view_personal_info(user_id)
    return render_template('admin/edit_instructor.html', user=user)


@app.route('/admin/instructors/delete/<int:user_id>')
def delete_instructor(user_id):
    admin = get_logged_in_user()
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    db.delete_instructor(user_id)
    flash('Instructor deleted successfully!', 'success')
    return redirect(url_for('manage_instructors'))

#TODO: Test
@app.route('/admin/classes')
def manage_classes():
    admin = get_logged_in_user()
    classes = admin.get_classes_with_instructors()
    
    return render_template('admin/manage_classes.html', classes=classes)  # your logic here

@app.route('/admin/classes/add', methods=['GET', 'POST'])
def add_class():
    admin = get_logged_in_user()
    if not admin:
        return redirect(url_for('home'))

    if request.method == 'POST':
        instructor = request.form['instructor']
        gym_id     = request.form['gym_id']
        class_name = request.form['class_name']
        start_time = request.form['start_time']
        end_time   = request.form['end_time']

        admin.add_class(class_name, instructor, gym_id, start_time, end_time)
        return redirect(url_for('manage_classes'))

    # GET: we need to populate the dropdowns
    instructors = admin.get_instructors()  # returns list of Person objects with memType='instructor'
    gyms        = admin.get_gyms()         # returns list of Gym objects
    return render_template(
        'admin/add_class.html',
        instructors=instructors,
        gyms=gyms
    )


@app.route('/admin/facilities')
def manage_facilities():
    admin = get_logged_in_user()
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    raw = db.get_facilities_list()
    facilities = [{
        'id':     r[0],
        'name':   r[1],
        'open':   r[2],
        'close':  r[3],
        'gym_id': r[4]
    } for r in raw]

    return render_template('admin/manage_facilities.html', facilities=facilities)


@app.route('/admin/facilities/add', methods=['GET','POST'])
def add_facility():
    admin = get_logged_in_user()
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        name       = request.form['name']
        open_time  = request.form['open_time']
        close_time = request.form['close_time']
        gym_id     = request.form['gym_id']

        db.add_facility(name, open_time, close_time, gym_id)
        flash('Facility added successfully!', 'success')
        return redirect(url_for('manage_facilities'))
    
    time_options = generate_time_options("00:00", "23:30", 30)

    return render_template('admin/add_facility.html', time_options=time_options)

@app.route('/admin/facilities/edit/<int:facility_id>', methods=['GET','POST'])
def edit_facility(facility_id):
    admin = get_logged_in_user()
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        name       = request.form['name']
        open_time  = request.form['open_time']
        close_time = request.form['close_time']
        gym_id     = request.form['gym_id']

        db.update_facility(facility_id, name, open_time, close_time, gym_id)
        flash('Facility updated successfully!', 'success')
        return redirect(url_for('manage_facilities'))
    
    time_options = generate_time_options("00:00", "23:30", 30)
    facility = db.get_facility_by_id(facility_id)
    return render_template('admin/edit_facility.html', facility=facility, time_options=time_options)


@app.route('/admin/facilities/delete/<int:facility_id>')
def delete_facility(facility_id):
    admin = get_logged_in_user()
    if not admin or session.get('memType') != 'admin':
        return redirect(url_for('home'))

    db.delete_facility(facility_id)
    flash('Facility deleted successfully!', 'success')
    return redirect(url_for('manage_facilities'))



#Instructor Routes

@app.route('/instructor')
def instructor_dashboard():
    print(session)
    if 'user_id' not in session or session['memType'] != 'instructor':
        return redirect(url_for('home'))
    
    instructor = get_logged_in_user()
    info = instructor.view_personal_info()
    classes = instructor.get_class_table()
    return render_template('instructor/instructor_dashboard.html',info = info, classes=classes)

# @app.route('/instructor/classes')
# def view_classes():
#     instructor = get_logged_in_user()
#     classes = instructor.get_class_table()
#     return render_template('admin/manage_classes.html', classes=classes)


@app.route('/instructor/view_enrollments/<int:class_id>')
def view_enrollments(class_id):
    instructor = get_logged_in_user()
    students = instructor.get_enrollments_by_class(class_id)

    return render_template('instructor/enrollments.html', students=students, class_id=class_id)

@app.route('/instructor/classes_and_enrollments')
def view_classes_and_enrollments():
    if not session.get("user_id"):
        return redirect(url_for('home'))
    instructor = get_logged_in_user()
    classes = instructor.get_class_table()

    return render_template('instructor/classes_and_enrollments.html', classes=classes)





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
    print("CLASS:" + class_id)
    
    db.add_member_to_class(member_id, class_id)
    
    return redirect(url_for('member_dashboard'))

@app.route('/unenroll', methods=['POST'])
def unenroll():
    if 'user_id' not in session or session.get('memType') not in ['monthly', 'yearly']:
        return redirect(url_for('log_in'))
    
    class_id = request.form.get('class_id')
    member_id = session['user_id']
    print("CLASS:" + class_id)
    db.unenroll_from_class(member_id, class_id)
    
    return redirect(url_for('member_dashboard'))

@app.route("/all_classes")
def all_classes():
    user = get_logged_in_user()
    result = db.get_class_info()
    enrolled_classes = db.get_enrolled_classes(user.view_personal_info()['userID'])
    classes = []
    enrolled_ids = []
    for item in result:
        instructorName = db.get_instructor_name(item['instructor_id'])
        c = Class(item['class_id'],
                  item['instructor_id'],
                  item['gym_name'],
                  item['class_name'],
                  item['start_time'],
                  item['end_time'])
        d = {'class': c, 'instructorName': instructorName[0]}
        classes.append(d)
    for item in enrolled_classes:
        print(item)
        enrolled_ids.append(item[0])
    return render_template('member/all_classes.html',
                         classes=classes, enrolled_ids=enrolled_ids
                        )



#Classes Routes
@app.route('/classes/edit/<int:class_id>', methods=['GET', 'POST'])
def edit_class(class_id):
    user = get_logged_in_user()
    gym_classes = user.get_og_class_table()

    gym_class = next((c for c in gym_classes if c.class_id == class_id), None)
    if not gym_class:
        flash('Class not found.', 'danger')
        return redirect(url_for('manage_classes'))
    
    

    if request.method == 'POST':
        gym_class['class_name'] = request.form['name']
        gym_class["instructor"] = request.form['instructor']
        gym_class['start'] = request.form['start_time']
        gym_class['end'] = request.form['end_time']
        
        #TODO: Write the edit class file in dbdriver.
        db.edit_class()
        flash('Class updated successfully!', 'success')
        return redirect(url_for('manage_classes'))

    time_options = generate_time_options("06:00", "18:00", 30)

    return render_template('classes/edit_class.html', gym_class=gym_class, time_options=time_options)



@app.route('/classes/delete/<int:class_id>', methods=['GET'])
def delete_class(class_id):
    user = get_logged_in_user()
    gym_classes = user.get_og_class_table()
    gym_classes = [c for c in gym_classes if c.class_id != class_id]
    db.delete_class(class_id=class_id)
    flash('Class deleted successfully.', 'success')
    return redirect(url_for('manage_classes'))



#Login and Register Routes

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))



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
    db.close()
    
