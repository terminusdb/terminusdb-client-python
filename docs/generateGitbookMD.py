#  * Python/Sphinx markdown to GitBook markdown converter. 
#  * Generates GitBook compatible md files (suffix: `.md`) from
#  * Sphinx md files.
#  * 
#  * Script location:
#  * ----------------
#  * 
#  * This script works from directory `terminusdb-client-python/docs/source/`. 
#  * 
#  * GitBook location:
#  * -----------------
#  * 
#  * Rendered files are uploaded to:
#  * https://terminusdb.com/docs/index/terminusx-db/reference-guides/python-client-reference
#  * 

import glob
import re
import os 

f_dir = "./build/markdown/"

aPyFile = []
f_md = None

#  * Create GitBook compatibility for 
#  * 
#  * 
#  * @param {string} s - 
#  */
def _pre_process_script(s):
    """Create GitBook compatibility for scripts.
    Parameters
    ----------
    s : string File contents.

    Returns
    -------
    string
        proccessed file contents
    """
    s = re.sub("### Options", "**Options**", s)
    s = re.sub("### \-", "* `-",s)
    s = re.sub("### Arguments", "\n\r**Arguments**",s)
    s = re.sub("\(\,", ",",s)
    s = re.sub("\( \<", " <",s)
    s = re.sub("\>\)", ">",s)
    s = re.sub("### ([A-Z])", r"* `\1",s)
    s = re.sub("\)\n", ")` \n",s)
    s = re.sub("\>\n", ">` \n",s)
    s = re.sub("###", "##",s)
    s= re.sub("^[ \t]+","",s,flags=re.MULTILINE)
    return s

def _pre_process(s):

    """Create GitBook compatibility for class and module defintions.
    Parameters
    ----------
    s : string File contents.

    Returns
    -------
    string
        proccessed file contents
    """
    s=re.sub("^ \*", "",s)
    s=re.sub("### _class_", "## class",s)
    s=re.sub("#### _property_", "\r\n> **Property:** ",s)
    s=re.sub("Bases: ", "**Bases:** ",s)
    s=re.sub("\\\_", "_",s)
    s=re.sub(">>> ", "",s)
    s=re.sub("\* \*\*Parameters\*\*", "**Parameter/s**",s)
    s=re.sub("\* \*\*Returns\*\*", "**Returns**",s)
    s=re.sub("\* \*\*Return type\*\*", "**Return type/s**",s)
    s=re.sub("\* \*\*Type\*\*", "**Type**",s)
    s=re.sub("\* \*\*Raises\*\*", "**Raises**",s)
    s=re.sub("### See also", "**See also**",s)
    s=re.sub("### Examples", "**Example/s**",s)
    s=re.sub("### Example", "**Example/s**",s)
    s=re.sub("### Notes", "**Notes**",s)
    s=re.sub("\*str\*", "`str`",s)
    s=re.sub(r"\b(str)\b", "`str`",s)
    s=re.sub("\*strs\*", "`strs`",s)
    s=re.sub("\*None\*", "`none`",s)
    s=re.sub("\*bool\*", "`bool`",s)
    s=re.sub("\*int\*", "`int`",s)
    s=re.sub("\*optional\*", "`optional`",s)
    s=re.sub("\*, \*", ", ",s)
    s=re.sub("^#### at\_type\(\_ = \'", "> **at_type** = '",s)
    s=re.sub("\_ \)", "'",s)
    s=re.sub("#### ", "### ",s)
    s= re.sub("^[ \t]+","",s,flags=re.MULTILINE)
    return s

def create_md_file(s):
    """Convert .py file to an array and write to md file a line at a time. Note - can be achieved with one write operation. 
    The 'line at a time' approach enables output to be fine-tuned should this be required in future.

    Parameters
    ----------
    s : string File contents.

    Returns
    -------
    string
        proccessed file contents
    """
    aPyFile = re.split("\r\n",s);

    for x in aPyFile:
        _md(x)
        

def _md(line, nL = 0):
    """Build MD file a line at a time.

    Parameters
    ----------
    s : string String to write to file.
    nL : integer Number of carriage returns to write after string.
    """
    line_end = ""
    if nL == 0:
        line_end = "\n"
    else:
        line_end = "\n\n"

    f_md.write(line + line_end)
    

path = f_dir+'gitbook-md'
    
# Create the directory 'gitbook' in  'build/markdown/' 
if not os.path.exists(path):
    try: 
        os.mkdir(path) 
    except OSError as error: 
        print(error)

# Loop through each file for conversion
for f in glob.glob(f"{f_dir}*.md"):
    file = open(f,"r")
    file_data = file.read()

    f_md = open(path+"/"+f.split("/")[3], "w")

    f = f_dir+f

    process_data = ""
    if re.search("Scaffolding", f): 
        process_data = _pre_process_script(file_data)
       
    else:
        process_data = _pre_process(file_data)

    create_md_file(process_data)
    f_md.close()
