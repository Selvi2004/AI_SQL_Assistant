import os
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.url import URL

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

# Function to create SQLAlchemy engine for Snowflake
def connect_to_snowflake(user, password, account, warehouse, database, schema, role):
    try:
        # Create connection string using URL.create
        connection_string = URL.create(
            drivername='snowflake',
            username=user,
            password=password,
            host=f'{account}',  # Use account name without .snowflakecomputing.com
            database=database,
            query={
                'warehouse': warehouse,
                'schema': schema,
                'role': role
            }
        )
        # Create the SQLAlchemy engine
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        print(f"Error creating Snowflake engine: {e}")
        raise

# Setup the Snowflake connection
engine = connect_to_snowflake(SF_USER, SF_PASSWORD, SF_ACCOUNT, SF_WAREHOUSE, SF_DATABASE, SF_SCHEMA, SF_ROLE)
inspector = inspect(engine)



# Define the Table and Column classes
class Table(BaseModel):
    """Table in SQL database."""
    name: str = Field(description="Name of table in SQL database.")

class Column(BaseModel):
    """Column in SQL table."""
    name: str = Field(description="Name of column in SQL table.")
    type: str = Field(description="Data type of the column.")

# Function to generate examples
def generate_examples(table, columns):
    examples = []
    column_list = ", ".join(columns) if columns else "*"
    column_condition = columns[0] if columns else "column_name"
    
    examples.append(f"""EXAMPLE

Conversation history:
Person #1: Please show me the {table} table
AI: SELECT * FROM {table};
Last line:
Person #1: Show me the {table} with {column_condition} = 'example_value'.
Output: SELECT {column_list}
FROM {table}
WHERE {column_condition} = 'example_value';

END OF EXAMPLE""")

    examples.append(f"""EXAMPLE

Conversation history:
Person #1: provide me the database name
AI: SELECT CURRENT_DATABASE();
Person #1: list the tables in our database
AI: Show tables;

Last line:
Person #1:
Output: SHOW COLUMNS IN TABLE {table};
END OF EXAMPLE""")

    examples.append(f"""EXAMPLE

Conversation history:
Person #1: hello / hi
AI: "hi, tell me how can i help you"
Person #1: list the {table} details
AI: SELECT {column_list} FROM {table};

Last line:
Person #1: list the {table} details of only {column_condition}
Output: SELECT * FROM {table} WHERE LOWER({column_condition}) LIKE '%example_value%';

END OF EXAMPLE""")

                
                    

    return "\n\n".join(examples)
# for the above genereated example prompts to work effectively a context word needs to be specified 
# Function to get table names from Snowflake
def get_table_names():
    return inspector.get_table_names(schema=SF_SCHEMA)

# Function to get column names from Snowflake
def get_column_names(table_name):
    columns = inspector.get_columns(table_name, schema=SF_SCHEMA)
    return [column['name'] for column in columns]

# Extract column names for each table and generate examples
all_examples = []
for table in get_table_names():
    column_names = get_column_names(table)
    if column_names:
        examples = generate_examples(table, column_names)
        all_examples.append(examples)
    else:
        print(f"No columns found for table {table}.")

# Append the context block at the end
context_block = """
Conversation history (for reference only):
{history}
Last line of conversation (for extraction):
User: {input}

Context:
{entities}

Current conversation:

Last line:
Human: {input}

You:"""

all_examples.append(context_block)

# Print or save the combined examples and context block
final_output = "\n\n".join(all_examples)


# Function to get table names from Snowflake
def get_table_names():
    return inspector.get_table_names(schema=SF_SCHEMA)

# Function to get column names and types from Snowflake
def get_columns_info(table_name):
    columns = inspector.get_columns(table_name, schema=SF_SCHEMA)
    return [(column['name'], column['type']) for column in columns]

# Function to generate schema string for the database
def generate_schema_string():
    schema_strings = []
    for table in get_table_names():
        columns_info = get_columns_info(table)
        if columns_info:
            columns_str = "<ul>" + "".join([f"<li><b>{col_name}</b> ({col_type})</li>" for col_name, col_type in columns_info]) + "</ul>"
            schema_strings.append(f"<h3>{table}</h3>{columns_str}")
        else:
            print(f"No columns found for table {table}.")
    return "".join(schema_strings)
def schema_venum():
    schema_string = generate_schema_string()
    return schema_string