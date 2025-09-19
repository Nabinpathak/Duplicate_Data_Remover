import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import config
import io

# ------------------- Connect to DB -------------------
engine = create_engine(config.DB_URL)

# ------------------- Streamlit Interface -------------------
st.title("Excel to Database Uploader")
st.write("Upload an Excel file to add unique records to the database based on Place_ID.")
try:
    total_data = pd.read_sql("SELECT COUNT(*) FROM leads", engine)
    st.write(f"📊 Total records in 'leads' table: {total_data.iloc[0,0]}")
except Exception as e:
    st.error(f"❌ Error fetching record count: {str(e)}")

# File uploader
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Read the Excel file
        data = pd.read_excel(uploaded_file)
        st.write(f"📄 Loaded Excel file: {uploaded_file.name}")
        st.write(f"📊 Preview of uploaded data:")
        st.dataframe(data.head())

        # Get existing data from the database
        db_data = pd.read_sql("SELECT * FROM leads", engine)
        # Ensure column names match the database (case-insensitive handling)
        data.columns = data.columns.str.lower()
        db_columns = pd.read_sql("SELECT * FROM leads LIMIT 0", engine).columns
        
        # Debugging: Show database and Excel columns
        st.write(f"📋 Database columns: {list(db_columns)}")
        st.write(f"📋 Excel columns (after lowercase): {list(data.columns)}")
        
        # Create a new DataFrame with all database columns, filled with None
        aligned_data = pd.DataFrame(columns=db_columns)
        
        # Copy matching columns from the uploaded Excel to the aligned DataFrame, forcing all to TEXT
        matched_columns = []
        for col in data.columns:
            if col in db_columns:
                aligned_data[col] = data[col].astype(str)  # Force all values to string
                matched_columns.append(col)
            else:
                st.warning(f"⚠️ Column '{col}' in Excel file is not in the database schema and will be ignored.")
        st.write(f"📋 Matched columns to be inserted: {matched_columns}")
        
        # Handle Place_ID for uniqueness
        if "place_id" not in aligned_data.columns:
            st.error("❌ The uploaded Excel file must contain a 'Place_ID' column.")
        else:
            # Check for duplicate place_id in the Excel file
            duplicate_place_ids = aligned_data[aligned_data.duplicated(subset=['place_id'], keep=False)]
            if not duplicate_place_ids.empty:
                st.warning(f"⚠️ Found {len(duplicate_place_ids)} rows with duplicate place_id values in the Excel file. Only unique rows will be inserted.")
            
            # Merge to find unique rows based on Place_ID
            merged = pd.merge(aligned_data, db_data[['place_id']], on="place_id", how="left", indicator=True)
            unique_data = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])
            
            # Remove any columns not in the database schema
            unique_data = unique_data[[col for col in unique_data.columns if col in db_columns]]
            
            if not unique_data.empty:
                # Debugging: Show data to be inserted
                st.write(f"📊 Preview of unique data to insert (based on Place_ID, {len(unique_data)} rows):")
                st.dataframe(unique_data.head())
                
                # Insert unique rows into the database
                with engine.connect() as connection:
                    try:
                        unique_data.to_sql("leads", connection, if_exists="append", index=False)
                        st.success(f"✅ Inserted {len(unique_data)} unique rows from '{uploaded_file.name}' into 'leads'.")
                    except Exception as e:
                        st.error(f"❌ Insertion failed: {str(e)}")
            else:
                st.warning("⚠️ No new unique rows found based on Place_ID. Check for existing place_id values in the database.")
                
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
else:
    st.info("ℹ️ Please upload an Excel file to proceed.")

# ------------------- Filter and Download Section -------------------
st.header("Filter Data by State and Download")

# Check if 'state' column exists in the database
db_columns = pd.read_sql("SELECT * FROM leads LIMIT 0", engine).columns
if "state" not in db_columns:
    st.error("❌ The 'leads' table does not have a 'state' column. Please add a 'state' column to the database using ALTER TABLE.")
else:
    # Hardcoded list of all 50 US states (sorted alphabetically)
    us_states = [
        'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware',
        'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky',
        'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
        'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico',
        'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
        'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
        'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
    ]
    
    # Allow multiple state selection
    selected_states = st.multiselect("Select States (multiple allowed)", us_states)
    
    if selected_states:
        try:
            # Query filtered data
            filter_query = "SELECT * FROM leads WHERE state IN %s"
            filtered_data = pd.read_sql(filter_query, engine, params=(tuple(selected_states),))
            
            if filtered_data.empty:
                st.warning("⚠️ No data found for the selected states. Ensure the 'state' column in the database contains these values.")
            else:
                st.write(f"📊 Filtered data preview (for selected states: {', '.join(selected_states)}):")
                st.dataframe(filtered_data.head())
            
            # Prepare Excel download (even if empty, allow download)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filtered_data.to_excel(writer, index=False, sheet_name='Filtered Leads')
            output.seek(0)
            
            st.download_button(
                label="Download Filtered Data as Excel",
                data=output,
                file_name="filtered_leads.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"❌ Error during filtering: {str(e)}")
    else:
        st.info("ℹ️ Select one or more states to filter and download data.")