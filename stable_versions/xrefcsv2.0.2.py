# Version 2.0.2.1 (2.0.2) release: 7/18/2024 | Last edit: 7/22/24
# Built by cdUAH
# Cleaned 3/20/25

import os
import platform
import pandas as pd
import tkinter as tk
from importlib.metadata import version
from tkinter import filedialog
from datetime import datetime


def checkversions():
    xrefvers = '2.0.2'
    print('*' * 40)
    print(f"$ Checking Python and module versions {'|':>2}")
    pdver = version('pandas')
    pyver = platform.python_version()
    print(f"$ Running xrefcsv {xrefvers} {'|':>16}\n"
          f"$ Running Pandas {pdver} {'|':>17}\n"
          f"$ Running Python {pyver} {'|':>16}")
    print('*' * 40 + '\n')


def xrefcsv():
    def to_epoch(s):
        # This function pulls the string date time from the dataframe and converts it to an epoch
        try:
            s = s.replace('000 UTC', '').strip()  # removes stuff not needed
            dt = datetime.strptime(s, '%Y/%j:%H:%M:%S.%f')  # date format of embedded time string pulled as int
            return dt.timestamp()  # returns date time converted to epoch
        except AttributeError:  # this can be caused if Embedded time appears as zero. Temporary solution
            print("Epoch Conversion Error")
            return 0

    # define nested functions
    def makedir(v):
        # Creates the directory to hold the outputs. Called twice, once for each file
        try:
            dirname = f'./{v}outputfiles'  # generates directory name
            os.makedirs(dirname)
            return dirname
        except FileExistsError:
            overwrite = input("$ Output directory already exists. Do you want to overwrite? (y/n):\n>>> ").lower()
            if overwrite == 'y':
                dirname = f'./{v}outputfiles'  # generates directory name
                os.makedirs(dirname, exist_ok=True)
                return dirname
            if overwrite == 'n':
                input("$ Exiting. Press any key to continue")
                quit()

    def select_file(i):
        # Code that lets the user select each file in file explorer
        if i == 0:  # file one
            print(f"$ Choose a Pre Firewall CSV. It must be in the same directory as {os.path.basename(__file__)}")
            diatitle = 'Choose a Pre Firewall CSV'
        if i == 1:  # file two
            print(f"$ Choose a Post Firewall CSV. It must be in the same directory as {os.path.basename(__file__)}")
            diatitle = 'Choose a Post Firewall CSV'
        root = tk.Tk()
        root.withdraw()  #not sure why, but recommended as a best practice for working with tkinter
        file_types = [('CSV Files', '*.csv'), ('All Files', '*.*')]  # Defaults to showing CSV files
        initial_dir = os.getcwd()  # ensures it opens in the present/current working directory
        file_selected = filedialog.askopenfilename(filetypes=file_types,
                                                   defaultextension=".csv",
                                                   initialdir=initial_dir,
                                                   title=diatitle)
        root.destroy()
        return os.path.basename(file_selected)

    def custom_range():
        while True:
            try:
                # This function provides the user the capability to select a time range to closer inspect.
                time_range_input_start = str(input("$ Enter the start of range formatted as 'YYYY-DDD.HH:MM:SS': "
                                                   "\n>>> "))
                time_range_input_end = str(input("$ Enter the end of range formatted as 'YYYY-DDD.HH:MM:SS': "
                                                 "\n>>> "))
                print(f"$ Range is: {time_range_input_start} - {time_range_input_end}")
                print("Converting to Epoch")
                # below is the same code used in to_epoch(), but adjusted for the input format from 
                dt_s = datetime.strptime(time_range_input_start, '%Y-%j.%H:%M:%S')  # change depending on []
                dt_s = dt_s.timestamp()
                dt_e = datetime.strptime(time_range_input_end, '%Y-%j.%H:%M:%S')  # change depending on []
                dt_e = dt_e.timestamp()
                print(f"Start Epoch: {dt_s}\nEnd Epoch: {dt_e}")
                return [dt_s, dt_e]
            except ValueError as error:
                print(f"$ ERROR! '{error}'\n$ Please ensure the format is 'YYYY-DDD.HH:MM:SS'\n")
            except TypeError as error:
                print(f"$ {error}\n$ Please ensure the format is 'YYYY-DDD.HH:MM:SS'")

    testver = input("$ Name to append to each file: \n"
                    "$ (E.g. 1_1_1970, etc)\n>>> ") + "_"
    # new in 2.0.2. Allows user to set a custom range. Will print full range and custom range as 2 separate files
    time_range_bool = str(input("$ Would you like to enter a custom range of values to inspect? (y/n): "))
    if time_range_bool.lower() == "y":
        time_range_bool = 1
        custom_range_list = custom_range()
        custom_start = custom_range_list[0]
        custom_end = custom_range_list[1]
    elif time_range_bool.lower() == "n":
        time_range_bool = 0
    while True:
        try:
            n = 0  # constant for select_file to know if pre or post is being passed. I'm sure there's another way...
            csv_input_pre = select_file(n)  # calls select_file
            n += 1
            print(csv_input_pre)
            outfile1 = testver + csv_input_pre + ".csv"
            df1 = pd.read_csv(csv_input_pre)
            path = f'{makedir(testver)}\\'  # creates new directory in PWD to store outputs
            df1 = df1.drop(columns=['Destination Port', 'APID', 'Info', 'Length'], errors='ignore')  # drop extras
            df1['Embedded Time (Epoch)'] = df1['Embedded Time'].apply(to_epoch)  # Creates epoch of embedded time
            df1['SeqNum_Adjust'] = df1['Sequence Number'] - df1['Sequence Number'].shift(1)  # a = n-(n-1)
            df1 = df1[df1.SeqNum_Adjust != 0]  # remove dupes
            df1.to_csv(path + outfile1, index=False)  # writes to created directory
            if time_range_bool == 1:
                df1_custom = df1[(df1['Embedded Time (Epoch)'] >= custom_start)
                                 & (df1['Embedded Time (Epoch)'] <= custom_end)]
                df1_custom.to_csv(path + "customRange_" + outfile1)
            print(f"$ New file created as: {path + outfile1}")
            break
        except FileNotFoundError as error:  # if filename is incorrect
            print(f"$ {error}\n$ Ensure the selected CSV is in your PWD: ({os.path.abspath('./')})\n")
            leave = str(input("$ To exit the program, enter 'y'\n"
                              "$ To try again, press any other key\n>>> "))
            if leave.lower() == 'y':
                exit()
            else:
                continue
        except PermissionError as error:  # if permission is denied
            print(f"$ {error}\n$ Check that your file isn't open in another program (e.g. Excel)\n")
        except Exception as error:  # catches other errors just in case one appears
            print(f"$ {error}\n$ There was an unexpected error. Exiting!")
            quit()

    while True:
        try:
            csv_input_post = select_file(n)
            print(csv_input_post)
            outfile2 = testver + csv_input_post + ".csv"
            df2 = pd.read_csv(csv_input_post)
            df2 = df2.drop(columns=['Destination Port', 'APID', 'Info', 'Length'], errors='ignore')
            df2['Embedded Time (Epoch)'] = df2['Embedded Time'].apply(to_epoch)  # Creates epoch of embedded time
            df2['SeqNum_Adjust'] = df2['Sequence Number'] - df2['Sequence Number'].shift(1)
            df2 = df2[df2.SeqNum_Adjust != 0]  # remove dupes
            df2.to_csv(path + outfile2, index=False)  # writes to created directory
            if time_range_bool == 1:
                df2_custom = df2[(df2['Embedded Time (Epoch)'] >= custom_start)
                                 & (df2['Embedded Time (Epoch)'] <= custom_end)]
                df2_custom.to_csv(path + "customRange_" + outfile2)
            print(f"$ New file created as: {path + outfile2}")
            break
        except FileNotFoundError as error:  # if filename is incorrect
            print(f"$ {error}\n$ Ensure the selected CSV is in your PWD: ({os.path.abspath('./')})\n")
            leave = str(input("$ To exit the program, enter 'y'\n"
                              "$ To try again, press any other key\n>>> "))
            if leave.lower() == 'y':
                exit()
            else:
                continue
        except PermissionError as error:  # if permission is denied
            print(f"$ {error}\n$ Check that your CSV isn't open in another program (e.g. Excel)\n")
        except Exception as error:  # catches other errors just in case one appears
            print(f"$ {error}\n$ There was an unexpected error. Exiting!")
            quit()

    # filter out the loose change 0s in VCDU so overlap isn't messed up
    df1_non_zero, df2_non_zero = df1[df1['Embedded Time (Epoch)'] != 0], df2[df2['Embedded Time (Epoch)'] != 0]
    #print("$ Zero out completed")   # troubleshooting code

    # finds overlap range by first by taking the highest of the minimums, and then the lowest of the maximums
    overlap_min = max(df1_non_zero['Embedded Time (Epoch)'].min(), df2_non_zero['Embedded Time (Epoch)'].min())
    overlap_max = min(df1_non_zero['Embedded Time (Epoch)'].max(), df2_non_zero['Embedded Time (Epoch)'].max())
    print(f"$ Overlap range determined (Epoch): {overlap_min} - {overlap_max}")

    # cuts the files to match the range determined above. Only the values between min and max are kept
    df1_filtered = df1[(df1['Embedded Time (Epoch)'] >= overlap_min)
                       & (df1['Embedded Time (Epoch)'] <= overlap_max)]
    df2_filtered = df2[(df2['Embedded Time (Epoch)'] >= overlap_min)
                       & (df2['Embedded Time (Epoch)'] <= overlap_max)]
    #print("$ Cut files successfully")  # troubleshooting code

    # slaps the 2 files together into 1
    df3 = (pd.concat([df1_filtered, df2_filtered], ignore_index=True, sort=False))  # merges both files into one
    #print(f"$ Merged files together")  # troubleshooting code

    # Drops all duplicates where VCDU Sequence Number and SeqNum match.
    # This will need to be changed. It is the only legacy VCDU unit. Need a better way to filter out duplicates
    df3 = df3.drop_duplicates(subset=['VCDU Sequence Number', 'SeqNum_Adjust'], keep=False)
    df3 = df3[df3['SeqNum_Adjust'] > 1]  # TEMPORARY SOLUTION
    # The above serves as a temporary solution. There could be a case where a sequence
    # number of 1 could show up, and it indicates an issue somewhere within the process. For now however,
    # this works to give us only the results where packets are lost and noted (SeqNum_adjust > 1)
    out = f"{testver}outfile.csv"
    df3.to_csv(path + out, index=False)
    if time_range_bool == 1:  # allows for custom time ranges. If user skips, then this does not apply
        df3_custom = df3[(df3['Embedded Time (Epoch)'] >= custom_start)
                         & (df3['Embedded Time (Epoch)'] <= custom_end)]
        df3_custom.to_csv(path + "customRange_" + out, index=False)
    print(f"$ Success!\n$ Output created as {path + out}")
    input("\n$ Press any key to finish\n")
    quit()


#  driver
def main():
    checkversions()
    xrefcsv()


if __name__ == '__main__':
    main()
