import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://bezoopliubauew:ff447efa87a96336c27fa8c83def232d790d8b48f8da38e236259b4f447926f7@ec2-46-137-84-140.eu-west-1.compute.amazonaws.com:5432/d9kk3aqpv4nur1")

db = scoped_session(sessionmaker(bind=engine))    

def main():
	f = open("books.csv")
	reader = csv.reader(f)
	for isbn, title, author, year in reader:
		db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", 
					{"isbn": isbn, "title": title, "author": author, "year": year})
		db.commit()

if __name__ == "__main__":
	main()

""" Check for year not greater than present"""