import streamlit as st
import pandas as pd
import os
from io import BytesIO
import zipfile

# Configure the Streamlit app's appearance and layout
st.set_page_config(page_title="Data Sweeper", layout="wide")

# Custom CSS for styling the app with a professional dark theme
st.markdown(
    """
    <style>
        .main {
            background-color: #0e1117;  /* Dark background for the main page */
            color: #ffffff;  /* White text for better readability */
        }
        .block-container {
            padding: 2rem 1.5rem;  /* Padding around main container for spacing */
            border-radius: 8px;  /* Rounds the corners of the container */
            background-color: #1e1e1e;  /* Slightly lighter shade for contrast */
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);  /* Adds subtle shadow for depth */
        }
        h1 {
            color: #4a90e2;  /* Light blue for main title */
            font-family: 'Arial', sans-serif;  /* Modern font for headings */
        }
        h2 {
            color: #ff6f61;  /* Coral color for subheadings */
            font-family: 'Arial', sans-serif;
        }
        h3 {
            color: #6bff6b;  /* Light green for smaller headings */
            font-family: 'Arial', sans-serif;
        }
        h4, h5, h6 {
            color: #ffcc00;  /* Yellow for smaller headings */
            font-family: 'Arial', sans-serif;
        }
        .stButton>button {
            border: none;
            border-radius: 6px;  /* Rounds button edges */
            background-color: #4a90e2;  /* Primary blue for buttons */
            color: white;  /* White text for contrast */
            padding: 0.5rem 1rem;  /* Enlarges button for better interaction */
            font-size: 0.9rem;  /* Readable button text */
            font-family: 'Arial', sans-serif;  /* Modern font for buttons */
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);  /* Shadow for button depth */
        }
        .stButton>button:hover {
            background-color: #357abd;  /* Darker blue on hover for visual feedback */
            cursor: pointer;
        }
        .stDataFrame, .stTable {
            border-radius: 8px;  /* Smooth edges for data tables and frames */
            overflow: hidden;  /* Prevents data from overflowing the container */
            background-color: #2e2e2e;  /* Dark background for tables */
            color: #ffffff;  /* White text for tables */
        }
        .css-1aumxhk, .css-18e3th9 {
            text-align: left;
            color: #ffffff;  /* Ensures all standard text is white for readability */
            font-family: 'Arial', sans-serif;  /* Modern font for text */
        }
        .stRadio>label {
            font-weight: bold;
            color: #ffffff;  /* White text for radio buttons */
            font-family: 'Arial', sans-serif;  /* Modern font for radio buttons */
        }
        .stCheckbox>label {
            color: #ffffff;  /* White text for checkboxes */
            font-family: 'Arial', sans-serif;  /* Modern font for checkboxes */
        }
        .stDownloadButton>button {
            background-color: #28a745;  /* Green color for download buttons */
            color: white;
            font-family: 'Arial', sans-serif;  /* Modern font for download buttons */
        }
        .stDownloadButton>button:hover {
            background-color: #218838;  /* Darker green on hover for download buttons */
        }
        .stMarkdown {
            color: #ffffff;  /* White text for markdown */
            font-family: 'Arial', sans-serif;  /* Modern font for markdown */
        }
    </style>
    """,
    unsafe_allow_html=True  # 'unsafe_allow_html' permits raw HTML/CSS embedding in the Streamlit app
)

# Display the main app title and introductory text
st.title("Advanced Data Sweeper")  # Large, eye-catching title
st.write("Transform your files between CSV and Excel formats with built-in data cleaning, filtering, and visualization.")

# File uploader widget that accepts CSV and Excel files
uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

# Initialize a list to store processed files for ZIP export
processed_files = []

# Processing logic for uploaded files (if any files are uploaded)
if uploaded_files:
    for file in uploaded_files:
        # Extract the file extension to determine if it's CSV or Excel
        file_extension = os.path.splitext(file.name)[-1].lower()
        
        # Read the uploaded file into a pandas DataFrame based on its extension
        try:
            if file_extension == ".csv":
                df = pd.read_csv(file)  # Read CSV files
            elif file_extension == ".xlsx":
                df = pd.read_excel(file)  # Read Excel files
            else:
                st.error(f"Unsupported file type: {file_extension}")
                continue
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")
            continue
        
        # Display uploaded file information (name and size)
        st.write(f"**📄 File Name:** {file.name}")
        st.write(f"**📏 File Size:** {file.size / 1024:.2f} KB")  # File size in KB

        # Debug: Display data types of the DataFrame
        st.write("🔍 Data Types of the Uploaded File:")
        st.write(df.dtypes)

        # Fix: Convert mixed-type columns to strings
        df = df.astype(str)

        # Preview the first 5 rows of the uploaded file
        st.write("🔍 Preview of the Uploaded File:")
        st.dataframe(df.head())  # Display a scrollable preview of the data
        
        # Section for data cleaning options
        st.subheader("🛠️ Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)  # Split cleaning options into two columns
            with col1:
                # Button to remove duplicate rows from the DataFrame
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!")
            with col2:
                # Button to fill missing numeric values with column means
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing Values in Numeric Columns Filled with Column Means!")

        # New Feature: Data Filtering
        st.subheader("🔍 Data Filtering")
        filter_condition = st.text_input(f"Enter a condition to filter rows (e.g., `column_name > 50` for {file.name}):")
        if filter_condition:
            try:
                df = df.query(filter_condition)
                st.write(f"Filtered Data for {file.name}:")
                st.dataframe(df)
            except Exception as e:
                st.error(f"Invalid filter condition: {e}")

        # New Feature: Column Renaming
        st.subheader("✏️ Column Renaming")
        rename_dict = {}
        for col in df.columns:
            new_name = st.text_input(f"Rename '{col}' to:", key=f"rename_{col}_{file.name}")
            if new_name:
                rename_dict[col] = new_name
        if rename_dict:
            df.rename(columns=rename_dict, inplace=True)
            st.write("Updated Column Names:")
            st.write(df.columns)

        # New Feature: Data Summary Statistics
        st.subheader("📊 Summary Statistics")
        if st.checkbox(f"Show Summary Statistics for {file.name}"):
            st.write(df.describe())

        # Visualization section for uploaded data
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            chart_type = st.selectbox(f"Select Chart Type for {file.name}", ["Bar Chart", "Line Chart", "Scatter Plot"])
            numeric_cols = df.select_dtypes(include='number').columns
            if len(numeric_cols) >= 2:
                if chart_type == "Bar Chart":
                    st.bar_chart(df[numeric_cols].iloc[:, :2])
                elif chart_type == "Line Chart":
                    st.line_chart(df[numeric_cols].iloc[:, :2])
                elif chart_type == "Scatter Plot":
                    st.write("Select two numeric columns for the scatter plot:")
                    x_axis = st.selectbox("X-axis", numeric_cols, key=f"x_axis_{file.name}")
                    y_axis = st.selectbox("Y-axis", numeric_cols, key=f"y_axis_{file.name}")
                    st.scatter_chart(df[[x_axis, y_axis]])
            else:
                st.warning("Not enough numeric columns for visualization.")

        # Section to choose file conversion type (CSV or Excel)
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()  # Creates in-memory buffer for file output
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)  # Save DataFrame as CSV in buffer
                file_name = file.name.replace(file_extension, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False, engine='openpyxl')  # Save as Excel using openpyxl
                file_name = file.name.replace(file_extension, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)
            
            # Download button for the converted file
            st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )
            processed_files.append((file_name, buffer))

    # New Feature: Export All Files as ZIP
    if processed_files:
        st.subheader("📦 Export All Files")
        if st.button("Export All Files as ZIP"):
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for file_name, buffer in processed_files:
                    zip_file.writestr(file_name, buffer.getvalue())
            zip_buffer.seek(0)
            st.download_button(
                label="⬇️ Download All Files as ZIP",
                data=zip_buffer,
                file_name="processed_files.zip",
                mime="application/zip"
            )

st.success("🎉 All files processed successfully!")
