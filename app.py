import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Wrangling Studio", layout="wide")

st.title("Data Wrangling Studio")

if "original_df" not in st.session_state:
    st.session_state.original_df = None
if "working_df" not in st.session_state:
    st.session_state.working_df = None
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None
if "transform_log" not in st.session_state:
    st.session_state.transform_log = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if st.button("Reset Session"):
    st.session_state.original_df = None
    st.session_state.working_df = None
    st.session_state.last_uploaded_file = None
    st.session_state.transform_log = []
    st.session_state.uploader_key += 1
    st.rerun()

uploaded_file = st.file_uploader("Upload a file",
                                 type=["csv", "xlsx", "json"],
                                 key=f"file)uploader_{st.session_state.uploader_key}"
                                 )

if uploaded_file is not None:
    file_name = uploaded_file.name

    if st.session_state.last_uploaded_file != file_name or st.session_state.original_df is None:
        try:
            if file_name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif file_name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            elif file_name.endswith(".json"):
                df = pd.read_json(uploaded_file)
            else:
                st.error("Unsupported file type.")
                st.stop()

            st.session_state.original_df = df.copy()
            st.session_state.working_df = df.copy()

            st.success("File uploaded successfully.")

            if st.session_state.last_uploaded_file != file_name:
                st.session_state.transform_log.append({
                    "step": "File uploaded",
                    "file_name": file_name
                })
                st.session_state.last_uploaded_file = file_name

        except Exception as e:
            st.error(f"Error reading file: {e}")

page = st.sidebar.radio(
    "Navigation",
    ["Upload & Overview", "Cleaning Studio", "Visualization", "Export & Report"],
    horizontal=True
)
if page == "Upload & Overview":
    if st.session_state.working_df is not None:
        df = st.session_state.working_df

        st.subheader("Dataset Preview")
        st.dataframe(df.head())

        st.subheader("Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])
        col3.metric("Duplicates", df.duplicated().sum())

        st.subheader("Column Names and Data Types")
        info_df = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str)
        })
        st.dataframe(info_df)

        st.subheader("Missing Values Summary")
        missing_df = pd.DataFrame({
            "Column": df.columns,
            "Missing Count": df.isnull().sum().values,
            "Missing Percent": (df.isnull().sum().values / len(df) * 100).round(2)
        })
        st.dataframe(missing_df)

        st.subheader("Summary Statistics")
        st.write("Numeric Summary")
        st.dataframe(df.describe())

        st.write("Categorical Summary")
        st.dataframe(df.describe(include=["object"]))

    else:
        st.info("Please upload a dataset first.")


if page == "Cleaning Studio":
    if st.session_state.working_df is not None:
        df = st.session_state.working_df

        st.header("Cleaning Studio")

        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "Missing Values",
            "Duplicates",
            "Types & Parsing",
            "Categorical Tools",
            "Cleaning, Scaling and Outliers",
            "Column Operations",
            "Validation"
        ])

        with tab1:
            st.info(
                "Handle null values by filling, dropping rows, or dropping columns above a "
                "missing-value threshold.")

            st.subheader("Missing Values Summary")
            missing_df = pd.DataFrame({
                "Column": df.columns,
                "Missing Count": df.isnull().sum().values,
                "Missing Percent": (df.isnull().sum().values / len(df) * 100).round(2)
            })
            st.dataframe(missing_df)

            missing_columns = df.columns[df.isnull().sum() > 0].tolist()

            if not missing_columns:
                st.success("No missing values remained in the dataset")
            else:
                selected_column = st.selectbox(
                    "Select a column with missing values",
                    options=missing_columns
                )

                st.write("Rows with missing values in selected column")
                st.dataframe(df[df[selected_column].isnull()].head())

                action = st.radio(
                    "Choose action",
                    ["Fill Missing Values", "Drop Rows with Missing Values"]
                )

                if action == "Fill Missing Values":
                    if pd.api.types.is_numeric_dtype(df[selected_column]):
                        fill_options = ["Mean", "Median", "Mode", "Constant"]
                    else:
                        fill_options = ["Mode", "Constant"]

                    fill_method = st.selectbox(
                        "Select fill method",
                        fill_options,
                        key=f"fill_method_{selected_column}"
                    )

                    constant_value = None
                    if fill_method == "Constant":
                        constant_value = st.text_input("Enter constant value")

                if st.button("Apply Missing Value Treatment"):
                    df_before = df.copy()
                    before_treatment = df_before[selected_column].isnull().sum()

                    if action == "Fill Missing Values":
                        if fill_method == "Mean":
                            df[selected_column] = df[selected_column].fillna(df[selected_column].mean())
                        elif fill_method == "Median":
                            df[selected_column] = df[selected_column].fillna(df[selected_column].median())
                        elif fill_method == "Mode":
                            df[selected_column] = df[selected_column].fillna(df[selected_column].mode()[0])
                        elif fill_method == "Constant":
                            df[selected_column] = df[selected_column].fillna(constant_value)

                        log_action = {
                            "step": "Missing values filled",
                            "column": selected_column,
                            "method": fill_method
                        }

                    elif action == "Drop Rows with Missing Values":
                        df = df.dropna(subset=[selected_column])

                        log_action = {
                            "step": "Rows dropped for missing values",
                            "column": selected_column
                        }

                    st.session_state.working_df = df
                    st.session_state.transform_log.append(log_action)

                    after_treatment = df[selected_column].isnull().sum()

                    st.rerun()
                # st.write("Before treatment:", before_treatment)
                # st.write("After treatment:", after_treatment)
                # st.success("Missing values treated successfully.")

        with tab2:

            st.info("Detect and remove full-row duplicates or duplicates based on selected key columns.")

            st.subheader("Duplicate Rows Summary")
            duplicated_rows = df[df.duplicated(keep=False)]
            st.dataframe(duplicated_rows)
            st.write("Number of duplicate rows:", df.duplicated().sum())

            keep_option = st.selectbox(
                "When removing duplicates, keep",
                ["first", "last"]
            )

            if st.button("Remove Full-Row Duplicates"):
                before_rows = len(df)
                df = df.drop_duplicates()
                after_rows = len(df)

                st.session_state.working_df = df
                st.session_state.transform_log.append({
                    "step": "Full-row duplicates removed",
                    "rows_removed": before_rows - after_rows,
                    "keep": keep_option
                })
                st.rerun()

            subset_columns = st.multiselect(
                "Select columns to check duplicates by",
                options=df.columns.tolist()
            )

            if subset_columns:
                subset_duplicates = df[df.duplicated(subset=subset_columns, keep=False)]
                st.write("Subset duplicate rows:")
                st.dataframe(subset_duplicates)

            if subset_columns:

                if st.button("Remove Subset Duplicates"):
                    before_rows = len(df)
                    df = df.drop_duplicates(subset=subset_columns, keep=keep_option)
                    after_rows = len(df)

                    st.session_state.working_df = df
                    st.session_state.transform_log.append({
                        "step": "Subset duplicates removed",
                        "columns": subset_columns,
                        "rows_removed": before_rows - after_rows,
                        "keep": keep_option
                    })
                    st.rerun()

        with tab3:

            st.info(
                "Convert columns to numeric, datetime, or category types and parse dirty numeric strings safely.")

            st.subheader("Data Types & Parsing")

            convert_column = st.selectbox(
                "Select column to convert",
                options=df.columns.tolist(),
                key="convert_column"
            )
            st.write("Selected column type: ", df[convert_column].dtype)

            target_type = st.selectbox(
                "Convert selected column to",
                ["numeric", "datetime", "category"],
                key="target_type"
            )

            if target_type == "datetime":
                datetime_format = st.text_input(
                    "Optional datetime format (leave empty for auto parse)",
                    key="datetime_format"
                )
            else:
                datetime_format = None

            clean_dirty_numeric = False
            if target_type == "numeric":
                clean_dirty_numeric = st.checkbox(
                    "Clean dirty numeric strings first (commas, currency signs, spaces)",
                    key="clean_dirty_numeric"
                )

            if st.button("Apply Type Conversion"):
                df = st.session_state.working_df.copy()

                try:
                    before_dtype = str(df[convert_column].dtype)

                    if target_type == "numeric":
                        if clean_dirty_numeric:
                            df[convert_column] = (
                                df[convert_column]
                                .astype(str)
                                .str.replace(",", "", regex=False)
                                .str.replace("$", "", regex=False)
                                .str.strip()
                            )
                        df[convert_column] = pd.to_numeric(df[convert_column], errors="coerce")

                    elif target_type == "datetime":
                        if datetime_format:
                            df[convert_column] = pd.to_datetime(
                                df[convert_column],
                                format=datetime_format,
                                errors="coerce"
                            )
                        else:
                            df[convert_column] = pd.to_datetime(
                                df[convert_column],
                                errors="coerce"
                            )

                    elif target_type == "category":
                        df[convert_column] = df[convert_column].astype("category")

                    after_dtype = str(df[convert_column].dtype)

                    st.session_state.working_df = df
                    st.session_state.transform_log.append({
                        "step": "Column type converted",
                        "column": convert_column,
                        "from": before_dtype,
                        "to": after_dtype,
                        "target_type": target_type,
                        "dirty_numeric_cleaned": clean_dirty_numeric if target_type == "numeric" else None,
                        "datetime_format": datetime_format if target_type == "datetime" else None
                    })

                    st.rerun()

                except Exception as e:
                    st.error(f"Conversion failed: {e}")

        with tab4:

            st.info("Standardize text categories, apply custom mappings, and group rare values into 'Other'.")

            st.subheader("Categorical Data Tools")

            categorical_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()

            if categorical_columns:
                cat_column = st.selectbox(
                    "Select categorical column",
                    options=categorical_columns,
                    key="cat_column"
                )

                cat_action = st.selectbox(
                    "Choose categorical action",
                    [
                        "Trim Whitespace",
                        "Lower Case",
                        "Title Case",
                        "Mapping / Replacement",
                        "Group Rare Categories"
                    ],
                    key="cat_action"
                )

                st.write("Current unique values preview")
                st.dataframe(pd.DataFrame({
                    "Unique Values": df[cat_column].dropna().astype(str).unique()[:20]
                }))

                if cat_action == "Mapping / Replacement":
                    st.write("Enter mapping pairs")
                    mapping_text = st.text_area(
                        "Format: old_value:new_value (one per line)",
                        key="mapping_text"
                    )

                if cat_action == "Group Rare Categories":
                    rare_threshold = st.number_input(
                        "Group categories with frequency less than this number into 'Other'",
                        min_value=1,
                        value=5,
                        step=1,
                        key="rare_threshold"
                    )

                if st.button("Apply Categorical Treatment"):
                    df = st.session_state.working_df.copy()

                    try:
                        if cat_action == "Trim Whitespace":
                            df[cat_column] = df[cat_column].astype(str).str.strip()
                            log_action = {
                                "step": "Categorical trim whitespace",
                                "column": cat_column
                            }

                        elif cat_action == "Lower Case":
                            df[cat_column] = df[cat_column].astype(str).str.lower()
                            log_action = {
                                "step": "Categorical lower case",
                                "column": cat_column
                            }

                        elif cat_action == "Title Case":
                            df[cat_column] = df[cat_column].astype(str).str.title()
                            log_action = {
                                "step": "Categorical title case",
                                "column": cat_column
                            }

                        elif cat_action == "Mapping / Replacement":
                            mapping_dict = {}
                            for line in mapping_text.splitlines():
                                if ":" in line:
                                    old, new = line.split(":", 1)
                                    mapping_dict[old.strip()] = new.strip()

                            df[cat_column] = df[cat_column].replace(mapping_dict)

                            log_action = {
                                "step": "Categorical mapping applied",
                                "column": cat_column,
                                "mapping": mapping_dict
                            }

                        elif cat_action == "Group Rare Categories":
                            value_counts = df[cat_column].value_counts(dropna=False)
                            rare_values = value_counts[value_counts < rare_threshold].index
                            df[cat_column] = df[cat_column].replace(list(rare_values), "Other")

                            log_action = {
                                "step": "Rare categories grouped",
                                "column": cat_column,
                                "threshold": rare_threshold,
                                "grouped_count": len(rare_values)
                            }

                        st.session_state.working_df = df
                        st.session_state.transform_log.append(log_action)
                        st.rerun()

                    except Exception as e:
                        st.error(f"Categorical treatment failed: {e}")

            else:
                st.info("No categorical columns available.")

        with tab5:

            st.info(
                "Review outliers, cap or remove extreme values, and apply min-max scaling or z-score standardization.")

            st.subheader("Numeric Cleaning, Outliers & Scaling")

            numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()

            if numeric_columns:
                num_column = st.selectbox(
                    "Select numeric column",
                    options=numeric_columns,
                    key="num_column"
                )

                num_action = st.selectbox(
                    "Choose numeric action",
                    [
                        "Outlier Summary",
                        "Cap Outliers (IQR)",
                        "Remove Outlier Rows (IQR)",
                        "Min-Max Scaling",
                        "Z-Score Standardization"
                    ],
                    key="num_action"
                )

                q1 = df[num_column].quantile(0.25)
                q3 = df[num_column].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr

                outlier_mask = (df[num_column] < lower_bound) | (df[num_column] > upper_bound)
                outlier_count = outlier_mask.sum()

                st.write(f"Q1: {q1}")
                st.write(f"Q3: {q3}")
                st.write(f"IQR: {iqr}")
                st.write(f"Lower Bound: {round(lower_bound, 2)}")
                st.write(f"Upper Bound: {round(upper_bound, 2)}")
                st.write(f"Outlier Count: {outlier_count}")

                if num_action == "Outlier Summary":
                    st.dataframe(df[outlier_mask][[num_column]].head(20))

                if st.button("Apply Numeric Treatment"):
                    df = st.session_state.working_df.copy()

                    try:
                        if num_action == "Cap Outliers (IQR)":
                            before_outliers = (
                                    (df[num_column] < lower_bound) | (df[num_column] > upper_bound)
                            ).sum()

                            df[num_column] = df[num_column].clip(lower=lower_bound, upper=upper_bound)

                            after_outliers = (
                                    (df[num_column] < lower_bound) | (df[num_column] > upper_bound)
                            ).sum()

                            log_action = {
                                "step": "Outliers capped",
                                "column": num_column,
                                "method": "IQR",
                                "before_outliers": int(before_outliers),
                                "after_outliers": int(after_outliers)
                            }

                        elif num_action == "Remove Outlier Rows (IQR)":
                            before_rows = len(df)
                            mask = (df[num_column] >= lower_bound) & (df[num_column] <= upper_bound)
                            df = df[mask]
                            after_rows = len(df)

                            log_action = {
                                "step": "Outlier rows removed",
                                "column": num_column,
                                "method": "IQR",
                                "rows_removed": int(before_rows - after_rows)
                            }

                        elif num_action == "Min-Max Scaling":
                            col_min = df[num_column].min()
                            col_max = df[num_column].max()

                            if col_max != col_min:
                                df[num_column] = (df[num_column] - col_min) / (col_max - col_min)

                            log_action = {
                                "step": "Min-max scaling applied",
                                "column": num_column,
                                "min": float(col_min),
                                "max": float(col_max)
                            }

                        elif num_action == "Z-Score Standardization":
                            col_mean = df[num_column].mean()
                            col_std = df[num_column].std()

                            if col_std != 0:
                                df[num_column] = (df[num_column] - col_mean) / col_std

                            log_action = {
                                "step": "Z-score standardization applied",
                                "column": num_column,
                                "mean": float(col_mean),
                                "std": float(col_std)
                            }

                        else:
                            log_action = None

                        st.session_state.working_df = df

                        if log_action is not None:
                            st.session_state.transform_log.append(log_action)

                        st.rerun()

                    except Exception as e:
                        st.error(f"Numeric treatment failed: {e}")

            else:
                st.info("No numeric columns available.")

        with tab6:

            st.info(
                "Rename or drop columns, create simple formula-based columns, and bin numeric values into ranges.")

            st.subheader("Column Operations")

            column_action = st.selectbox(
                "Choose column operation",
                [
                    "Rename Column",
                    "Drop Columns",
                    "Create Formula Column",
                    "Bin Numeric Column"
                ],
                key="column_action"
            )

            if column_action == "Rename Column":
                rename_column = st.selectbox(
                    "Select column to rename",
                    options=df.columns.tolist(),
                    key="rename_column"
                )

                new_column_name = st.text_input(
                    "Enter new column name",
                    key="new_column_name"
                )

                if st.button("Apply Rename Column"):
                    df = st.session_state.working_df.copy()

                    if new_column_name.strip() == "":
                        st.error("New column name cannot be empty.")
                    elif new_column_name in df.columns:
                        st.error("A column with this name already exists.")
                    else:
                        old_name = rename_column
                        df = df.rename(columns={old_name: new_column_name})

                        st.session_state.working_df = df
                        st.session_state.transform_log.append({
                            "step": "Column renamed",
                            "old_name": old_name,
                            "new_name": new_column_name
                        })
                        st.rerun()

            elif column_action == "Drop Columns":
                drop_columns = st.multiselect(
                    "Select columns to drop",
                    options=df.columns.tolist(),
                    key="drop_columns"
                )

                if st.button("Apply Drop Columns"):
                    df = st.session_state.working_df.copy()

                    if not drop_columns:
                        st.error("Please select at least one column.")
                    else:
                        df = df.drop(columns=drop_columns)

                        st.session_state.working_df = df
                        st.session_state.transform_log.append({
                            "step": "Columns dropped",
                            "dropped_columns": drop_columns
                        })
                        st.rerun()

            elif column_action == "Create Formula Column":
                numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()

                if len(numeric_columns) >= 1:
                    formula_type = st.selectbox(
                        "Choose formula type",
                        [
                            "colA / colB",
                            "colA - mean(colA)",
                            "log(colA)"
                        ],
                        key="formula_type"
                    )

                    new_formula_column = st.text_input(
                        "Enter new column name",
                        key="new_formula_column"
                    )

                    if formula_type == "colA / colB":
                        colA = st.selectbox("Select numerator column", numeric_columns, key="formula_colA")
                        colB = st.selectbox("Select denominator column", numeric_columns, key="formula_colB")

                    elif formula_type == "colA - mean(colA)":
                        colA = st.selectbox("Select column", numeric_columns, key="formula_colA_mean")

                    elif formula_type == "log(colA)":
                        colA = st.selectbox("Select column", numeric_columns, key="formula_colA_log")

                    if st.button("Apply Formula Column"):
                        df = st.session_state.working_df.copy()

                        try:
                            if new_formula_column.strip() == "":
                                st.error("New column name cannot be empty.")
                            elif new_formula_column in df.columns:
                                st.error("A column with this name already exists.")
                            else:
                                if formula_type == "colA / colB":
                                    df[new_formula_column] = df[colA] / df[colB]
                                elif formula_type == "colA - mean(colA)":
                                    df[new_formula_column] = df[colA] - df[colA].mean()
                                elif formula_type == "log(colA)":
                                    import numpy as np

                                    df[new_formula_column] = np.where(df[colA] > 0, np.log(df[colA]), np.nan)

                                st.session_state.working_df = df
                                st.session_state.transform_log.append({
                                    "step": "Formula column created",
                                    "new_column": new_formula_column,
                                    "formula_type": formula_type
                                })
                                st.rerun()

                        except Exception as e:
                            st.error(f"Formula creation failed: {e}")
                else:
                    st.info("No numeric columns available for formula operations.")

            elif column_action == "Bin Numeric Column":
                numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()

                if numeric_columns:
                    bin_column = st.selectbox(
                        "Select numeric column to bin",
                        numeric_columns,
                        key="bin_column"
                    )

                    bin_method = st.selectbox(
                        "Choose binning method",
                        ["Equal Width", "Quantile"],
                        key="bin_method"
                    )

                    bin_count = st.number_input(
                        "Number of bins",
                        min_value=2,
                        value=4,
                        step=1,
                        key="bin_count"
                    )

                    new_bin_column = st.text_input(
                        "Enter new binned column name",
                        key="new_bin_column"
                    )

                    if st.button("Apply Binning"):
                        df = st.session_state.working_df.copy()

                        try:
                            if new_bin_column.strip() == "":
                                st.error("New column name cannot be empty.")
                            elif new_bin_column in df.columns:
                                st.error("A column with this name already exists.")
                            else:
                                if bin_method == "Equal Width":
                                    df[new_bin_column] = pd.cut(df[bin_column], bins=bin_count)
                                else:
                                    df[new_bin_column] = pd.qcut(df[bin_column], q=bin_count, duplicates="drop")

                                st.session_state.working_df = df
                                st.session_state.transform_log.append({
                                    "step": "Numeric column binned",
                                    "source_column": bin_column,
                                    "new_column": new_bin_column,
                                    "bin_method": bin_method,
                                    "bin_count": int(bin_count)
                                })
                                st.rerun()

                        except Exception as e:
                            st.error(f"Binning failed: {e}")
                else:
                    st.info("No numeric columns available for binning.")

        with tab7:

            st.info(
                "Run validation checks for numeric ranges, allowed category values, and required non-null fields.")

            st.subheader("Data Validation Rules")

            validation_action = st.selectbox(
                "Choose validation rule",
                [
                    "Numeric Range Check",
                    "Allowed Categories Check",
                    "Non-Null Check"
                ],
                key="validation_action"
            )

            if validation_action == "Numeric Range Check":
                numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()

                if numeric_columns:
                    validation_column = st.selectbox(
                        "Select numeric column",
                        numeric_columns,
                        key="validation_numeric_column"
                    )

                    min_value = st.number_input(
                        "Minimum allowed value",
                        value=float(df[validation_column].min()) if not df[validation_column].dropna().empty else 0.0,
                        key="validation_min_value"
                    )

                    max_value = st.number_input(
                        "Maximum allowed value",
                        value=float(df[validation_column].max()) if not df[validation_column].dropna().empty else 0.0,
                        key="validation_max_value"
                    )

                    if st.button("Run Numeric Range Validation"):
                        violations_df = df[
                            (df[validation_column] < min_value) | (df[validation_column] > max_value)
                            ].copy()

                        st.write("Violations Table")
                        st.dataframe(violations_df)

                        st.session_state.transform_log.append({
                            "step": "Numeric range validation run",
                            "column": validation_column,
                            "min_value": float(min_value),
                            "max_value": float(max_value),
                            "violations_count": int(len(violations_df))
                        })

                else:
                    st.info("No numeric columns available for numeric validation.")


            elif validation_action == "Allowed Categories Check":
                categorical_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()

                if categorical_columns:
                    validation_column = st.selectbox(
                        "Select categorical column",
                        categorical_columns,
                        key="validation_category_column"
                    )

                    allowed_values_text = st.text_area(
                        "Enter allowed categories (one per line)",
                        key="allowed_values_text"
                    )

                    if st.button("Run Allowed Categories Validation"):
                        allowed_values = [
                            value.strip() for value in allowed_values_text.splitlines() if value.strip() != ""
                        ]

                        violations_df = df[
                            ~df[validation_column].isin(allowed_values) & df[validation_column].notna()
                            ].copy()

                        st.write("Violations Table")
                        st.dataframe(violations_df)

                        st.session_state.transform_log.append({
                            "step": "Allowed categories validation run",
                            "column": validation_column,
                            "allowed_values": allowed_values,
                            "violations_count": int(len(violations_df))
                        })

                else:
                    st.info("No categorical columns available for category validation.")


            elif validation_action == "Non-Null Check":
                validation_columns = st.multiselect(
                    "Select columns that must not be null",
                    options=df.columns.tolist(),
                    key="nonnull_columns"
                )

                if st.button("Run Non-Null Validation"):
                    if not validation_columns:
                        st.error("Please select at least one column.")
                    else:
                        violations_df = df[df[validation_columns].isnull().any(axis=1)].copy()

                        st.write("Violations Table")
                        st.dataframe(violations_df)

                        st.session_state.transform_log.append({
                            "step": "Non-null validation run",
                            "columns": validation_columns,
                            "violations_count": int(len(violations_df))
                        })

            validation_export_df = None

            if validation_action == "Numeric Range Check" and "violations_df" in locals():
                validation_export_df = violations_df
            elif validation_action == "Allowed Categories Check" and "violations_df" in locals():
                validation_export_df = violations_df
            elif validation_action == "Non-Null Check" and "violations_df" in locals():
                validation_export_df = violations_df

            if validation_export_df is not None and not validation_export_df.empty:
                csv_data = validation_export_df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="Download Violations Table as CSV",
                    data=csv_data,
                    file_name="validation_violations.csv",
                    mime="text/csv"
                )

        st.subheader("Transformation Log")
        st.dataframe(pd.DataFrame(st.session_state.transform_log))

    else:
        st.info("Please upload a dataset first.")


if page == "Visualization":
    if st.session_state.working_df is not None:
        df = st.session_state.working_df.copy()

        st.subheader("Visualization Builder")
        st.info("Use this page to filter the cleaned dataset and generate charts dynamically.")

        import matplotlib.pyplot as plt
        import plotly.express as px

        filter_columns = st.multiselect(
            "Filter by categorical columns",
            options=df.select_dtypes(include=["object", "category"]).columns.tolist(),
            key="viz_filter_columns"
        )

        filtered_df = df.copy()

        for col in filter_columns:
            selected_values = st.multiselect(
                f"Select values for {col}",
                options=sorted(filtered_df[col].dropna().astype(str).unique().tolist()),
                key=f"filter_values_{col}"
            )
            if selected_values:
                filtered_df = filtered_df[filtered_df[col].astype(str).isin(selected_values)]

        numeric_filter_columns = st.multiselect(
            "Filter by numeric range",
            options=filtered_df.select_dtypes(include=["number"]).columns.tolist(),
            key="viz_numeric_filter_columns"
        )

        for col in numeric_filter_columns:
            col_min = float(filtered_df[col].min())
            col_max = float(filtered_df[col].max())

            if col_min != col_max:
                selected_range = st.slider(
                    f"Select range for {col}",
                    min_value=col_min,
                    max_value=col_max,
                    value=(col_min, col_max),
                    key=f"range_filter_{col}"
                )

                filtered_df = filtered_df[
                    (filtered_df[col] >= selected_range[0]) &
                    (filtered_df[col] <= selected_range[1])
                ]

        st.write("Filtered dataset preview")
        st.dataframe(filtered_df)
        st.write("Number of row in the table", filtered_df.shape[0])

        plot_type = st.selectbox(
            "Choose plot type",
            [
                "Histogram",
                "Box Plot",
                "Scatter Plot",
                "Line Chart",
                "Bar Chart",
                "Correlation Heatmap"
            ],
            key="plot_type"
        )

        numeric_columns = filtered_df.select_dtypes(include=["number"]).columns.tolist()
        categorical_columns = filtered_df.select_dtypes(include=["object", "category"]).columns.tolist()
        datetime_columns = filtered_df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns.tolist()
        all_columns = filtered_df.columns.tolist()

        if plot_type == "Histogram":
            if numeric_columns:
                x_col = st.selectbox("Select numeric column", numeric_columns, key="hist_x")

                if st.button("Generate Histogram"):
                    fig = px.histogram(
                        filtered_df,
                        x=x_col,
                        nbins=20,
                        title=f"Histogram of {x_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No numeric columns available for histogram.")

        elif plot_type == "Box Plot":
            if numeric_columns:
                y_col = st.selectbox("Select numeric column", numeric_columns, key="box_y")

                if st.button("Generate Box Plot"):
                    fig = px.box(
                        filtered_df,
                        y=y_col,
                        title=f"Box Plot of {y_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No numeric columns available for box plot.")

        elif plot_type == "Scatter Plot":
            if len(numeric_columns) >= 2:
                x_col = st.selectbox("Select X column", numeric_columns, key="scatter_x")
                y_col = st.selectbox("Select Y column", numeric_columns, key="scatter_y")
                color_col = st.selectbox(
                    "Optional group/color column",
                    ["None"] + categorical_columns,
                    key="scatter_color"
                )

                if st.button("Generate Scatter Plot"):
                    if color_col != "None":
                        fig = px.scatter(
                            filtered_df,
                            x=x_col,
                            y=y_col,
                            color=color_col,
                            title=f"{y_col} vs {x_col}"
                        )
                    else:
                        fig = px.scatter(
                            filtered_df,
                            x=x_col,
                            y=y_col,
                            title=f"{y_col} vs {x_col}"
                        )

                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("At least two numeric columns are needed for a scatter plot.")

        elif plot_type == "Line Chart":
            if numeric_columns and (datetime_columns or all_columns):
                x_options = datetime_columns if datetime_columns else all_columns
                x_col = st.selectbox("Select X column", x_options, key="line_x")
                y_col = st.selectbox("Select Y column", numeric_columns, key="line_y")
                color_col = st.selectbox(
                    "Optional group/color column",
                    ["None"] + categorical_columns,
                    key="line_color"
                )

                if st.button("Generate Line Chart"):
                    plot_df = filtered_df[[x_col, y_col] + ([color_col] if color_col != "None" else [])].dropna()
                    plot_df = plot_df.sort_values(by=x_col)

                    if color_col != "None":
                        fig = px.line(
                            plot_df,
                            x=x_col,
                            y=y_col,
                            color=color_col,
                            title=f"{y_col} over {x_col}"
                        )
                    else:
                        fig = px.line(
                            plot_df,
                            x=x_col,
                            y=y_col,
                            title=f"{y_col} over {x_col}"
                        )

                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Suitable columns are not available for a line chart.")

        elif plot_type == "Bar Chart":
            if categorical_columns or all_columns:
                x_col = st.selectbox(
                    "Select category column",
                    categorical_columns if categorical_columns else all_columns,
                    key="bar_x"
                )

                aggregation = st.selectbox(
                    "Select aggregation",
                    ["count", "sum", "mean", "median"],
                    key="bar_agg"
                )

                y_col = None
                if aggregation != "count":
                    if numeric_columns:
                        y_col = st.selectbox("Select numeric column", numeric_columns, key="bar_y")
                    else:
                        st.warning("Numeric column required for this aggregation.")

                top_n = st.number_input(
                    "Top N categories",
                    min_value=1,
                    value=10,
                    step=1,
                    key="bar_top_n"
                )

                color_col = st.selectbox(
                    "Optional group/color column",
                    ["None"] + categorical_columns,
                    key="bar_color"
                )

                if st.button("Generate Bar Chart"):
                    if aggregation == "count":
                        if color_col != "None" and color_col != x_col:
                            plot_df = (
                                filtered_df.groupby([x_col, color_col])
                                .size()
                                .reset_index(name="value")
                            )

                            top_categories = (
                                filtered_df[x_col].value_counts().head(top_n).index.tolist()
                            )
                            plot_df = plot_df[plot_df[x_col].isin(top_categories)]

                            fig = px.bar(
                                plot_df,
                                x=x_col,
                                y="value",
                                color=color_col,
                                barmode="group",
                                title=f"Count by {x_col}"
                            )
                        else:
                            plot_df = filtered_df[x_col].value_counts().head(top_n).reset_index()
                            plot_df.columns = [x_col, "value"]

                            fig = px.bar(
                                plot_df,
                                x=x_col,
                                y="value",
                                title=f"Count by {x_col}"
                            )
                    elif y_col is not None:
                        if color_col != "None" and color_col != x_col:
                            plot_df = (
                                filtered_df.groupby([x_col, color_col])[y_col]
                                .agg(aggregation)
                                .reset_index(name="value")
                            )

                            top_categories = (
                                filtered_df.groupby(x_col)[y_col]
                                .agg(aggregation)
                                .sort_values(ascending=False)
                                .head(top_n)
                                .index.tolist()
                            )
                            plot_df = plot_df[plot_df[x_col].isin(top_categories)]

                            fig = px.bar(
                                plot_df,
                                x=x_col,
                                y="value",
                                color=color_col,
                                barmode="group",
                                title=f"{aggregation.title()} of {y_col} by {x_col}"
                            )
                        else:
                            plot_df = (
                                filtered_df.groupby(x_col)[y_col]
                                .agg(aggregation)
                                .sort_values(ascending=False)
                                .head(top_n)
                                .reset_index(name="value")
                            )

                            fig = px.bar(
                                plot_df,
                                x=x_col,
                                y="value",
                                title=f"{aggregation.title()} of {y_col} by {x_col}"
                            )
                    else:
                        fig = None

                    if fig is not None:
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No suitable columns available for bar chart.")

        elif plot_type == "Correlation Heatmap":
            if len(numeric_columns) >= 2:
                corr = filtered_df[numeric_columns].corr()

                if st.button("Generate Correlation Heatmap"):
                    fig, ax = plt.subplots()
                    cax = ax.imshow(corr, aspect="auto")
                    ax.set_xticks(range(len(corr.columns)))
                    ax.set_yticks(range(len(corr.columns)))
                    ax.set_xticklabels(corr.columns, rotation=45, ha="right")
                    ax.set_yticklabels(corr.columns)
                    ax.set_title("Correlation Heatmap")
                    fig.colorbar(cax)
                    st.pyplot(fig)
            else:
                st.warning("At least two numeric columns are needed for a heatmap.")
    else:
        st.info("Please upload a dataset first.")


if page == "Export & Report":
    if st.session_state.working_df is not None:
        df = st.session_state.working_df.copy()

        st.subheader("Export & Report")
        st.info("Use this page to download the cleaned dataset, transformation log, and reproducible recipe.")

        st.write("Cleaned Dataset Preview")
        st.dataframe(df.head())

        st.write("Dataset Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])
        col3.metric("Transformations Logged", len(st.session_state.transform_log))

        st.write("Transformation Log")
        if st.session_state.transform_log:
            log_df = pd.DataFrame(st.session_state.transform_log)
            st.dataframe(log_df)
        else:
            log_df = pd.DataFrame()
            st.info("No transformations have been logged yet.")

        cleaned_csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Cleaned Dataset (CSV)",
            data=cleaned_csv,
            file_name="cleaned_dataset.csv",
            mime="text/csv"
        )

        try:
            import io

            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="CleanedData")
            excel_data = excel_buffer.getvalue()

            st.download_button(
                label="Download Cleaned Dataset (Excel)",
                data=excel_data,
                file_name="cleaned_dataset.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.warning(f"Excel export is unavailable: {e}")

        if not log_df.empty:
            log_csv = log_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download Transformation Report (CSV)",
                data=log_csv,
                file_name="transformation_report.csv",
                mime="text/csv"
            )

        import json
        from datetime import datetime

        recipe = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "steps": st.session_state.transform_log
        }

        recipe_json = json.dumps(recipe, indent=4, default=str)

        st.download_button(
            label="Download Recipe (JSON)",
            data=recipe_json,
            file_name="transformation_recipe.json",
            mime="application/json"
        )

    else:
        st.info("Please upload a dataset first.")