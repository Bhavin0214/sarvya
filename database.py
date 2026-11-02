import mysql.connector
from mysql.connector import Error
import logging

class Database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""  # Set your MySQL password
        self.database = "sarvya_db"
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection and self.connection.is_connected():
                return True
        except Error as e:
            return False 
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query, params=None):
        """Execute INSERT, UPDATE, DELETE queries"""
        try:
            if not self.connection or not self.connection.is_connected():
                return False
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            return True
        except Error as e:
            print(f"❌ Query execution failed: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def fetch_all(self, query, params=None):
        """Execute SELECT query and return all results"""
        try:
            if not self.connection or not self.connection.is_connected():
                return []
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            print(f"❌ Fetch query failed: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def fetch_one(self, query, params=None):
        """Execute SELECT query and return single result"""
        try:
            if not self.connection or not self.connection.is_connected():
                return None
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            print(f"❌ Fetch one query failed: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()

# Create global database instance
db = Database()