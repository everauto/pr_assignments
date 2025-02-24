import pandas as pd
import os

ATTACHEMNT_FOLDER = r"J:\Admin & Plans Unit\Recovery Systems\2. Reports\4. Data Files\FLPA Accounts Export"


def find_bad_data(attachment_folder):
    fileNames=[]
    for file in os.listdir(attachment_folder):
        fileNames.append(file)
    sorted_file_names = sorted(fileNames, reverse=True)

    filename =  attachment_folder+"/"+sorted_file_names[0]

    # with open(filename, 'rb') as file:
    #     for line_number, line in enumerate(file):
    #         try:
    #             line.decode('utf-8')
    #         except UnicodeDecodeError as e:
    #             print(f"Error decoding line {line_number}: {e}")
    #             print()
    #             break


    try:
        df = pd.read_csv(filename, encoding='ISO-8859-1')
        print("File read successfully with ISO-8859-1 encoding.")
    except Exception as e:
        print(f"Unable to load CSV file: {e}")

    # Search for characters that might be problematic:
    for col in df.columns:
        for index, value in df[col].iteritems():
            if isinstance(value, str):  # Only try to encode strings
                try:
                    value.encode('utf-8')
                except UnicodeEncodeError:
                    print(f"Problematic value found at Row {index}, Column '{col}': {value}")

find_bad_data(ATTACHEMNT_FOLDER)