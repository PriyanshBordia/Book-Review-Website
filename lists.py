import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://bezoopliubauew:ff447efa87a96336c27fa8c83def232d790d8b48f8da38e236259b4f447926f7@ec2-46-137-84-140.eu-west-1.compute.amazonaws.com:5432/d9kk3aqpv4nur1")

db = scoped_session(sessionmaker(bind=engine))    

def main():
	book = db.execute("SELECT * FROM books").fetchone()
	print(f"Title : '{book.title}'")
	print(f"Autror: {book.author}")
	print(f"ISBN  : {book.isbn}")
	print(f"Year  : {book.year}")

if __name__ == "__main__":
	main()