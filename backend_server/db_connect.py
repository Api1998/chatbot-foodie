import mysql.connector
from mysql.connector import Error

class MySQLClient:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """Establish a connection to the MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error: {e}")

    def disconnect(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")

    # Function to call the MySQL stored procedure and insert an order item
    def insert_order_item(self, food_item, quantity, order_id):
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()

            # Calling the stored procedure
            cursor.callproc('insert_order_item', (food_item, quantity, order_id))

            # Committing the changes
            self.connection.commit()

            # Closing the cursor
            cursor.close()

            print("Order item inserted successfully!")

            return 1

        except mysql.connector.Error as err:
            print(f"Error inserting order item: {err}")

            # Rollback changes if necessary
            self.connection.rollback()

            return -1

        except Exception as e:
            print(f"An error occurred: {e}")
            # Rollback changes if necessary
            self.connection.rollback()

            return -1
        
    # Function to insert a record into the order_tracking table
    def insert_order_tracking(self, order_id, status):
        cursor = self.connection.cursor()

        # Inserting the record into the order_tracking table
        insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
        cursor.execute(insert_query, (order_id, status))

        # Committing the changes
        self.connection.commit()

        # Closing the cursor
        cursor.close()

    def get_total_order_price(self, order_id):
        cursor = self.connection.cursor()

        # Executing the SQL query to get the total order price
        query = f"SELECT get_total_order_price({order_id})"
        cursor.execute(query)

        # Fetching the result
        result = cursor.fetchone()[0]

        # Closing the cursor
        cursor.close()

        return result

    # Function to get the next available order_id
    def get_next_order_id(self):
        cursor = self.connection.cursor()

        # Executing the SQL query to get the next available order_id
        query = "SELECT MAX(order_id) FROM orders"
        cursor.execute(query)

        # Fetching the result
        result = cursor.fetchone()[0]

        # Closing the cursor
        cursor.close()

        # Returning the next available order_id
        if result is None:
            return 1
        else:
            return result + 1
    
    # Function to fetch the order status from the order_tracking table
    def get_order_status(self, order_id: int):
        cursor = self.connection.cursor()

        # Executing the SQL query to fetch the order status
        query = f"SELECT status FROM order_tracking WHERE order_id = {order_id}"
        cursor.execute(query)

        # Fetching the result
        result = cursor.fetchone()

        # Closing the cursor
        cursor.close()

        # Returning the order status
        if result:
            return result[0]
        else:
            return None

# Example usage:
if __name__ == "__main__":
    # Replace with your actual database credentials
    db_config = {
        'host': 'localhost',
        'user': 'your_username',
        'password': 'your_password',
        'database': 'your_database'
    }
    