import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(
	"postgres://etrfsjyhdmwult:9b5b9d599e303c30bd329266871f2653016154c8f2cba5c6439022abbe341077@ec2-52-7-168-69.compute-1.amazonaws.com:5432/d4j6denllckr8l")

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
