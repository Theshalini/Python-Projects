import mysql.connector
from mysql.connector import Error
import datetime
import smtplib

def create_connection():
    """ Create a database connection """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='election_db',
            user='root',
            password='12345'
        )
        if connection.is_connected():
            print("Connected to MySQL database successfully...")
        return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

def fetch_candidates(connection):
    """ Fetch and display all candidates """
    try:
        cursor = connection.cursor()
        query = "SELECT id, name FROM candidates"
        cursor.execute(query)
        results = cursor.fetchall()
        print("\nCandidates:")
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}")
        return [row[0] for row in results]
    except Error as e:
        print(f"Error: '{e}'")
        return []

def cast_vote(connection, candidate_id, name_voter, aadhar_no, voter_id):
    """ Cast a vote for a candidate """
    try:
        cursor = connection.cursor()
        query = "UPDATE candidates SET votes = votes + 1 WHERE id = %s"
        cursor.execute(query, (candidate_id,))
        connection.commit()
        print(f"Voted for candidate ID {candidate_id}")
        print("Thanks for voting!")
        f= open("voters.txt","a")
        current_time = datetime.datetime.now()
        f.write(f"Date & Time: {current_time}\n")
        f.write(f"Name: {name_voter}\n")
        f.write(f"Aadhar No: {aadhar_no}\n")
        f.write(f"Voter Id: {voter_id}\n")
        f.write(f"{name_voter} has voted successfully.\n\n")
        email_sending(name_voter, int(aadhar_no),voter_id)
    except Error as e:
        print(f"Error: '{e}'")
        connection.rollback()

def show_results(connection):
    """ Show the current election results """
    try:
        cursor = connection.cursor()
        query = "SELECT name, votes FROM candidates"
        cursor.execute(query)
        results = cursor.fetchall()
        print("Current election results:")
        for row in results:
            print(f"Candidate: {row[0]}, Votes: {row[1]}")
    except Error as e:
        print(f"Error: '{e}'")

def email_sending(name_voter, aadhar_no, voter_id):
    try:
        receiver_mail = input("Enter your email_id: ")
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("admin@gmail.com", "admin_encrypted_password")
        
        current_time = datetime.datetime.now()
        message = f"""\
        Subject: Regarding your vote
        
        Date & Time: {current_time}
        Name: {name_voter}
        Aadhar No: {aadhar_no}
        Voter Id: {voter_id}
        
        Thanks for voting! You have done your job as a responsible citizen!
        """
        
        s.sendmail("admin@gmail.com", receiver_mail, message)
        s.quit()
        print("Email is sent successfully")
    except Exception as e:
        print(f"Mail not sent due to: {e}")

def main():
    connection = create_connection()
    if connection is not None:
        print("\n***WELCOME TO ELECTION SYSTEM***\n")
        name_voter = input("Enter your name: ")
        aadhar_no = input("Enter your Aadhar No:")
        while True:
            print("\n1. Cast Vote\n2. Show Results\n3. Exit")
            choice = input("Enter your choice: ")
            if choice == '1':
                voter_id= input("Enter your Voter's Id:")
                candidate_ids = fetch_candidates(connection)
                if candidate_ids:
                    candidate_id = input("Enter the candidate's ID to vote: ")
                    if candidate_id.isdigit() and int(candidate_id) in candidate_ids:
                        cast_vote(connection, int(candidate_id),name_voter, aadhar_no,voter_id)
                    else:
                        print("Invalid candidate ID. Please try again.")
                else:
                    print("No candidates found.")
            elif choice == '2':
                show_results(connection)
            elif choice == '3':
                break
            else:
                print("Invalid choice, please try again.")
        connection.close()

if __name__ == "__main__":
    main()
