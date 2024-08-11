import snowflake.connector as sf
import pandas as pd

# Snowflake connection details
SF_USER = 'SRIMATHI'
SF_PASSWORD = 'Shri@1608'
SF_ACCOUNT = 'wu16729.ap-southeast-1'
SF_WAREHOUSE = 'COMPUTE_WH'
SF_DATABASE = 'MEC'
SF_SCHEMA = 'MEC'
SF_ROLE = 'ACCOUNTADMIN'

#SF_USER = 'SHYAAM'
#SF_PASSWORD = 'Shyaamkumar@31'
#SF_ACCOUNT = 'oy99057.ap-southeast-1'
#SF_WAREHOUSE = 'COMPUTE_WH'
#SF_DATABASE = 'MEC'
#SF_SCHEMA = 'STUDENT'
#SF_ROLE = 'ACCOUNTADMIN'

def execute_mysql_query(sql):
    try:
        # Establish connection
        conn = sf.connect(
            user=SF_USER,
            password=SF_PASSWORD,
            account=SF_ACCOUNT,
            warehouse=SF_WAREHOUSE,
            database=SF_DATABASE,
            schema=SF_SCHEMA,
            role=SF_ROLE
        )
        print("Connection established")

        # Execute query
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Fetch results
        results = cursor.fetchall()

        # Convert results to DataFrame
        df = pd.DataFrame(results, columns=[col[0] for col in cursor.description])

        # Close cursor and connection
        cursor.close()
        conn.close()

        return df

    except sf.Error as e:
        print(f"An error occurred: {e}")
        return None