# Data Wrangling Studio

## Project Overview
Data Wrangling Studio is a Streamlit app that allows users to upload a dataset, clean and transform it interactively, build visualizations, and export the cleaned dataset together with a transformation report and recipe.

## Features
- Upload datasets in CSV, Excel, and JSON format
- View dataset overview, shape, column names, data types, duplicates, and missing values
- Handle missing values by filling or dropping
- Detect and remove duplicates
- Convert data types and parse dirty numeric strings
- Clean and standardize categorical columns
- Detect outliers and apply scaling
- Rename, drop, and create columns
- Run validation checks
- Build dynamic visualizations
- Export cleaned dataset, transformation report, and JSON recipe

## File Structure
- `app.py` - main Streamlit application
- `requirements.txt` - required Python packages
- `README.md` - project documentation
- `sample_data/` - sample datasets for testing and demonstration

## How to Run the App
1. Open the project folder
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Sample Datasets
The `sample_data` folder contains two datasets for testing:
- HR dataset
- Sales dataset

## Main Sections of the App
### 1. Upload & Overview
- upload dataset
- preview data
- view rows, columns, duplicates
- inspect missing values and summary statistics

### 2. Cleaning Studio
- missing values
- duplicates
- data types and parsing
- categorical tools
- numeric cleaning, scaling, and outliers
- column operations
- validation rules

### 3. Visualization
- histogram
- box plot
- scatter plot
- line chart
- bar chart
- correlation heatmap
- category and numeric filtering

### 4. Export & Report
- export cleaned CSV
- export cleaned Excel file
- export transformation report
- export JSON recipe

## Notes
- Reset Session clears the uploaded dataset and current working session
- The app uses session state to preserve the working dataframe and transformation log
- Matplotlib and Plotly are used for visualizations

