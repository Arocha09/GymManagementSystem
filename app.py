# TO complete this class we need to finish the routes for the
# admin, and instructor pages. We also need to endure that all pages offered work and no broken links

from flask import Flask, render_template, request, redirect, url_for, session, flash
from dbdriver import DB_Driver
import login
from class_defs import Member, Person, Administrator, Class

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
            # elif user_struct["memType"] == 'instructor':
            #     return redirect(url_for('instructor_dashboard'))
        else:
            error = "Invalid credentials. Please try again."

    return render_template("login.html", error=error)


def get_logged_in_admin():
    if 'user_id' not in session or session.get('memType') != 'admin':
        return None
    user_id = session["user_id"]
    result = db.view_personal_info(user_id)
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
    return None

#TODO: Test
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('memType') != 'admin':
        return redirect(url_for('home'))
    
    return render_template('admin/admin_dashboard.html')

#TODO: Test
@app.route('/admin/gyms')
def manage_gyms():
    admin = get_logged_in_admin()
    gyms = admin.get_gyms()
    return render_template('manage_gyms.html', gyms=gyms)

@app.route('/admin/members')
def manage_members():
    admin = get_logged_in_admin()
    # TODO: Implement
    # #members = admin.get_members() 
    # return render_template('manage_users.html', users=)  # your logic here
    pass

@app.route('/admin/instructors')
def manage_instructors():
    admin = get_logged_in_admin()
    # TODO: Implement
    # #members = admin.get_members() 
    # return render_template('manage_users.html', users=)  # your logic here
    pass

#TODO: Test
@app.route('/admin/classes')
def manage_classes():
    admin = get_logged_in_admin()
    classes = admin.get_class_table()
    return render_template('admin/manage_classes.html', classes=classes)  # your logic here

@app.route('/admin/classes', methods=['GET', 'POST'])
def add_class():
    #TODO: Finish implementation
    admin = get_logged_in_admin()
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
    return render_template('manage_classes.html', admin=admin)


@app.route('/admin/facilities')
def manage_facilities():
    pass 
    #TODO: Implement
    # return render_template('manage_facilities.html', facilities=...)  # your logic here



# @app.route('/instructor')
# def instructor_dashboard():
#     if not session.get('user') or session['user']['memType'] != 'instructor':
#         return redirect(url_for('home'))
#     instructor_id = session['user']['id']
#     classes = db.get_instructor_classes(instructor_id)
#     return render_template('instructor_dashboard.html', classes=classes)
def get_logged_in_member():
    if 'user_id' not in session or session.get('memType') not in ['monthly', 'yearly']:
        return None
    user_id = session["user_id"]
    result = db.view_personal_info(user_id)
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

@app.route('/member', methods=['GET', 'POST'])
def member_dashboard():
    # Check if user is logged in and is a member
    if 'user_id' not in session or session.get('memType') not in ['monthly', 'yearly']:
        return redirect(url_for('home'))
    
    member = get_logged_in_member()
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
def display_classes():
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         email = request.form.get('email')
#         mem_type = request.form.get('memType')

#         # Validate inputs (this part can be extended based on your requirements)
#         if not username or not password or not email:
#             return render_template('register.html', error="All fields are required.")

#         # Call db.create_login() and db.create_person() to save the user in the database
#         db.create_login(username, password, email, mem_type)  # You should implement this
#         db.create_person(username, email, mem_type)  # Create additional user data if needed
        
#         return redirect(url_for('home'))  # Redirect to login or home page after successful registration
    
#     return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
