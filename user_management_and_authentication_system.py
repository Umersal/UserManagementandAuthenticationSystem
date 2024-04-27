#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#imports
from flask import Flask, request, jsonify
from datetime import datetime
from argon2 import PasswordHasher
import mysql.connector
import configparser

app = Flask(__name__)

parser = configparser.ConfigParser()
parser.read('config.ini')
host = parser.get('MYSQL', 'host')
port = parser.get('MYSQL', 'port')
user = parser.get('MYSQL', 'user')
password = parser.get('MYSQL', 'password')
database_name = parser.get('MYSQL', 'database_name')

class User:
    
    def __init__(self,name,email,password):
        self.name = name
        self.email = email
        if password is not None:
            self.hashedPassword = self.generate_hash_password(password)
        else:
            self.hashedPassword = None #password can also be None in those cases where we fetch the user details
        self.last_login = None
        
    def generate_hash_password(self,password):
        """
        Function that generates hashes for the password
        """
        
        ph = PasswordHasher()
        hash = ph.hash(password)
        return hash
    
    def rehash(self,hash,password):
        """
        Function rehash the password for verification
        """
        
        ph = PasswordHasher()
        try:
            return ph.verify(hash, password)
        except:
            return False
        
        
    def database_initializing(self):
        """
        Function to initialize the database
        """
        
        mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port = port,
            database = database_name  
        )
        return mydb
    
    def insertUsers(self):
        """
        Function to insert the user details into the database
        """
        
        db = self.database_initializing()
        cursor = db.cursor()
        insert_user_query = "INSERT INTO users (name,email,password_hash,last_login) VALUES (%s,%s,%s,%s)"
        value = (self.name,self.email,self.hashedPassword,self.last_login)
        try:
            cursor.execute(insert_user_query, value)
            db.commit()
            db.close()
            return True
        except mysql.connector.Error as err:
            if err.errno == 1062:  # MySQL error number for duplicate entry
                error_message = "Email address already exists in our database"
            else:
                error_message = "An error occurred while inserting the user"
            print("Error:", err)
            db.close()
            return False, error_message
        
    def updateUsers(self,user_id):
        """
        Function to update the user details in the database
        """
        
        db = self.database_initializing()
        cursor = db.cursor()
        update_fields = []
        update_values = []

        if self.name is not None:
            update_fields.append("name=%s")
            update_values.append(self.name)
        if self.email is not None:
            update_fields.append("email=%s")
            update_values.append(self.email)
        if self.hashedPassword is not None:
            update_fields.append("password_hash=%s")
            update_values.append(self.hashedPassword)

        if not update_fields:
            return False
        #if there are multiple fields that needs to be updated then I am using list for getting those fields and values
        update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id={user_id}"
        print(update_query)
        print(update_values)
        try:
            cursor.execute(update_query, update_values)
            db.commit()
            db.close()
            return True
        except mysql.connector.Error as err:
            print("Error:", err)
            db.rollback()
            db.close()
            return False, err
        
    def deleteUser(self,user_id):
        """
        Function to delete the user from the database
        """
        
        db = self.database_initializing()
        cursor = db.cursor()
        delete_query = f"DELETE FROM users WHERE id={user_id}"
        try:
            cursor.execute(delete_query)
            db.commit()
            db.close()
            return True
        except mysql.connector.Error as err:
            print("Error:", err)
            db.close()
            return False, err
        
    def listUsers(self):
        """
        function to retrieve the list of users from the database
        """
        
        db = self.database_initializing()
        cursor = db.cursor()

        try:
            cursor.execute("SELECT id, name, email, last_login FROM users")
            users = cursor.fetchall()
            db.close()
            user_list = []
            for user in users:
                user_dict = {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "last_login": str(user[3]) if user[3] else None
                }
                user_list.append(user_dict)

            return user_list
        except mysql.connector.Error as err:
            print("Error:", err)
            db.close()
            return False
        
    def login(self,password):
        """
        Function to verify and validate the login credentials from the user
        """
        
        db = self.database_initializing()
        cursor = db.cursor()
        try:
            cursor.execute("SELECT id, email, password_hash FROM users WHERE email = %s", (self.email,))
            user = cursor.fetchone()
            print(user)
            if user is None:
                return "Email doesnot exist!",False
            #match the email
            if self.email == user[1]:
                #check if the password matches in the database
                verify = self.rehash(user[2],password)
                
                if verify:
                    """
                    once the password is verified, store the login time of the user
                    """
                    formatted_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    update_query = f"UPDATE users SET last_login = '{formatted_datetime}' WHERE email='{self.email}'"
                    print(update_query)
                    cursor.execute(update_query)
                    db.commit()
                    db.close()
                    return "User Validated",True
                else:
                    return "Password is wrong",False
                db.close()
                
        except mysql.connector.Error as err:
            print("Error:", err)
            db.close()
                
    
        
@app.route("/users/create", methods=['POST'])
def create_user():
    data = request.get_json()
    if data['name'] == '' or data['email'] == '' or data['password'] == '':
        return jsonify({"error": "Missing required fields (email, password)"}), 400
    name = data["name"]
    email = data["email"]
    password = data["password"]
    new_user = User(name, email, password)
    insertUser = new_user.insertUsers()
    if insertUser is True:
        return jsonify({"Success": "User inserted successfully"}), 200
    else:   
        return jsonify({"error": insertUser[1]}), 400
    
@app.route('/users/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name = None
    email = None
    password = None
    if "name" in data:
        name = data["name"]
    if "email" in data:
        email = data["email"]
    if "password" in data:
        password = data["password"]
    update_user = User(name, email, password)
    existing_user_update = update_user.updateUsers(user_id)
    if existing_user_update is True:
        return jsonify({"Success": "User data updated successfully"}), 200
    else:
        return jsonify({"error": existing_user[1]}), 400
    
@app.route('/users/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    delete_user = User(name = None, email = None, password = None)
    deleting_user = delete_user.deleteUser(user_id)
    if deleting_user is True:
        return jsonify({"Success": "User data deleted successfully"}), 200
    else:
        return jsonify({"error": existing_user[1]}), 400
    
@app.route('/users/list', methods=['GET'])
def list_users():
    user = User(name=None, email=None, password=None) 
    user_list = user.listUsers() 
    if user_list is not None:
        return jsonify({"users": user_list}), 200
    else:
        return jsonify({"error": "Failed to retrieve user list"}), 500
    
@app.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    if data['email'] == '' or data['password'] == '':
        return jsonify({"error": "Missing required fields (email, password)"}), 400
    login_user = User(name = None, email = data['email'], password = None)
    validation,flag = login_user.login(data['password'])
    if flag:
        return jsonify({"Success": "Login Successful!!"}), 200
    else:
        return jsonify({"error": validation}), 400
        
if __name__ == '__main__':
    app.run()


# In[ ]:





# In[ ]:




