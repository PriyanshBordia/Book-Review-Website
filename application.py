import os
import requests

from flask import Flask, render_template, session, request, url_for, redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not "postgres://bezoopliubauew:ff447efa87a96336c27fa8c83def232d790d8b48f8da38e236259b4f447926f7@ec2-46-137-84-140.eu-west-1.compute.amazonaws.com:5432/d9kk3aqpv4nur1":
	raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://bezoopliubauew:ff447efa87a96336c27fa8c83def232d790d8b48f8da38e236259b4f447926f7@ec2-46-137-84-140.eu-west-1.compute.amazonaws.com:5432/d9kk3aqpv4nur1")
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/register", methods=["POST", "GET"])
def register():
	if request.method == "POST":
		return render_template("error.html", mesasge = "Try registering!!")
	else:
		return render_template("register.html")

@app.route("/register_user", methods=["POST", "GET"])
def register_user():
	if request.method == "GET":
		return render_template("error.html", mesasge = "Try registering!!")
	
	user_name = request.form.get("user_name")
	user_pass = request.form.get("user_pass")
	user_pass_re = request.form.get("user_pass_re")

	if user_pass != user_pass_re:
		return render_template("error.html", mesasge="Password doesn't match!!")
	
	if db.execute("SELECT (username, password) FROM user_details WHERE (username = :username AND password = :password)", {"username": user_name, "password": user_pass}).rowcount == 1:
		return render_template("error.html", message="Already a user! Try login.");

	db.execute("INSERT INTO user_details (username, password) VALUES (:username, :password)", {"username": user_name, "password": user_pass})
	db.commit()

	books = db.execute("SELECT * FROM books FETCH FIRST 15 ROW ONLY")
	return render_template("homepage.html", books=books);

"""Login to the page with username and password"""
@app.route("/login")
def login():
	return render_template("index.html")	

"""If user exists create a local session for the user"""
@app.route("/session", methods=["POST", "GET"])
def session():
	if request.method == "GET":
		return render_template("error.html", message="Try Login!!")

	user_name = str(request.form.get("user_name"))
	user_pass = str(request.form.get("user_pass"))
	
	if db.execute("SELECT * FROM user_details WHERE (username = :username AND password = :password)", {"username": user_name, "password": user_pass}).rowcount == 0:
		return render_template("error.html", message="Invalid username or password! It takes only 15s to register! Try registering.");

	"""Create a session for the user"""
	books = db.execute("SELECT * FROM books FETCH FIRST 15 ROW ONLY")
	return render_template("homepage.html", books=books)

@app.route("/homepage")
def homepage():
	books = db.execute("SELECT * FROM books FETCH FIRST 15 ROW ONLY")
	return render_template("homepage.html", books = books)

@app.route("/search", methods=["POST", "GET"])
def search(): 	
	# Get form information.
	try :
		book_details = str(request.form.get("book_details"))
	except ValueError:
		return render_template("error.html", message="No book matches given details number!")

	#Check for existence of book with provided title
	if db.execute("SELECT * FROM books WHERE title = :title", {"title": book_details}).rowcount == 1:
		book = db.execute("SELECT * FROM books WHERE title = :title", {"title": book_details}).fetchone()
		return render_template("book.html", book=book)

	#Check for existence of book with provided author name
	if db.execute("SELECT * FROM books WHERE author = :author", {"author": book_details}).rowcount == 1:
		book = db.execute("SELECT * FROM books WHERE author = :author", {"author": book_details}).fetchone()
		return render_template("book.html", book=book)

	#Check for existence of book with provided isbn number: 3
	if db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_details}).rowcount == 1:
		book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_details}).fetchone()
		return render_template("book.html", book=book)

	return render_template("error.html", message="Try entering correct details!")
	#Corresponding error messages
""" if error_type == 1:
		return render_template("error.html", message="Try entering correct details!")
	
	elif error_type == 1:
		return render_template("error.html", message="No book with entered title!")

	elif error_type == 2:
		return render_template("error.html", message="Author has no books in his name!")

	else:
		return render_template("error.html", message="Invalid ISBN number!")	
"""
@app.route("/book/<string:details>")
def book(details):
	if details is None:
		return render_template("error.html", message="URL not found!!")
	book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()

	if book is None:
		return render_template("error.html", message = "No book with entered title / Invalid ISBN")
	
	return render_template("book.html", book=book)

"""Print details of all the books in database"""
@app.route("/books/<string:details>")
def books(details):
	books = db.execute("SELECT * FROM books WHERE isbn OR title OR author LIKE '%a%'").fetchall()
	return render_template("books.html", books=books)

@app.route("/api/<string:title>", methods=["POST", "GET"])
def book_api(title):
	res = requests.get("https://www.goodreads.com/book/title.json", 
							params={"format": json, "key": "P2LGOZuBDHH7LSzJZhnsA", "title": "Blink"})
	if res.status_code != 200:
		raise Exception("Error: API request failed!")
	details = res.json()

if __name__ == '__main__':
	main()
