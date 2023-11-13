# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 15:58:54 2023

@author: 91983
"""

from flask import Flask, request, jsonify,render_template
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, ForeignKey, text,select
from sqlalchemy.orm import sessionmaker
from faker import Faker
from datetime import date

app = Flask(__name__)

# Path to the SQLite file
db_file_path = 'library.db'

# Create an SQLite database engine for the library database
engine = create_engine('sqlite:///' + db_file_path, echo=True)


# Function to insert 20 rows into the 'user' table
def insert_random_users(session, num_rows=20):
    fake = Faker()
    for i in range(num_rows):
        username = fake.user_name()
        email = fake.email()
        address = fake.address()

        insert_query = text("INSERT INTO user (username, email, address) VALUES (:username, :email, :address)")
        session.execute(insert_query, {"username": username, "email": email, "address": address})
    session.commit()

# Function to insert random authors into the 'author' table
def insert_random_authors(session, num_rows=20):
    fake = Faker()
    for i in range(num_rows):
        authorname = fake.name()
        biography = fake.text()

        insert_query = text("INSERT INTO author(authorname, biography) VALUES (:authorname, :biography)")
        session.execute(insert_query, {"authorname": authorname, "biography": biography})
    session.commit()

# Function to insert random books into the 'book' table
def insert_random_books(session, num_rows=20):
    fake = Faker()
    for i in range(num_rows):
        author_id = fake.random_int(min=1, max=20)  # Assuming authorids are from 1 to 20
        title = fake.text(max_nb_chars=50)  # Adjust as needed
        author_name = fake.name()
        genre = fake.word()
        publication_date = fake.date_of_birth(minimum_age=18, maximum_age=65)  # Adjust as needed

        insert_query = text("""
            INSERT INTO book (authorid, title, author, genre, publicationdate)
            VALUES (:author_id, :title, :author_name, :genre, :publication_date)
        """)

        session.execute(insert_query, {
            "author_id": author_id,
            "title": title,
            "author_name": author_name,
            "genre": genre,
            "publication_date": publication_date
        })

    session.commit()

# Function to insert random borrow records into the 'borrow' table
def insert_random_borrows(session, num_rows=20):
    fake = Faker()
    for i in range(num_rows):
        user_id = fake.random_int(min=1, max=20)  # Assuming userids are from 1 to 20
        book_id = fake.random_int(min=1, max=20)  # Assuming bookids are from 1 to 20
        checkout_date = fake.date_this_decade()
        return_date = fake.date_between(start_date=checkout_date, end_date='today')

        insert_query = text("""
            INSERT INTO borrow (userid, bookid, checkoutdate, returndate)
            VALUES (:user_id, :book_id, :checkout_date, :return_date)
        """)

        session.execute(insert_query, {
            "user_id": user_id,
            "book_id": book_id,
            "checkout_date": checkout_date,
            "return_date": return_date
        })

    session.commit()

# Function to execute a SQL query and return the result
def execute_query(query):
    try:
        result = engine.execute(text(query))
        return result.fetchall()
    except Exception as e:
        return str(e)


# Function to create tables and return a message
def create_tables(engine):
    try:
        # Remove the SQLite file if it exists
        if os.path.exists(db_file_path):
            os.remove(db_file_path)

        # Create a connection to the database
        my_conn = engine.connect()

        # Create a metadata object
        meta = MetaData()

        # Creating the 'user' table
        user = Table('user', meta,
                     Column('userid', Integer, primary_key=True),
                     Column('username', String, nullable=False),
                     Column('email', String, nullable=False),
                     Column('address', String, nullable=False)
                     )

        # Creating the 'author' table
        author = Table('author', meta,
                       Column('authorid', Integer, primary_key=True),
                       Column('authorname', String, nullable=False),
                       Column('biography', String, nullable=False)
                       )

        # Creating the 'book' table
        book = Table('book', meta,
                     Column('bookid', Integer, primary_key=True),
                     Column('authorid', ForeignKey('author.authorid')),
                     Column('title', String, nullable=False),
                     Column('author', String, nullable=False),
                     Column('genre', String, nullable=False),
                     Column('publicationdate', Date, nullable=False)
                     )

        # Creating the 'borrow' table
        borrow = Table('borrow', meta,
                       Column('borrowid', Integer, primary_key=True),
                       Column('userid', ForeignKey('user.userid')),
                       Column('bookid', ForeignKey('book.bookid')),
                       Column('checkoutdate', Date, nullable=False),
                       Column('returndate', Date, nullable=False)
                       )

        # Create the tables in the database
        meta.create_all(engine)
        
        # Create a new session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Insert 20 random rows into the 'user' table
        insert_random_users(session)

        # Insert 20 random rows into the 'author' table
        insert_random_authors(session)

        # Insert 20 random rows into the 'book' table
        insert_random_books(session)

        # Insert 20 random rows into the 'borrow' table
        insert_random_borrows(session)

        # Close the session
        session.close()
        
        return "Tables created successfully."
    except Exception as e:
        return str(e)

# Call the function to create tables when the application starts
#create_tables(engine)

# Flask route to render the HTML page
@app.route('/')
def index():
    return render_template('index.html')



# Flask route to handle queries from the front end
@app.route('/execute_query', methods=['POST'])
def execute_query_from_frontend():
    try:
        # Get the query from the front end
        data = request.get_json()
        query = data['query']

        # Execute the query
        result = execute_query(query)

        # Convert the result to a list of dictionaries
        result_list = [dict(row) for row in result]

        # Return the result as JSON
        return jsonify({'result': result_list})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)





