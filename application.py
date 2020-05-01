import os
import requests
# import connect_database  #

from flask import Flask, render_template, session, request, url_for, redirect, jsonify, flash, json
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from cerberus import Validator
# from util import sql, get_password, search_in_books, write_review, get_reviews

# db = connect_database.get_db()

app = Flask(__name__)

app.config["SECRET_KEY"] = 'dont ask about the key'

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

uniq_id = -1

@app.route("/")
def index():
	return redirect("login")


"""Bookmarked Books"""
@app.route("/marked/<int:user_id>")
def marked():
	book_isbn = db.execute("SELECT * books WHERE user_id = id ")
	books = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchall()
	return render_template("marked.html", nav1="Search", link1="search", nav2="Logout", link2="login", books=books)


@app.route("/register", methods=["POST", "GET"])
def register():
	if request.method == "POST":
		return render_template("error.html", mesasge = "Try registering!!")			#
	else:
		return render_template("register.html", nav1="Login", link1="index", nav2="Register", link2="register")


@app.route('/register_error/<string:error>')
def register_error(error):
	if error_type == 'email':
		error_message = "Please enter a valid email!"
	
	elif error_type == 'pass':
		error_message = "Passwords do not match!"

	elif error_type == 'already exists':
		error_message = "Sorry. The email already exists in our records. Please register with another email."

	return render_template("register_error.html", message=error_message)	


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

	return render_template("success.html", message="Successfully Registered Now you can login")


"""Login to the page with username and password"""
@app.route("/login")
def login():
	return render_template("index.html", nav1="Login", link1="index", nav2="Register", link2="register")	


"""If user exists create a local session for the user"""
@app.route("/login_session", methods=["POST", "GET"])
def login_session():
	if request.method == "GET":
		return render_template("error.html", message="Try Login!!")

	user_name = str(request.form.get("user_name"))
	user_pass = str(request.form.get("user_pass"))
	
	if db.execute("SELECT * FROM user_details WHERE (username = :username AND password = :password)", {"username": user_name, "password": user_pass}).rowcount == 0:
		return render_template("error.html", message="Invalid username or password! It takes only 15s to register! Try registering.");

	else:
		unique_id = db.execute("SELECT id FROM user_details WHERE (username = :username AND password = :password)", {"username": user_name, "password": user_pass})
		
		global uniq_id 
		uniq_id = unique_id.first()[0]
	
		name = user_name.split("@")
		name = name[0]
		return render_template("search.html" , name=name, nav1="Marked", link1="index", nav2="Logout", link2="index", books=books)


@app.route("/search_book")
def search_book():
	return render_template("search.html", nav1="Marked", link1="index", nav2="Logout", link2="index", books=books)


# Search books that match the string entered
@app.route("/search", methods=["POST", "GET"])
def search(): 	
	# Get form information.
	
	try :
		book_details = str(request.form.get("book_details"))
	except ValueError:
		return render_template("error.html", message="No book matches given details number!")

	books = []
	#Check for existence of book with provided title
	# if db.execute("SELECT * FROM books WHERE title = :title", {"title": book_details}).rowcount >= 1:
	title_book_isbn = db.execute("SELECT isbn FROM books WHERE title LIKE :title", {"title": '%' + str(book_details) + '%'}).fetchall()
	if title_book_isbn != None:
		for book in title_book_isbn:
			books.append(book.isbn)
		# return render_template("book.html", book=book)

	#Check for existence of book with provided author name
	# if db.execute("SELECT * FROM books WHERE author = :author", {"author": book_details}).rowcount >= 1:
	author_book_isbn = db.execute("SELECT isbn FROM books WHERE author LIKE :author", {"author": '%' + str(book_details) + '%'}).fetchall()
	if author_book_isbn != None:
		for book in author_book_isbn:
			books.append(book.isbn) 
		#return render_template("book.html", book=book)

	#Check for existence of book with provided isbn number: 3
	# if db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_details}).rowcount >= 1:
	isbn_book_isbn = db.execute("SELECT isbn FROM books WHERE isbn LIKE :isbn", {"isbn": '%' + str(book_details) + '%'}).fetchall()
	if isbn_book_isbn != None:
		for book in isbn_book_isbn:
			books.append(book.isbn)
		# return render_template("book.html", books=book)
	
	if not books:
		return render_template("error.html", message="Try entering correct details!")
	
	else:
		for i in range(0,len(books)):
			books[i] = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": books[i]}).fetchone()

		books.sort(reverse = True)
		return render_template("books.html", nav1="Marked", link1="index", nav2="Logout", link2="login", books=books)


"""Print details of all the books in database"""
@app.route("/books/<string:details>")
def books(details):
	books = db.execute("SELECT * FROM books WHERE isbn OR title OR author LIKE '%a%'").fetchall()
	return render_template("books.html", books=books)


# Details about about with provided isbn
@app.route("/book/<string:details>")
def book(details):
	if details is None:
		return render_template("error.html", message="URL not found!!")
	
	book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": details}).fetchone()

	if book is None:
		return render_template("error.html", message = "No book with entered title / Invalid ISBN")
	
	return render_template("book.html" , qid=uniq_id, nav1="Search", link1="search_book", nav2="Logout", link2="login", book=book)


@app.route("/user_review/<string:book_isbn>", methods=["GET", "POST"])
def user_review(book_isbn):

	global uniq_id

	book_review = str(request.form.get("book_review"))
	book_rating = str(request.form.get("book_rating"))

	if uniq_id == -1:
		render_template("error.html", message="Login to write a review!!")

	if request.method == "GET":
		render_template("error.html", message="Please Write a review and then submit!")

	if db.execute("SELECT * FROM reviews WHERE (isbn = :book_isbn AND user_id = :uniq_id)", {"book_isbn": book_isbn, "uniq_id": uniq_id}).rowcount != 0:
		render_template("error.html", message="Sorry, You can review a book only once!")

	db.execute("INSERT INTO reviews (user_id, isbn, review, rating) VALUES (:id, :isbn, :review, :rating)" ,{"id": uniq_id, "isbn": book_isbn, "review": book_review, "rating": book_rating})
	db.commit()

	book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()

	return render_template("book.html", qid=uniq_id, nav1="Search", link1="search", nav2="Logout", link2="index", book=book, book_rating=book_rating, book_review=book_review)

# @app.route("/display_review")
# def display_review():
	
"""Avg Ratings and rating distribution, total count"""
@app.route("/api/<string:title>", methods=["POST", "GET"])
def book_api(title):
	res = requests.get("https://www.goodreads.com/book/title.json", 
						params={"format": json, "key": "P2LGOZuBDHH7LSzJZhnsA", "title": "Blink"})
	if res.status_code != 200:
		raise Exception("Error: API request failed!")
	details = res.json()


@app.route("/logout")
def logout():
	global uniq_id
	uniq_id = -1
	redirect("login")


@app.route("/homepage")
def homepage():
	books = db.execute("SELECT * FROM books FETCH FIRST 15 ROW ONLY")
	return render_template("homepage.html", nav1="Marked", link1="index", nav2="Logout", link2="login", books = books)

if __name__ == '__main__':
	app.run(debug=True)