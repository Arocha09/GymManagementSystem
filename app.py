from flask import Flask, render_template, request, redirect, url_for, session
from dbdriver import DB_Driver
import login
from class_defs import Member, Person, Class

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
            session["memType"] = user_struct["memType"]  # Store memType in session

            if user_struct["memType"] in ['monthly', 'yearly']:
                return redirect(url_for('member_dashboard'))
            # elif user_struct["memType"] == 'admin':
            #     return redirect(url_for('admin_dashboard'))
            # elif user_struct["memType"] == 'instructor':
            #     return redirect(url_for('instructor_dashboard'))
        else:
            error = "Invalid credentials. Please try again."

    return render_template("login.html", error=error)


# @app.route('/admin')
# def admin_dashboard():
#     if not session.get('user') or session['user']['memType'] != 'admin':
#         return redirect(url_for('home'))
#     return render_template('admin_dashboard.html')

# @app.route('/instructor')
# def instructor_dashboard():
#     if not session.get('user') or session['user']['memType'] != 'instructor':
#         return redirect(url_for('home'))
#     instructor_id = session['user']['id']
#     classes = db.get_instructor_classes(instructor_id)
#     return render_template('instructor_dashboard.html', classes=classes)

@app.route('/member', methods=['GET', 'POST'])
def member_dashboard():
    # Check if user is logged in and is a member
    if 'user_id' not in session or session.get('memType') not in ['monthly', 'yearly']:
        return redirect(url_for('home'))
    
    user_id = session["user_id"]
    result = db.view_personal_info(user_id)
    if result['memType'] == "monthly" or result['memType'] == "yearly":
        new_member = Member(result['userID'],
                        result['email'],
                        result['name'],
                        result['memType'],        
                        result['phone'],
                        result['addressID'],
                        result['loginID']        
        )
        classes = new_member.view_my_classes()
        return render_template("member_info.html", info=result, classes=classes)
    return render_template("user_info.html", info=result)

@app.route('/enroll', methods=['POST'])
def enroll():
    if 'user_id' not in session or session.get('memType') not in ['monthly', 'yearly']:
        return redirect(url_for('log_in'))
    
    class_id = request.form.get('class_id')
    member_id = session['user_id']
    
    # Add enrollment logic
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
    return render_template('all_classes.html',
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
