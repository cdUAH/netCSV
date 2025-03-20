# netcsv Changelog

### Update 2.1.0
There are 2 main changes here: changes to file management and code changes. These have been split into 2 different
sections:
#### Management Changes
1. Renamed from xrefcsv to netcsv. Updated all documentation. Some previous references will be updated over time
2. Added version control system and created a GitHub repo. Contact Cooper for info on branching/pulling
3. Moved docs to GitHub

#### Code Changes
1. Created python script `call_netcsv` to call netcsv from a subdirectory, specifically `netcsv/active_files`
   1. `netcsv/active_files` is a gitignored directory with an exclusion for `call_netcsv`. This allows you to do work 
   within this directory without worrying about commiting potentially sensitive information if using git. 
2. Added a Menu option

---
### Version 2.0.3 (8/29/2024)
1. Added ability to read in a user-made CSV file for single-file analysis
   1. This user-made file will be a copy-paste of the AMS drops report. Netcsv will prompt with an option to allow you 
   to read this CSV in and automatically tell you which of the lines are found missing drop the drop file.
2. Removed custom time range
   1. The source file times do not sync with the reported times. This means that this feature doesn't really do much, 
   and just adds more confusion. It is being commented out, and new code will be built around the assumption that it is 
   not active. In the future, if this item is re-added, new functions will have to incorporate this feature
---
### Version 2.0.2 (7/17/2024)
1. Framework to allow for Embedded Time referencing, instead of relying on VCDU number for alignment
   1. This will expand the capabilities to allow netcsv to work with a broader range of inputs along the AMS data track,
   as well as provide a baseline framework for expansion beyond AMS data
   2. Still relies on VCDU for dropping dupes. If there’s a file with a different format, this will need to be changed 
   to match some unique identifier in that
2. Implemented the ability for the user to enter a custom time range to sort by
   1. User is prompted for a start time and an end time. New files will be created within those time ranges. There is a 
   specific format required for this time that can be changed depending on what the user wants.
3. Shifted automerging of files to v2.0.3 TBD, may shift to later version
4. Packaged exe as one file, instead of application folder. Will only need the one .exe file to run (Windows only)
5. Slight edits to verbiage and prompts to improve usage
6. Added additional code comments to improve readability
---
### Version 2.0.1 (7/1/2024)
1. Modified how the try functions work during file read in order to loop file selection if error is thrown.
   1. v2.0.0 tried the entire netcsv() function, resulting in a complete restart if an error was thrown (such as FNF)
   . If you had selected a file during pre, but an error was thrown during post, you would have to reselect pre
   2. v2.0.1 makes each read-in independent. If an error is thrown during post, you only have to reselect post, not 
   everything else*
2. Added quit() if an unexpected error is thrown during file read-in. 
   1. As more data is tested, this can be refined. Error handling could be moved to its own function if need-be
3. Fixed default opening of file explorer directory. Now works as intended (opens in the directory netcsv.py is in)
4. Created executable for Windows machines. This allows you to run the script without needing python installed on your 
system.
5. Added platform module to check python version during startup()
6. Slight edits to verbiage and prompts to improve usage
7. Added additional code comments to improve readability