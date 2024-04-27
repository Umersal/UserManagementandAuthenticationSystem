# UserManagementandAuthenticationSystem.

1. This project is a simple user management and authentication system that authenticates users whenever they log in. 
2. It is built with Python on top of the Flask framework for API creation and management.
3. In addition to the requirements that were given, I have implemented hashing in order to maintain the security while storing and retriving the password
4. MySQL is used as the backend database, sourced from an online platform called Aiven. You can find the MySQL service on their website: https://aiven.io/mysql.
5. All the private credentials like username, host, password, etc are stored as a config file which is used in the code using configParser
6. The code can be complied and we can run in our local system.
7. I have used jupyter notebooks to complile, run and execute the code.

# Reference and Usage:
1. MYSQL: https://aiven.io/mysql
2. MYSQL python connector: https://www.w3schools.com/python/python_mysql_getstarted.asp
3. Password hasher for python: https://argon2-cffi.readthedocs.io/en/stable/
4. To catch exception when duplicate email id found: https://stackoverflow.com/questions/67567606/how-to-catch-mysql-insert-exception-1062-23000-duplicate-entry-while-catch
