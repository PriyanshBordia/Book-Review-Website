import requests

import hashlib
from flask import Flask, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DB_URL"):
	raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("DB_URL")
db = scoped_session(sessionmaker(bind=engine))

uniq_id = -2
qname = "anonymous_user"

@app.route("/")
def index():
	global uniq_id
	
	if uniq_id == -2 or uniq_id == -1:
		return redirect("login")
	else:
		return redirect("search_book")


"""Bookmarked Books"""
@app.route("/marked")
def marked():
	global uniq_id

	if uniq_id == -2:
		return render_template("error.html", message="Please Register to See bookmarked!", prev_link="register")

	if uniq_id == -1:
		return render_template("error.html", message="Please LogIn to See bookmarked!", prev_link="login")

	books = db.execute("SELECT * FROM marked WHERE mark_id = :id", {"id": uniq_id}).fetchall()

	if books is None:
		return render_template("success.html", message="None Books Marked", prev_link="search_book")

	return render_template("marked.html", nav1="Search", link1="search_book", nav2="Logout", link2="logout", books=books)



@app.route("/register", methods=["POST", "GET"])
def register():
	if request.method == "POST":
		return render_template("error.html", message = "Try registering!!", prev_link="login")		
	else:
		return render_template("register.html", nav1="Login", link1="login", nav2="Register", link2="register")


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
		return render_template("error.html", message = "Try registering!!", prev_link="register")
	
	user_name = request.form.get("user_name")
	user_pass = request.form.get("user_pass")
	user_pass_re = request.form.get("user_pass_re")

	if user_pass != user_pass_re:
		return render_template("error.html", message="Password doesn't match!!", prev_link="register")

	if len(user_pass) == 0:
		return render_template("error.html", message="Password field can 't be empty!", prev_link="register")


	if db.execute("SELECT (username, password) FROM user_details WHERE (username = :username AND password = :password)", {"username": user_name, "password": user_pass}).rowcount == 1:
		return render_template("error.html", message="Already a user! Try login.", prev_link="login");

	global uniq_id 
	uniq_id = -1
	
	db.execute("INSERT INTO user_details (username, password) VALUES (:username, :password)", {"username": user_name, "password": user_pass})
	db.commit()

	return render_template("success.html", message="Successfully Registered Now you can login", prev_link="login")


"""Login to the page with username and password"""
@app.route("/login")
def login():
	return render_template("login.html", nav1="Login", link1="login", nav2="Register", link2="register")	


"""If user exists create a local session for the user"""
@app.route("/login_session", methods=["POST", "GET"])
def login_session():
	global uniq_id

	if request.method == "GET":
		return render_template("error.html", message="Try Login!!", prev_link="login")

	user_name = str(request.form.get("user_name"))
	user_pass = str(request.form.get("user_pass"))
	
	if db.execute("SELECT * FROM user_details WHERE (username = :username AND password = :password)", {"username": user_name, "password": user_pass}).rowcount == 0:
		return render_template("error.html", message="Invalid username or password! It takes only 15s to register! Try registering.", prev_link="login")

	else:
		unique_id = db.execute("SELECT id FROM user_details WHERE (username = :username AND password = :password)", {"username": user_name, "password": user_pass})

		uniq_id = int(unique_id.first()[0])
		
	# Extracting username from email as string before '@''
		name = user_name.split("@")
		
		global qname
		qname = name[0]
		
		return render_template("search.html" , name=qname, nav1="Marked", link1="marked", nav2="Logout", link2="logout")


@app.route("/search_book")
def search_book():
	global qname
	return render_template("search.html", name=qname, nav1="Marked", link1="marked", nav2="Logout", link2="logout")


# Search books that match the string entered
@app.route("/search", methods=["POST", "GET"])
def search(): 	
	# Get form information.
	try :
		book_details = str(request.form.get("book_details"))
	except ValueError:
		return render_template("error.html", message="No book matches given details number!", prev_link="search_book")

	books = []

	title_book_isbn = db.execute("SELECT isbn FROM books WHERE title LIKE :title", {"title": '%' + str(book_details) + '%'}).fetchall()
	if title_book_isbn != None:
		for book in title_book_isbn:
			books.append(book.isbn)

	author_book_isbn = db.execute("SELECT isbn FROM books WHERE author LIKE :author", {"author": '%' + str(book_details) + '%'}).fetchall()
	if author_book_isbn != None:
		for book in author_book_isbn:
			books.append(book.isbn) 

	isbn_book_isbn = db.execute("SELECT isbn FROM books WHERE isbn LIKE :isbn", {"isbn": '%' + str(book_details) + '%'}).fetchall()
	if isbn_book_isbn != None:
		for book in isbn_book_isbn:
			books.append(book.isbn)
	
	if len(books) == 0:
		return render_template("error.html", message="No book matches given details number!", prev_link="search_book")
	
	else:
		for i in range(0,len(books)):
			books[i] = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": books[i]}).fetchone()

		books.sort(reverse = True)
		return render_template("books.html", nav1="Marked", link1="marked", nav2="Logout", link2="logout", books=books)


# Details about about with provided isbn
@app.route("/book/<string:details>")
def book(details):
	global uniq_id
	global qname

	if details is None:
		return render_template("error.html", message="URL not found!!", prev_link="search_book")
	
	book = book_api(details)

	if db.execute("SELECT * FROM reviews WHERE (user_id = :uniq_id AND isbn = :ISBN)", { "uniq_id": uniq_id, "ISBN": details}).rowcount == 1:	
		unique = db.execute("SELECT review FROM reviews WHERE (user_id = :uniq_id AND isbn = :ISBN)", { "uniq_id": uniq_id, "ISBN": details})	
		book_review = str(unique.first()[0])
		
		unique = db.execute("SELECT rating FROM reviews WHERE (user_id = :uniq_id AND isbn = :ISBN)", { "uniq_id": uniq_id, "ISBN": details})	
		book_rating = int(unique.first()[0])

		return render_template("book_review.html" , name=qname, nav1="Search", link1="search_book", nav2="Logout", link2="logout", book=book, book_rating=book_rating, book_review=book_review)
	
	else:
		return render_template("book.html" , nav1="Search", link1="search_book", nav2="Logout", link2="logout", book=book)

#user reviews and 
@app.route("/user_review/<string:book_isbn>", methods=["GET", "POST"])
def user_review(book_isbn):	
	global uniq_id
	global qname

	if request.method == "GET":
		render_template("error.html", message="Please Write a review and then submit!", prev_link="#")

	book_review = str(request.form.get("book_review"))
	book_rating = str(request.form.get("book_rating"))

	if uniq_id == -1 :
		return render_template("error.html", message="Login to write a review!!", prev_link="login")

	if db.execute("SELECT * FROM reviews WHERE (user_id = :uniq_id AND isbn = :ISBN)", { "uniq_id": uniq_id, "ISBN": book_isbn}).rowcount == 0:
		db.execute("INSERT INTO reviews (user_id, isbn, review, rating) VALUES (:id, :isbn, :review, :rating)" ,{"id": uniq_id, "isbn": book_isbn, "review": book_review, "rating": book_rating})
		db.commit()	
		
		book = book_api(book_isbn)
		return render_template("book_review.html", name=qname, nav1="Search", link1="search_book", nav2="Logout", link2="logout", book=book, book_rating=book_rating, book_review=book_review)
	
	else:
		return render_template("error.html", message="Sorry, You can review a book only once!", prev_link="search_book")
		

"""Avg Ratings and rating distribution, total count"""
@app.route("/api/<string:ISBN>", methods=["POST", "GET"])
def book_api(ISBN):

	book_details = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": ISBN}).fetchone()

	if book_details is None:
		return render_template("error.html", message = "No book with entered title / Invalid ISBN", prev_link="search_book")
	
	res = requests.get("https://www.goodreads.com/book/review_counts.json",
					   params={"key": "ko689CsTUQ8ecggW4ootw", "isbns": ISBN})
	
	if res.status_code != 200:
		raise Exception("Error: API request failed!")
	
	response = res.json()

	count = response['books'][0]['reviews_count']
	avg = response['books'][0]['average_rating']

	book = {}

	book[0] = book_details.isbn
	book[1] = book_details.title
	book[2] = book_details.author
	book[3] = book_details.year
	book[4] = count
	book[5] = avg

	return book


@app.route("/logout")
def logout():
	global uniq_id
	
	if uniq_id == -2:
		return render_template("error.html", message="Sorry, You haven't Registered!!", prev_link="register")

	elif uniq_id == -1:
		return render_template("error.html", message="Sorry, You haven't logedIn!!", prev_link="login")
	
	else:	
		uniq_id = -1
		return render_template("login.html", nav1="Login", link1="login", nav2="Register", link2="register")	


@app.route("/homepage")
def homepage():
	books = db.execute("SELECT * FROM books FETCH FIRST 15 ROW ONLY")
	return render_template("homepage.html", nav1="Marked", link1="marked", nav2="Logout", link2="logout", books=books)


if __name__ == '__main__':
    app.debug = True
    app.run()

