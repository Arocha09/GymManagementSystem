from flask import Flask, render_template, request, redirect, session, url_for
from class_defs import Person, Member  
from dbdriver import DB_Driver
import login

app = Flask(__name__)
app.secret_key = "super_secret_key"
driver = DB_Driver()


@app.route("/")
def home():
    return redirect(url_for("log_in"))

@app.route("/login", methods=["GET", "POST"])
def log_in():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Validate user using your Login class or DB_Driver
        user = login.login(username, password)
        user_struct = user.view_personal_info()
        
        if user != None:  # You found a valid user
            session["user_id"] = user_struct["userID"]
            session["username"] = user_struct["name"]
            return redirect(url_for("show_user_info", user_id=user_struct["userID"]))
        else:
            error = "Invalid credentials. Please try again."

    return render_template("login.html", error=error)

@app.route('/user/<int:user_id>')
def show_user_info(user_id):
    result = driver.view_personal_info(user_id)
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

if __name__ == "__main__":
    app.run(debug=True)
