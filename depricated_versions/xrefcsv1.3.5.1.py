# version 1.3.5.1
# Built 6/24 | Cleaned 3/20/25
# cdUAH
import csv  # used during pcap conversion
import pandas as pd  # used for data manipulation in pcap
import datetime
import multiprocessing
from math import ceil
from scapy.all import *  # scapy for networking interface
from scapy.layers.inet import IP, UDP  # Pull IP from Scapy's layer.inet


# def funcs
###############################################################################################
def startup():
    print("$ BOOTING SCRIPT")
    print("$ Running ", os.path.basename(__file__), " version 1.3.5")  # Prints current file/version
    print('''
$ INSTRUCTIONS: This script will take 2 pcap/ng files, convert to CSV, and cross reference them to find differences
$ To use, enter a "before" pcap or pcapng at the prompt. xrefcsv will convert it to csv. Once completed enter an 
$ "after" pcap or pcapng at the prompt. xrefcsv will convert this to csv. Following both files entered 
$ successfully, xrefcsv will calculate sequence number, and then write any differences out to an output file 'out.csv' 
''')
    global fileamount
    fileamount = str(input("How many files are you testing? "))


global testver
testver = "1351_5"

# def pcap_conv_csvpd():
#     #converts from pcap to a dataframe then exports to csv
#     while True:
#         try:
#             pcap_IN_preFW = input('$ Enter full exact name of PreFW pcap: \n>> ')
#             start = time.time()
#             print(f"Reading in {pcap_IN_preFW} to rdpcap. This may take a while")
#             packets = rdpcap(pcap_IN_preFW)[UDP]
#             print("$ Converting ", pcap_IN_preFW, " from pcap/ng to dataframe")
#             csv_file_pre = pcap_IN_preFW + testver + '.csv'  # appends the csv file extension
#             start_index = 38

def pcap_conv_csv_pre_multi():
    while True:
        try:
            pcap_IN_preFW = input('$ Enter full exact name of PreFW pcap: \n>> ')
            portnum = 000 # enter port num here (CLEANED 3/20/25)
            # Read packets from pcap file
            start = time.time()
            print(f"Reading in {pcap_IN_preFW} to rdpcap. This may take a while")
            packets = rdpcap(pcap_IN_preFW)[UDP]
            print("$ Converting ", pcap_IN_preFW, " from pcap/ng to csv")
            csv_file_pre = pcap_IN_preFW + testver + '.csv'  # appends the csv file extension
            start_index = 38  # enter what byte you want to address in dec (ARRAYS START FROM 0!!!!) also could hex...
            with open(csv_file_pre, 'w', newline='') as csvfile:  # this whole thing does the actual writing
                seen_seqnums = set()
                if len(seen_seqnums) == 0x3FFF:
                    seen_seqnums.clear()  # if 16384 values have been recorded, reset
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["Packet Number [CSV]", "Time", "Epoch", "Epoch Ceil", "Source IP",
                                    "Destination IP", "Sequence Number"])  # What columns?
                for n, pkt in enumerate(packets):
                    raw_bytes = raw(pkt[UDP])  # raw hex
                    byte_sequence = raw_bytes[start_index:start_index + 2]  # index + following x bytes (BIG END)
                    seqnum_hex = int.from_bytes(byte_sequence, byteorder='big')  # converts bytes to ints in BE
                    seqnum_hex = seqnum_hex - 0xC000  # offset for 14 bit usage of seqnum, assuming flag is always 11
                    # if seqnum_hex in seen_seqnums:
                    #     continue
                    seen_seqnums.add(seqnum_hex)
                    if UDP in pkt and pkt.sport == portnum:  # If UDP-type and src portnum
                        timeEPC = float(pkt.time)
                        timeDT = datetime.fromtimestamp(timeEPC).strftime('%Y/%j %H:%M:%S:%f')  # format of time output
                        csvwriter.writerow([n, timeDT, float(pkt.time), math.ceil(float(pkt.time)), pkt[IP].src,
                                            pkt[IP].dst, seqnum_hex])  # columns
                        print(n)
            csvfile.close()  # garbage collection
            end = time.time()
            timetaken = round(end - start, 3)
            print(f"$ SUCCESS!\n$ Created {csv_file_pre} in PWD over: {timetaken} seconds")
            break
        except FileNotFoundError as error:  # if filename is incorrect
            print("$", error, " [CODE 0x0f]\n$ Please make sure you include .pcap or .pcapng\n")
        except PermissionError as error:  # if permission is denied
            print("$", error, " [CODE 0x0a]\n$ Check that your file isn't open in another program (e.g. Excel)\n")
    global global_csvPre  # change globals ASAP
    global_csvPre = csv_file_pre

def pcap_conv_csv_post_multi():
    while True:
        try:
            pcap_IN_postFW = input('$ Enter full exact name of PostFW pcap: \n>> ')
            portnum = 000 portnum = 000 # enter port num here (CLEANED 3/20/25)
            # Read packets from pcap file
            start = time.time()  # time tracker for duration of script
            print(f"Reading in {pcap_IN_postFW} to rdpcap. This may take a while")
            packets = rdpcap(pcap_IN_postFW)[UDP]
            print("$ Converting ", pcap_IN_postFW, " from pcap/ng to csv")
            csv_file_post = pcap_IN_postFW + testver + '.csv'  # appends the csv file extension
            start_index = 38  # enter what byte you want to address (ARRAYS START FROM 0!!!!)
            with open(csv_file_post, 'w', newline='') as csvfile:  # this whole thing does the actual writing
                seen_seqnums = set()
                # if len(seen_seqnums) == 0x3FFF:
                #     seen_seqnums.clear()  # if 16384 values have been recorded, reset
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["Packet Number [CSV]", "Time", "Epoch", "Epoch Ceil", "Source IP",
                                    "Destination IP", "Sequence Number"])  # What columns?
                for n, pkt in enumerate(packets):
                    raw_bytes = raw(pkt[UDP])  # raw hex
                    byte_sequence = raw_bytes[start_index:start_index + 2]  # index + following x bytes (BIG END)
                    seqnum_hex = int.from_bytes(byte_sequence, byteorder='big')  # converts bytes to ints in BE
                    seqnum_hex = seqnum_hex - 0xC000  # offset for 14 bit usage of seqnum, assuming flag is always 11
                    if seqnum_hex in seen_seqnums:
                        continue
                    seen_seqnums.add(seqnum_hex)
                    if UDP in pkt and pkt.sport == portnum:  # If UDP-type
                        timeEPC = float(pkt.time)
                        timeDT = datetime.fromtimestamp(timeEPC).strftime('%Y/%j %H:%M:%S:%f')  # format of time output
                        csvwriter.writerow([n, timeDT, float(pkt.time), math.ceil(float(pkt.time)), pkt[IP].src,
                                            pkt[IP].dst, seqnum_hex])  # columns
                        print(n)
            csvfile.close()  # garbage collection
            end = time.time()
            timetaken = round(end - start, 3)
            print(f"$ SUCCESS!\n$ Created {csv_file_post} in PWD over: {timetaken} seconds")
            break
        except FileNotFoundError as error:  # if filename is incorrect
            print("$", error, " [CODE 0x0f]\n$ Please make sure you include .pcap or .pcapng\n")
        except PermissionError as error:  # if permission is denied
            print("$", error, " [CODE 0x0a]\n$ Check that your file isn't open in another program (e.g. Excel)\n")
    global global_csvPost  # Change globals ASAP
    global_csvPost = csv_file_post

def pcap_conv_csv_pre():
    while True:
        try:
            pcap_IN_preFW = input('$ Enter full exact name of PreFW pcap: \n>> ')
            portnum = 000 # enter port num here (CLEANED 3/20/25)
            # Read packets from pcap file
            start = time.time()
            print(f"Reading in {pcap_IN_preFW} to rdpcap. This may take a while")
            packets = rdpcap(pcap_IN_preFW)[UDP]
            print("$ Converting ", pcap_IN_preFW, " from pcap/ng to csv")
            csv_file_pre = pcap_IN_preFW + testver + '.csv'  # appends the csv file extension
            start_index = 38  # enter what byte you want to address in dec (ARRAYS START FROM 0!!!!) also could hex...
            with open(csv_file_pre, 'w', newline='') as csvfile:  # this whole thing does the actual writing
                seen_seqnums = set()
                if len(seen_seqnums) == 0x3FFF:
                    seen_seqnums.clear()  # if 16384 values have been recorded, reset
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["Packet Number [CSV]", "Time", "Epoch", "Epoch Ceil", "Source IP",
                                    "Destination IP", "Sequence Number"])  # What columns?
                for n, pkt in enumerate(packets):
                    raw_bytes = raw(pkt[UDP])  # raw hex
                    byte_sequence = raw_bytes[start_index:start_index + 2]  # index + following x bytes (BIG END)
                    seqnum_hex = int.from_bytes(byte_sequence, byteorder='big')  # converts bytes to ints in BE
                    seqnum_hex = seqnum_hex - 0xC000  # offset for 14 bit usage of seqnum, assuming flag is always 11
                    # if seqnum_hex in seen_seqnums:
                    #     continue
                    seen_seqnums.add(seqnum_hex)
                    if UDP in pkt and pkt.sport == portnum:  # If UDP-type and src port
                        timeEPC = float(pkt.time)
                        timeDT = datetime.fromtimestamp(timeEPC).strftime('%Y/%j %H:%M:%S:%f')  # format of time output
                        csvwriter.writerow([n, timeDT, float(pkt.time), math.ceil(float(pkt.time)), pkt[IP].src,
                                            pkt[IP].dst, seqnum_hex])  # columns
                        print(n)
            csvfile.close()  # garbage collection
            end = time.time()
            timetaken = round(end - start, 3)
            print(f"$ SUCCESS!\n$ Created {csv_file_pre} in PWD over: {timetaken} seconds")
            break
        except FileNotFoundError as error:  # if filename is incorrect
            print("$", error, " [CODE 0x0f]\n$ Please make sure you include .pcap or .pcapng\n")
        except PermissionError as error:  # if permission is denied
            print("$", error, " [CODE 0x0a]\n$ Check that your file isn't open in another program (e.g. Excel)\n")
    global global_csvPre  # change globals ASAP
    global_csvPre = csv_file_pre


def pcap_conv_csv_post():
    while True:
        try:
            pcap_IN_postFW = input('$ Enter full exact name of PostFW pcap: \n>> ')
            portnum = 000 # enter port num here (CLEANED 3/20/25)
            # Read packets from pcap file
            start = time.time()  # time tracker for duration of script
            print(f"Reading in {pcap_IN_postFW} to rdpcap. This may take a while")
            packets = rdpcap(pcap_IN_postFW)[UDP]
            print("$ Converting ", pcap_IN_postFW, " from pcap/ng to csv")
            csv_file_post = pcap_IN_postFW + testver + '.csv'  # appends the csv file extension
            start_index = 38  # enter what byte you want to address (ARRAYS START FROM 0!!!!)
            with open(csv_file_post, 'w', newline='') as csvfile:  # this whole thing does the actual writing
                seen_seqnums = set()
                if len(seen_seqnums) == 0x3FFF:
                    seen_seqnums.clear()  # if 16384 values have been recorded, reset
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["Packet Number [CSV]", "Time", "Epoch", "Epoch Ceil", "Source IP",
                                    "Destination IP", "Sequence Number"])  # What columns?
                for n, pkt in enumerate(packets):
                    raw_bytes = raw(pkt[UDP])  # raw hex
                    byte_sequence = raw_bytes[start_index:start_index + 2]  # index + following x bytes (BIG END)
                    seqnum_hex = int.from_bytes(byte_sequence, byteorder='big')  # converts bytes to ints in BE
                    seqnum_hex = seqnum_hex - 0xC000  # offset for 14 bit usage of seqnum, assuming flag is always 11
                    if seqnum_hex in seen_seqnums:
                        continue

                    if len(seen_seqnums) == 0x3FFE:
                        seen_seqnums.clear()  # if 16383 values have been recorded, reset
                        seen_seqnums = set()
                    seen_seqnums.add(seqnum_hex)
                    if UDP in pkt and pkt.sport == portnum:  # If UDP-type and src port 
                        timeEPC = float(pkt.time)
                        timeDT = datetime.fromtimestamp(timeEPC).strftime('%Y/%j %H:%M:%S:%f')  # format of time output
                        csvwriter.writerow([n, timeDT, float(pkt.time), math.ceil(float(pkt.time)), pkt[IP].src,
                                            pkt[IP].dst, seqnum_hex])  # columns
                        print(n)
            csvfile.close()  # garbage collection
            end = time.time()
            timetaken = round(end - start, 3)
            print(f"$ SUCCESS!\n$ Created {csv_file_post} in PWD over: {timetaken} seconds")
            break
        except FileNotFoundError as error:  # if filename is incorrect
            print("$", error, " [CODE 0x0f]\n$ Please make sure you include .pcap or .pcapng\n")
        except PermissionError as error:  # if permission is denied
            print("$", error, " [CODE 0x0a]\n$ Check that your file isn't open in another program (e.g. Excel)\n")
    print("$ Renaming to global_csvPre and global_csvPost")
    global global_csvPost  # Change globals ASAP
    global_csvPost = csv_file_post

def pcap_conv_csv():
    # converts the pcap to a csv that can be read later
    while True:
        try:
            pcap_IN_preFW = input('$ Enter full exact name of PreFW pcap: \n>> ')
            portnum = 000 # enter port num here (CLEANED 3/20/25)
            # Read packets from pcap file
            start = time.time()
            print(f"Reading in {pcap_IN_preFW} to rdpcap. This may take a while")
            packets = rdpcap(pcap_IN_preFW)[UDP]
            print("$ Converting ", pcap_IN_preFW, " from pcap/ng to csv")
            csv_file_pre = pcap_IN_preFW + testver + '.csv'  # appends the csv file extension
            start_index = 38  # enter what byte you want to address in dec (ARRAYS START FROM 0!!!!) also could hex...
            with open(csv_file_pre, 'w', newline='') as csvfile:  # this whole thing does the actual writing
                seen_seqnums = set()
                if len(seen_seqnums) == 0x3FFF:
                    seen_seqnums.clear()  # if 16384 values have been recorded, reset
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["Packet Number [CSV]", "Time", "Epoch", "Epoch Ceil", "Source IP",
                                    "Destination IP", "Sequence Number"])  # What columns?
                for n, pkt in enumerate(packets):
                    raw_bytes = raw(pkt[UDP])  # raw hex
                    byte_sequence = raw_bytes[start_index:start_index + 2]  # index + following x bytes (BIG END)
                    seqnum_hex = int.from_bytes(byte_sequence, byteorder='big')  # converts bytes to ints in BE
                    seqnum_hex = seqnum_hex - 0xC000  # offset for 14 bit usage of seqnum, assuming flag is always 11
                    # if seqnum_hex in seen_seqnums:
                    #     continue
                    seen_seqnums.add(seqnum_hex)
                    if UDP in pkt and pkt.sport == portnum:  # If UDP-type and src port 
                        timeEPC = float(pkt.time)
                        timeDT = datetime.fromtimestamp(timeEPC).strftime('%Y/%j %H:%M:%S:%f')  # format of time output
                        csvwriter.writerow([n, timeDT, float(pkt.time), math.ceil(float(pkt.time)), pkt[IP].src,
                                            pkt[IP].dst, seqnum_hex])  # columns
                        print(n)
            csvfile.close()  # garbage collection
            end = time.time()
            timetaken = round(end - start, 3)
            print(f"$ SUCCESS!\n$ Created {csv_file_pre} in PWD over: {timetaken} seconds")
            break
        except FileNotFoundError as error:  # if filename is incorrect
            print("$", error, " [CODE 0x0f]\n$ Please make sure you include .pcap or .pcapng\n")
        except PermissionError as error:  # if permission is denied
            print("$", error, " [CODE 0x0a]\n$ Check that your file isn't open in another program (e.g. Excel)\n")
    #####
    # below is repeat, just for second csv
    while True:
        try:
            pcap_IN_postFW = input('$ Enter full exact name of PostFW pcap: \n>> ')
            portnum = 000 # enter port num here (CLEANED 3/20/25)
            # Read packets from pcap file
            start = time.time()  # time tracker for duration of script
            print(f"Reading in {pcap_IN_postFW} to rdpcap. This may take a while")
            packets = rdpcap(pcap_IN_postFW)[UDP]
            print("$ Converting ", pcap_IN_postFW, " from pcap/ng to csv")
            csv_file_post = pcap_IN_postFW + testver + '.csv'  # appends the csv file extension
            start_index = 38  # enter what byte you want to address (ARRAYS START FROM 0!!!!)
            with open(csv_file_post, 'w', newline='') as csvfile:  # this whole thing does the actual writing
                seen_seqnums = set()
                # if len(seen_seqnums) == 0x3FFF:
                #     seen_seqnums.clear()  # if 16384 values have been recorded, reset
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["Packet Number [CSV]", "Time", "Epoch", "Epoch Ceil", "Source IP",
                                    "Destination IP", "Sequence Number"])  # What columns?
                for n, pkt in enumerate(packets):
                    raw_bytes = raw(pkt[UDP])  # raw hex
                    byte_sequence = raw_bytes[start_index:start_index + 2]  # index + following x bytes (BIG END)
                    seqnum_hex = int.from_bytes(byte_sequence, byteorder='big')  # converts bytes to ints in BE
                    seqnum_hex = seqnum_hex - 0xC000  # offset for 14 bit usage of seqnum, assuming flag is always 11
                    if seqnum_hex in seen_seqnums:
                        continue
                    seen_seqnums.add(seqnum_hex)
                    if UDP in pkt and pkt.sport == portnum:  # If UDP-type and src port 
                        timeEPC = float(pkt.time)
                        timeDT = datetime.fromtimestamp(timeEPC).strftime('%Y/%j %H:%M:%S:%f')  # format of time output
                        csvwriter.writerow([n, timeDT, float(pkt.time), math.ceil(float(pkt.time)), pkt[IP].src,
                                            pkt[IP].dst, seqnum_hex])  # columns
                        print(n)
            csvfile.close()  # garbage collection
            end = time.time()
            timetaken = round(end - start, 3)
            print(f"$ SUCCESS!\n$ Created {csv_file_post} in PWD over: {timetaken} seconds")
            break
        except FileNotFoundError as error:  # if filename is incorrect
            print("$", error, " [CODE 0x0f]\n$ Please make sure you include .pcap or .pcapng\n")
        except PermissionError as error:  # if permission is denied
            print("$", error, " [CODE 0x0a]\n$ Check that your file isn't open in another program (e.g. Excel)\n")
    print("$ Renaming to global_csvPre and global_csvPost")

    global global_csvPre  # change globals ASAP
    global_csvPre = csv_file_pre
    global global_csvPost  # Change globals ASAP
    global_csvPost = csv_file_post

def skippcapconv():
    # I'm tired of figuring out the pcap conversion myself. Its faster to just do everything else with python and
    # the conversion through wireshark...
    pcap_IN_preFW = input('$ Enter full exact name of PreFW pcap: \n>> ')
    df1 = pd.read_csv(pcap_IN_preFW)
    df1 = df1.drop(columns=["Destination Port", "APID", "Info"])
    df1['SeqNum_Adjust'] = df1['Sequence Number'] - df1['Sequence Number'].shift(1)
    nf = df1.to_csv(pcap_IN_preFW, index = False)
    print(f"Exported to csv")

# noinspection PyPep8Naming
def SeqNumAlgo():
    if fileamount == 1:
        # This function will find the n-(n-1) > 1 rows, and then pass this file off to the xref function
        print("$ Running Sequence Number conversion algorithm on PreFW")
        df = pd.read_csv(global_csvPre)  # read into dataframe the name of the file (pulled from pcap_conv_csv()
        df['SeqNum_Adjust'] = df['Sequence Number'] - df['Sequence Number'].shift(1)  # create new row that takes
        # seqnum[1]-seqnum[0] to find diff
        nf = df.to_csv(global_csvPre, index=False)  # exports dataframe as new csv that can be used by xref()
        print("$ Finished, exported as: ", nf)
        return
    else:
        # This function will find the n-(n-1) > 1 rows, and then pass this file off to the xref function
        print("$ Running Sequence Number conversion algorithm on PreFW")
        df = pd.read_csv(global_csvPre)  # read into dataframe the name of the file (pulled from pcap_conv_csv()
        df['SeqNum_Adjust'] = df['Sequence Number'] - df['Sequence Number'].shift(1)  # create new row that takes
        # seqnum[1]-seqnum[0] to find diff
        nf = df.to_csv(global_csvPre, index=False)  # exports dataframe as new csv that can be used by xref()
        print("$ Finished, exported as: ", nf)

        print("$ Running Sequence Number conversion algorithm on PostFW")
        df = pd.read_csv(global_csvPost)  # read into dataframe the name of the file (pulled from pcap_conv_csv()
        df['SeqNum_Adjust'] = df['Sequence Number'] - df['Sequence Number'].shift(1)  # create new row that takes
        # seqnum[1]-seqnum[0] to find diff
        nf = df.to_csv(global_csvPost, index=False)  # exports dataframe as new csv that can be used by xref()
        print("$ Finished, exported as: ", nf)


def switching():
    # Temp holder for "first" determinant function
    global global_sflag
    print("$ Running switching systems")
    df1 = pd.read_csv(global_csvPre, dtype={'Epoch': float})  # read in files
    df2 = pd.read_csv(global_csvPost, dtype={'Epoch': float})
    while df1.iloc[0,2] <= df2.iloc[0,2]:
        df1 = df1.iloc[1:]
    df1.to_csv(global_csvPre, index=False)
        # if len(df1) > 0:
        #     compval = df2.iloc[0,1]
    #df1=df1[df1.iloc[0,2]<= df2.iloc[0,2]]
    #while True:
    # if df1.iloc[0, 2] <= df2.iloc[0, 2]:  # if the preFW time is greater, make xref process that first
    #     print("Pre- file first")
    #     while df1.iloc[0, 2] <= df2.iloc[0, 2]:
    #         df1 = df1.iloc[1:]
    #     global_sflag = True
    #     df1.to_csv(global_csvPre, index=False)
    # if df1.iloc[0, 1] > df2.iloc[0, 1]:  # if the postFW time is greater, swap the files and process that first
    #     print("Post- file first")
    #     while df1.iloc[0, 2] > df2.iloc[0, 2]:
    #         df2 = df2.iloc[1:]
    #     global_sflag = True
    #     df2.to_csv(global_csvPre, index=False)
        #global_sflag = False
    #else:
       # print("$ ERROR, ENDING PROGRAM")  # no idea what this use case is, but it allows for a soft exit
        #quit()
        #df1.to_csv(global_csvPre)


###############################################################################################
###############################################################################################
def xrefpd():
    df1 = pd.read_csv(global_csvPre, dtype={'Epoch': float, 'SeqNum_Adjust': float})
    df2 = pd.read_csv(global_csvPost, dtype={'Epoch': float, 'SeqNum_Adjust': float})
    df3 = df1[df1.iloc[:, 7] > 1].copy()
    print("$ Both files opened")
    # below is the logic that determines whether a dump is found. Basically, the above line reads all of df1 where
    # seqnum adjust > 1 into df3. The line below will compare any line df2 where seqnum > 1. If it is, it will compare
    # the seqnum and the rounded epoch time to see if it is in df3. if it is, it will remove it from df3.
    # Effectively, this will result in df3 only holding values that were found in df1 but not in df2. Any values in here
    # are ones that are lost in the firewall.
    condition = df3.apply(lambda row: not ((df2.iloc[:, 3] == row.iloc[3]).any() and
                                           (df2.iloc[:, 7] == row.iloc[7]).any()), axis=1)
    df3 = df3[condition]
    print("condition applied")
    outname = "outpd" + testver + ".csv"
    df3.to_csv(outname, index=False)
    print(f"outputted as {outname}")

def xref():
    csv_preFW = global_csvPre
    csv_postFW = global_csvPost
    #switchflag = global_sflag
    # now that both files are "declared", run the difference finder to locate differences
    # this compares the 2nd against the first, and as such will output lines NOT in 2nd that ARE in 1st. To swap this,
    # change for line in fileone if line not in filetwo to vice versa
    print("$ Finding Differences")
    with open(csv_preFW, 'r', newline='') as t1, open(csv_postFW, 'r', newline='') as t2:
        fileone = t1.readlines()
        filetwo = t2.readlines()
    print("$ Both files opened")
    outname = "out" + testver + ".csv"
    with open(outname, 'w', newline='') as outfile:
        csvwriter = csv.writer(outfile)
        csvwriter.writerow(
            ["Packet Number [CSV]", "Packet Number [PCAP]", "Time", "Source IP", "Destination IP",
             "Sequence Number", "SeqNumAlgo"])
        #if not switchflag:
        for line in fileone:
            if line not in filetwo:
                outfile.write(line)
        # if switchflag:
        #     for line in filetwo:
        #         if line not in fileone:
        #             outfile.write(line)
    print(f"$ New file created named {outname}")
    t1.close() and t2.close() and outfile.close()  # garbage collection


###############################################################################################
#  driver
def main():
    startup()  # runs startup scripts with intro and instructions
    # p1 = multiprocessing.Process(target=pcap_conv_csv_pre_multi())
    # p2 = multiprocessing.Process(target=pcap_conv_csv_post_multi())
    # print("Starting Process 1")
    # p1.start()
    # print("Process 1 completed...joining")
    # p1.join()
    # print("Process 1 joined, starting Process 2")
    # p2.start()
    # print("Process 2 completed...joining")
    # p2.join()
    # print("Process 2 joined")
    # print("$ Renaming to global_csvPre and global_csvPost")
    pcap_conv_csv_post()  # converts pcap file to csv file
    pcap_conv_csv_pre()
    SeqNumAlgo()  # finds missing packets via SeqNum
    #switching()  # wibbly wobbly timey wimey stuff
    #xrefpd()
    #xref()  # reads the 2 csv files and xref


if __name__ == '__main__':
    main()
