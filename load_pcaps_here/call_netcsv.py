import os
import subprocess

# Calls the first file in Unstable_Version.
# Use this scipt to keep files in load_pcaps_here if you want to git.ignore
# this directory. Dpending on file structure, you may have to edit the actual
# implementation of running the code. You can always just adjust the path referenced
# below to adjust to your needs. 

def call_script():
    fileList = os.listdir('..\\unstable_version')
    file = fileList[0]
    rel_path = f'..\\unstable_version\\{file}'
    subprocess.run(['python', rel_path])

print("Calling netcsv.py\n#\n#\n#\n")
call_script()
