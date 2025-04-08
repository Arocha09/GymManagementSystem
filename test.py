#This is an example file that shows how to use the psycopg2 
import psycopg2

print("connect to the db")
client = psycopg2.connect(dbname = "group13", user = "group13", password = "V5ukP3C2", host = "bastion.cs.virginia.edu", port = "5432")

print("create cursor")
cursor = client.cursor()

print("SELECT * FROM Person")
cursor.execute("SELECT * FROM Person")
result = cursor.fetchall()

print(result)