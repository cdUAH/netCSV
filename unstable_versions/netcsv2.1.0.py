# Version 2.1 release: N/A | Last edit 2/26/25
# Built by cdUAH
# Cleaned 3/20/25
# UNSTABLE. SHOULD RUN FOR MOST ITEMS, BUT THERE ARE EDGE CASES THAT I HAVE NOT TESTED

# imports
import os
import platform
import tkinter as tk
from datetime import datetime
from importlib.metadata import version
from tkinter import filedialog
import pandas as pd

# options
pd.options.mode.chained_assignment = None  # disables SettingWithCopyWarning thrown during Szudziks Pairing


# Globals
error_counter = 0


def checkversions():
    # Checks the current versions for the main packages and python version
    netcsvver = '2.1.0 (UNSTABLE)'
    print('*' * 40)
    print(f"$ Checking Python and module versions {'|':>2}")
    pdver = version('pandas')
    pyver = platform.python_version()
    print(f"$ Running netcsv {netcsvver} {'|':>6}\n"
          f"$ Running Pandas {pdver} {'|':>17}\n"
          f"$ Running Python {pyver} {'|':>16}")
    print('*' * 40 + '\n')



def netcsv():
    # main code
    def to_epoch(s):
        # This function pulls the string date time from the dataframe and converts it to an epoch. datetime.strptime
        # requires specific formatting. THis can be easily edited, just refer to python docs re: datetime
        # in order to ensure it is correct

        try:
            s = s.replace('000 UTC', '').strip()  # removes stuff not needed
            dt = datetime.strptime(s, '%Y/%j:%H:%M:%S.%f')  # date format of embedded time string pulled as int
            return dt.timestamp()  # returns date time converted to epoch
        except AttributeError:  # this can be caused if Embedded time appears as zero. Temporary solution
            global error_counter
            error_counter += 1
            print("$ Epoch Conversion Error. Probable un-decoded file."
                  " This could be a retransmit over alternative port")
            return 0

    def makedir(v):
        # Creates the directory to hold the outputs
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
        # Code that lets the user select each file in file explorer. Uses tkinter. Uses simple logic passed from
        # function call (i) to determine which string names to use, depending on if d1 or d2 is being called
        defaultextension_mod = ".csv"  # modifies the default filetype displayed based on csv or txt
        diatitle = ""
        if i == 0:  # file one
            print(f"$ Choose a Pre Firewall CSV. It must be in the same directory as {os.path.basename(__file__)}")
            diatitle = 'Choose a Pre Firewall CSV'
        if i == 1:  # file two
            print(f"$ Choose a Post Firewall CSV. It must be in the same directory as {os.path.basename(__file__)}")
            diatitle = 'Choose a Post Firewall CSV'
        if i == 2:  # single file analysis
            print(f"$ Choose a CSV file with missing sequence numbers. It must be in the same directory as "
                  f"{os.path.basename(__file__)}")
            diatitle = 'Choose a standalone CSV'
        root = tk.Tk()
        root.withdraw()  # not sure why, but recommended as a best practice for working with tkinter
        # ^^^ must be removed to run tkinter in pycharm. No issues when running on system or as exe
        file_types = [('CSV Files', '*.csv'), ('All Files', '*.*')]  # Defaults to showing CSV files
        initial_dir = os.getcwd()  # ensures it opens in the present/current working directory
        file_selected = filedialog.askopenfilename(filetypes=file_types,
                                                   defaultextension=defaultextension_mod,
                                                   initialdir=initial_dir,
                                                   title=diatitle)
        root.destroy()
        return os.path.basename(file_selected)

    def custom_range():
        # allows the user to define a specific range. The program will output the entire formatting as well, but will
        # also generate 3 additional files (one for d1, d2, and d3) with only the time range determined. THis means that
        # The program will still process everything, so no reduction in time or complexity is acquired from this
        # process
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
                dt_s = datetime.strptime(time_range_input_start, '%Y-%j.%H:%M:%S')  # change depending on 
                dt_s = dt_s.timestamp()
                dt_e = datetime.strptime(time_range_input_end, '%Y-%j.%H:%M:%S')  # change depending on 
                dt_e = dt_e.timestamp()
                return [dt_s, dt_e]
            except ValueError as error:
                print(f"$ ERROR! '{error}'\n$ Please ensure the format is 'YYYY-DDD.HH:MM:SS'\n")
            except TypeError as error:
                print(f"$ {error}\n$ Please ensure the format is 'YYYY-DDD.HH:MM:SS'")

    def szudzik_pairing(x, y):
        # Szudzik's Elegant Pair function. The result of 2 values is entirely unique.
        # this function is called both for the initial file on single analysis and df1. The result is
        # pi: N\ X N\ -> N\ bijection
        # Warning this function will throw a SettingWithCopyWarning. It is currently disabled, however it may end up
        # causing an issue in the future. If you want to figure out why, remove the set option after imports
        return (x * x) + x + y if x >= y else (y * y) + x

    def txt_reader(path_usercsv):  # added in 2.0.3
        # below reads a user-made csv file from copy-paste email. column 12 = seqnum || column 14 = diff
        df_disclosed = pd.read_csv(path_usercsv, header=None, sep="\\s+", dtype={12: int})
        # need to modify the dataframe a bit
        df_disclosed[14] = df_disclosed[14].str.replace(')', '')  # drops column14's (diff) ')'
        df_disclosed[14] = df_disclosed[14].astype('int')  # changes column21 to being an int
        zipd_reader = zip(df_disclosed[12], df_disclosed[14])
        df_disclosed['szudziks_pair'] = [szudzik_pairing(val1, val2) for val1, val2 in zipd_reader]
        missingSN_list = df_disclosed['szudziks_pair'].to_list()
        return missingSN_list

    def menu():
        while True:
            choice = input("\n"
                           "$ Please enter what you would like to do next:\n"
                           "$ 1: Pre/Post Analysis (Limited)\n"
                           "$ 2: Pre/Post Analysis (Full)\n"
                           "$ 3: Single Analysis\n"
                           "$ 4: Filter (Remove all seqnum = 1)\n"
                           "$ 0: Exit\n"
                           ">>> ")
            match choice:
                case '1':
                    print("$ Running Pre/Post (Limited)")
                    return choice
                case '2':
                    print("$ Running Pre/Post (Full)")
                    return choice
                case '3':
                    print("$ Running Single Analysis")
                    return choice
                case '4':
                    print("$ Running Filter")
                    return choice
                case '0':
                    print("$ Exiting!")
                    quit()
                case _:  # default value
                    print("$ Invalid Option, please choose again")
                    #return choice

########################################################################################################################
################################################ Start of Main #########################################################
########################################################################################################################


    testver = input("$ Name to append to each file: \n"
                    "$ (E.g. 1_1_1970, etc)\n>>> ") + "_"
    # new in 2.0.2. Allows user to set a custom range. Will print full range and custom range as 2 separate files.
    # removed in 2.0.3 due to lack of integration and actual use. Might incorporate into a later version

    # time_range_bool = str(input("$ Would you like to enter a custom range of values to inspect? (y/n): "))



    # if menu() == 1:
    #     time_range_bool = 'y'

    time_range_bool = 'n'  # set as constant as removal for now starting on version 2.0.3
    if time_range_bool.lower() == 'y':
        time_range_bool = 1
        custom_range_list = custom_range()
        custom_start = custom_range_list[0]
        custom_end = custom_range_list[1]
    elif time_range_bool.lower() == 'n':
        time_range_bool = 0

    while True:
        try:
            n = 0  # constant for select_file to know if pre or post is being passed. I'm sure there's another way...
            csv_input_pre = select_file(n)  # calls select_file
            n += 1
            print("$ File selected: " + csv_input_pre)
            outfile1 = testver + csv_input_pre
            df1 = pd.read_csv(csv_input_pre)
            path = f'{makedir(testver)}\\'  # creates new directory in PWD to store outputs
            df1 = df1.drop(columns=['Destination Port', 'APID', 'Info', 'Length'], errors='ignore')  # drop extras
            df1['Embedded Time (Epoch)'] = df1['Embedded Time'].apply(to_epoch)  # Creates epoch of embedded time
            global error_counter  # call on global
            print(f"\n$ Total Errors: {error_counter}")
            error_counter = 0  # reset error counter
            df1['SeqNum_Adjust'] = df1['Sequence Number'] - df1['Sequence Number'].shift(1)  # a = n-(n-1)


            #below must be disabled for current troubleshooting of dupe packets.
            #df1 = df1[df1.SeqNum_Adjust != 0]  # remove dupes


            df1.to_csv(path + outfile1, index=False)  # writes to created directory
            if time_range_bool == 1:
                df1_custom = df1[(df1['Embedded Time (Epoch)'] >= custom_start)
                                 & (df1['Embedded Time (Epoch)'] <= custom_end)]
                df1_custom.to_csv(path + "customRange_" + outfile1)
            print(f"$ New file created as: {path + outfile1}")
            break
        except FileNotFoundError as error:  # if filename is incorrect
            print(f"$ {error}\n$ Ensure the selected CSV is in your PWD: ({os.path.abspath('testing/')})\n")
            leave = str(input("$ To exit the program, enter 'y'\n"
                              "$ To try again, press enter\n>>> "))
            if leave.lower() == 'y':
                exit()
            else:
                continue
        except PermissionError as error:  # if permission is denied
            print(f"$ {error}\n$ Check that your file isn't open in another program (e.g. Excel)\n")
        except Exception as error:  # catches other errors just in case one appears
            print(f"$ {error}\n$ There was an unexpected error. Exiting!")
            quit()

    donext = menu()  # determines single or second analysis

    if donext == '1' or donext == '2':
        while True:
            try:
                csv_input_post = select_file(n)
                print("$ File selected: " + csv_input_post)
                outfile2 = testver + csv_input_post
                df2 = pd.read_csv(csv_input_post)
                df2 = df2.drop(columns=['Destination Port', 'APID', 'Info', 'Length'], errors='ignore')
                df2['Embedded Time (Epoch)'] = df2['Embedded Time'].apply(to_epoch)  # Creates epoch of embedded time
                print(f"\n$ Total Errors: {error_counter}")
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
                print(f"$ {error}\n$ Ensure the selected CSV is in your PWD: ({os.path.abspath('testing/')})\n")
                leave = str(input("$ To exit the program, enter 'y'\n"
                                  "$ To try again, press enter\n>>> "))
                if leave.lower() == 'y':
                    exit()
                else:
                    continue
            except PermissionError as error:  # if permission is denied
                print(f"$ {error}\n$ Check that your CSV isn't open in another program (e.g. Excel)\n")
            except Exception as error:  # catches other errors just in case one appears
                print(f"$ {error}\n$ There was an unexpected error. Exiting!")
                quit()
    elif donext == '3':
        while True:
            try:
                n = 2
                filepath = select_file(n)  # get directions to the path of the txt
                disclosed_list = txt_reader(filepath)
                df1_algd = df1
                df1_algd['SeqNum-1'] = df1_algd['SeqNum_Adjust'] - 1  # filters all non-cared (diff 1/0)
                df1_algd = df1_algd[df1_algd['SeqNum-1'] > 0]  # pt 2 of filtering (removes all 0s out)
                zipd_main = zip(df1_algd['Sequence Number'], df1_algd['SeqNum-1'])
                df1_algd['Szudziks Pair'] = [szudzik_pairing(val1, val2) for val1, val2 in zipd_main]
                mask = df1_algd['Szudziks Pair'].isin(disclosed_list)  # the actual filter
                df1_remaining = df1_algd[~mask]  # any NOT in the mask are left
                print("$ Szudzik Pair filter complete")
                print(f"$ A total of: ({len(df1_remaining)}) rows were found in {csv_input_pre}, and not reported in "
                      f"user-generated file: {filepath}")
                see_results = input("\n$ Enter 'y' if you would like to see them: ")
                if see_results.lower() == 'y':
                    print(df1_remaining.to_string(index=False))
                out = f"{testver}szudzikoutfile.csv"
                df1_remaining.to_csv(path + out, index=False)
                print(f"$ Output created as {path + out}")
                input("\n$ Press enter to finish\n")
                quit()
            except FileNotFoundError as error:  # if filename is incorrect
                print(f"$ {error}\n$ Ensure the selected CSV is in your PWD: ({os.path.abspath('testing/')})\n")
                leave = str(input("$ To exit the program, enter 'y'\n"
                                  "$ To try again, press enter\n>>> "))
                if leave.lower() == 'y':
                    exit()
                else:
                    continue
            except PermissionError as error:  # if permission is denied
                print(f"$ {error}\n$ Check that your CSV isn't open in another program (e.g. Excel)\n")
            except Exception as error:  # catches other errors just in case one appears
                print(f"$ {error}\n$ There was an unexpected error. Exiting!")
                quit()
    elif donext == '4':
        df1_algd = df1
        df1_algd['SeqNum-1'] = df1_algd['SeqNum_Adjust'] - 1  # filters all non-cared (diff 1/0)
        df1_algd = df1_algd[df1_algd['SeqNum-1'] != 0]  # pt 2 of filtering (removes all 0s out ("normal")
        df1_algd = df1_algd[df1_algd['SeqNum-1'] != -16384]  # pt 3 removes all rollovers
        out = f"{testver}outfile.csv"
        df1_algd.to_csv(path + out, index=False)
        print(f"$ Success!\n$ Output created as {path + out}")
        print(f"$ Total of {len(df1_algd)} rows left")
        input("\n$ Press enter to finish\n")
        quit()



    # filter out the loose change 0s in Epoch so overlap isn't messed up
    df1_non_zero, df2_non_zero = df1[df1['Embedded Time (Epoch)'] != 0], df2[df2['Embedded Time (Epoch)'] != 0]
    # need to change how it filters zeros, based on how the recent GEDI dataloss is appearing. Certain important values
    # can appear as

    # finds overlap range by first by taking the highest of the minimums, and then the lowest of the maximums
    overlap_min = max(df1_non_zero['Embedded Time (Epoch)'].min(), df2_non_zero['Embedded Time (Epoch)'].min())
    overlap_max = min(df1_non_zero['Embedded Time (Epoch)'].max(), df2_non_zero['Embedded Time (Epoch)'].max())
    print(f"$ Overlap range determined (Epoch): {overlap_min} - {overlap_max}")

    # cuts the files to match the range determined above. Only the values between min and max are kept
    df1_filtered = df1[(df1['Embedded Time (Epoch)'] >= overlap_min)
                       & (df1['Embedded Time (Epoch)'] <= overlap_max)]
    df1_filtered.to_csv(path + "filtered_" + outfile1, index=False)  # creates filtered file
    df2_filtered = df2[(df2['Embedded Time (Epoch)'] >= overlap_min)
                       & (df2['Embedded Time (Epoch)'] <= overlap_max)]
    df2_filtered.to_csv(path + "filtered_" + outfile2, index=False)
    # prints out lined up versions of df1 and df2 for analysis reasons.



    # slaps the 2 files together into 1
    df3 = (pd.concat([df1_filtered, df2_filtered], ignore_index=True, sort=False))  # merges both files into one

    # Drops all duplicates where VCDUseqNum and SeqNum match.
    # This will need to be changed. It's the only legacy VCDU unit. Need a better way to filter out duplicates
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
    print(f"$ Total of {len(df3)} discrepancies found")
    input("\n$ Press enter to finish\n")
    quit()



# driver
def main():
    checkversions()
    netcsv()


if __name__ == '__main__':
    main()
