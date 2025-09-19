# Duplicate_Data_Remover
A Python-based web application designed to upload Excel files to a PostgreSQL database, focusing on managing business data. This project provides an interactive interface to import records, ensure uniqueness based on unique id, and filter/export data. Built to handle real-world data challenges, it includes robust error handing.

#Features

Excel Upload: 
Uploads Excel files (e.g., .xlsx, .xls) and maps columns to a leads table in a PostgreSQL database.

Data Uniqueness: 
Ensures only unique records are inserted based on the place_id column.

State Filtering: 
Allows filtering of database records by US state and downloading the filtered data as an Excel file.

Debugging Support: 
Provides previews and logs of uploaded data, matched columns, and insertion status for troubleshooting.

Flexible Schema: 
Supports a schema with 69 columns, including id, place_id, state, name, and more, with adaptive data type handling (e.g., converting unsigned integers to text).

#Technologies

Python: Core language for scripting and logic.
PostgreSQL: Database for storing lead data.
SQLAlchemy: ORM and database connection library.
pandas: For Excel file processing and data manipulation.
Streamlit: Interactive web interface (alternative frameworks like Dash or Flask can be explored).

#Installation

Clone the repository:
git clone https://github.com/Nabinpathak/Duplicate_Data_Remover.git
cd Duplicate_Data_Remover

Install dependencies:
pip install -r libraries.txt

Configure config.py with your PostgreSQL credentials (e.g., DB_URL).
Set up the database and create the leads table (SQL script provided in the repo).

Run the app:
streamlit run app.py

#Usage

Upload an Excel file containing lead data (e.g., Vape-shop-in-Lauderhill,-FL-(09-13-2025).xlsx).
Review the preview and matched columns in the interface.
Insert unique records into the database and filter by state for export.

#Challenges & Solutions

Unsigned 64-bit Integer Issue: Resolved by converting all numeric data to text (TEXT type) to ensure compatibility with PostgreSQL.

Schema Mismatch: Handled by aligning Excel columns with the database schema and providing warnings for unmatched columns.
