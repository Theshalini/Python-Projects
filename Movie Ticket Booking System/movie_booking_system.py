import mysql.connector
from mysql.connector import Error
import csv
import re
import os

def create_connection():
    """ Create a database connection """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='movie_bookings_db',
            user='root',
            password='12345'
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

def check_movies_exist(connection):
    """ Check if movies exist in the database """
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM movies")
        count = cursor.fetchone()[0]
        return count > 0
    except Error as e:
        print(f"Error checking movies: '{e}'")
        return False

def load_movies_from_csv(connection, csv_file):
    """ Load movies from a CSV file and insert into the database if not already loaded """
    try:
        if check_movies_exist(connection):
            print("Movies already exist in the database. Skipping CSV load.")
            return
        
        cursor = connection.cursor()
        current_directory = os.getcwd()
        print(f"Current working directory: {current_directory}")

        if not os.path.exists(csv_file):
            print(f"CSV file '{csv_file}' not found.")
            return
        
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) != 5:
                    print(f"Skipping invalid row: {row}")
                    continue
                title, genre, duration, rating, price = row
                if not re.match(r"^[A-Za-z0-9\s:]+$", title):
                    print(f"Invalid title: {title}")
                    continue
                if not re.match(r"^[A-Za-z\s]+$", genre):
                    print(f"Invalid genre: {genre}")
                    continue
                if not re.match(r"^\d+$", duration):
                    print(f"Invalid duration: {duration}")
                    continue
                if not re.match(r"^\d+(\.\d+)?$", rating):
                    print(f"Invalid rating: {rating}")
                    continue
                if not re.match(r"^\d+(\.\d+)?$", price):
                    print(f"Invalid price: {price}")
                    continue
                query = "INSERT INTO movies (title, genre, duration, rating, price) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (title, genre, int(duration), float(rating), float(price)))
        connection.commit()
        print("Movies loaded from CSV file successfully.")
    except Error as e:
        print(f"Error: '{e}'")
        connection.rollback()
    except Exception as e:
        print(f"Unexpected error: '{e}'")

def view_movies(connection):
    """ View all movies """
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM movies"
        cursor.execute(query)
        results = cursor.fetchall()
        print("Movies:")
        for row in results:
            print(f"ID: {row[0]}, Title: {row[1]}, Genre: {row[2]}, Duration: {row[3]} mins, Rating: {row[4]}, Price: ${row[5]:.2f}")
    except Error as e:
        print(f"Error: '{e}'")

def book_ticket(connection, movie_id, customer_name, seats):
    """ Book tickets for a movie and generate bill """
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT title, price FROM movies WHERE id = %s", (movie_id,))
        movie = cursor.fetchone()
        if not movie:
            print("Movie ID not found.")
            return

        title, price = movie
        total_cost = price * seats

        query = "INSERT INTO bookings (movie_id, customer_name, seats) VALUES (%s, %s, %s)"
        cursor.execute(query, (movie_id, customer_name, seats))
        connection.commit()

        # Write bill to a text file
        with open("bill.txt", "w") as bill_file:
            bill_file.write("***** Movie Ticket Booking System *****\n")
            bill_file.write(f"Customer Name: {customer_name}\n")
            bill_file.write(f"Movie: {title}\n")
            bill_file.write(f"Seats: {seats}\n")
            bill_file.write(f"Price per Ticket: ${price:.2f}\n")
            bill_file.write(f"Total Cost: Rs.{total_cost:.2f}\n")
            bill_file.write("***************************************\n")

        print(f"Tickets booked successfully for movie ID {movie_id}. Bill has been generated.")
    except Error as e:
        print(f"Error: '{e}'")
        connection.rollback()

def view_bookings(connection):
    """ View all bookings """
    try:
        cursor = connection.cursor()
        query = """
        SELECT b.id, m.title, b.customer_name, b.seats, b.booking_time
        FROM bookings b
        JOIN movies m ON b.movie_id = m.id
        """
        cursor.execute(query)
        results = cursor.fetchall()
        print("Bookings:")
        for row in results:
            print(f"Booking ID: {row[0]}, Movie: {row[1]}, Customer: {row[2]}, Seats: {row[3]}, Time: {row[4]}")
    except Error as e:
        print(f"Error: '{e}'")

def main():
    connection = create_connection()
    if connection is not None:
        # Load movies from CSV file only if the database is empty
        load_movies_from_csv(connection, 'movies.csv')

        while True:
            print("\n1. View Movies\n2. Book Ticket\n3. View Bookings\n4. Exit")
            choice = input("Enter your choice: ")
            if choice == '1':
                view_movies(connection)
            elif choice == '2':
                view_movies(connection)
                movie_id = int(input("Enter the movie ID to book: "))
                customer_name = input("Enter your name: ")
                seats = int(input("Enter number of seats: "))
                book_ticket(connection, movie_id, customer_name, seats)
            elif choice == '3':
                view_bookings(connection)
            elif choice == '4':
                break
            else:
                print("Invalid choice, please try again.")
        connection.close()

if __name__ == "__main__":
    main()
