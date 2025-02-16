import os
import duckdb
import pandas as pd

#per chatgpt, used for progress bar estimations below
mimic_table_row_counts = { 
    'ADMISSIONS': 58976,
    'CALLOUT': 34499,
    'CAREGIVERS': 7567,
    'CHARTEVENTS': 330712483,
    'CPTEVENTS': 573146,
    'D_CPT': 134,
    'D_ICD_DIAGNOSES': 14710,
    'D_ICD_PROCEDURES': 3898,
    'D_ITEMS': 12487,
    'D_LABITEMS': 753,
    'DATETIMEEVENTS': 4485937,
    'DIAGNOSES_ICD': 651047,
    'DRGCODES': 125557,
    'ICUSTAYS': 61532,
    'INPUTEVENTS_CV': 17527935,
    'INPUTEVENTS_MV': 3618991,
    'LABEVENTS': 27854055,
    'MICROBIOLOGYEVENTS': 631726,
    'NOTEEVENTS': 2083180,
    'OUTPUTEVENTS': 4349218,
    'PATIENTS': 46520,
    'PRESCRIPTIONS': 4157756,
    'PROCEDUREEVENTS_MV': 258066,
    'PROCEDURES_ICD': 240095,
    'SERVICES': 733241,
    'TRANSFERS': 261897
}

os.chdir("./parquet")

# column look ups for convenience when wanting to see what columns are available in what tables
mimic_columns = dict()
for tbl in mimic_table_row_counts.keys():
    df = pd.read_parquet(f"{tbl}_0.parquet")
    mimic_columns[tbl] = df.columns

del df
# reformat index objects to lists 
mimic_columns = {col: list(mimic_columns[col]) for col in mimic_columns}
# Setup DuckDB helper functions

def table_finder(columns):
    if type(columns) is str:
        columns = [columns]
    for column in columns:
        for table in mimic_columns.keys():
            if column in mimic_columns[table]:
                print(f"{column} found in {table}")
    return None

def table_check():
    def decorator(fnc):
        def wrapper(*args, **kwargs):
            for arg in args:
                if arg not in mimic_columns.keys():
                    raise ValueError(f"'{arg}' is not in the list of MIMIC III tables")
            return fnc(*args, **kwargs)
        return wrapper
    return decorator

# decorator to change anything I am passing a query to be updated with the parquet files
def duckify():
    def decorator(fnc):
        def wrapper(*args, **kwargs):
            #print(*args)
            new_args = []
            for arg in args:
                if type(arg)==str:
                # print(arg)
                    found=False
                    for tbl in mimic_columns.keys():
                        if arg.find(tbl)>-1:
                            #print(f"before {arg=}")
                            arg = arg.replace(tbl, f"'{tbl}*.parquet'")
                            #print(f"after {arg=}")
                            found=True
                    if not found:
                        raise ValueError("Found no table name in the query string")
                new_args.append(arg)
                #print(args)
            return fnc(*new_args, **kwargs)
        return wrapper
    return decorator

@duckify()
def run_query(qry, print_qry=False):
    """
    Run query and return dataframe, or simply print resulting query
    """
    if print_qry:
        print(qry)

    return duckdb.query(qry).to_df()