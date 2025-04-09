import psycopg2

# basic set up code

print("connect to the db")
client = psycopg2.connect(dbname = "group13", user = "group13", password = "V5ukP3C2", host = "bastion.cs.virginia.edu", port = "5432")

print("create cursor")
cursor = client.cursor()

# after this, remember in the test file to print the query, execute that query, and then fetchall
# example from test.py
# print("SELECT * FROM Person")
# cursor.execute("SELECT * FROM Person")
# result = cursor.fetchall()
# print(result)


# Administrator Queries





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

