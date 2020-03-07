import os
import argparse
import subprocess
import re
from subprocess import call

#Handle flags
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--meta",         help="Meta flag")
parser.add_argument("-w", "--workspace",    help="Workspace flag")
parser.add_argument("-mw","--move_window",  help="Move flag")
parser.add_argument("-mwm","--move_window_meta",  help="Move flag to meta")
parser.add_argument("-n","--next",  help="Move to next meta")
parser.add_argument("-p","--prev",  help="Move to prev meta")
parser.add_argument("-r", "--rename",       help="Rename Meta Workspace")
args = parser.parse_args()

#Name of stored meta variable
metaVarName = "meta_workspace"

#Correct path to stored variable
dirname = os.path.dirname(__file__) + "/.vars/"
# Create target Directory if don't exist
if not os.path.exists(dirname):
    os.mkdir(dirname)

variable_name = 'variables'
filename = os.path.join(dirname, variable_name)

workspace_name = 'cur_ws'
cur_ws   = os.path.join(dirname, workspace_name)

ws_list = 'ws_list'
wslist  = os.path.join(dirname, ws_list)

ws_str = 'ws_str'
wsstr  = os.path.join(dirname, ws_str)

def readMeta():
    with open(filename) as fin:
        for line in fin:
            if line.startswith(metaVarName):
                return line.split(":")[-1].strip()

def readWsList(meta,overwrite):
    outline = []
    found = 0
    with open(wslist) as fin:
        for line in fin:
            line = line.rstrip()
            if line.startswith(meta):
                found = 1
                if overwrite:
                    cmd = subprocess.Popen('zenity --entry', stdout=subprocess.PIPE, shell=True)
                    output, err = cmd.communicate()
                    returncode = cmd.wait()
                    if returncode == 0:
                        name = "%s" % output.decode("utf-8").strip()
                        cur_ws_string = meta + ":" + name
                        outline.append(cur_ws_string + "")
                    else:
                        cur_ws_string = line
                        outline.append(cur_ws_string + "")
                else:
                    if line.split(":")[-1].strip() == "":
                        cmd = os.popen('zenity --entry').read()
                        cmd = cmd.split("output = ")[-1].strip()
                        cur_ws_string = meta + ":" + cmd
                        outline.append(cur_ws_string + "")
                    else:
                        outline.append(line)
                        cur_ws_string = line
            else:
                #check if format of line is correct
                if re.match('\d+:', line):
                    cur_ws_string = line
                    outline.append(line)

    if found == 0: #if we have scanned all lines and not found a match
        cmd = os.popen('zenity --entry').read()
        cur_ws_string = meta + ":" + cmd
        outline.append(cur_ws_string)
    fin.close
    with open(wslist, 'w') as out:
        for line in outline:
            out.write(line + "\n")
    if os.path.isfile(cur_ws):
        os.remove(cur_ws)
    with open(cur_ws, 'a') as out:
        out.write(cur_ws_string)

    statusline = ""
    myoutline = sorted(outline, key = lambda a: int(a.split(":")[0]))
    for line in myoutline:
        a = line.split(":")
        disp =  "" if (a[0] == meta) else ""
        if a[1] or a[0] == meta:
            statusline += "["+disp+a[0]+":"+a[1]+"]"
        # else:
        #     statusline += "["+disp+a[0]+"]"

    with open(wsstr, 'w') as out:
        out.write(statusline)

def writeMeta(value):
    if os.path.isfile(filename):
        os.remove(filename)
    with open(filename, 'a') as out:
        out.write(metaVarName + ":" + value + '\n')

#Create file if it does not exist
if not os.path.isfile(filename):
    writeMeta("1")

#Create file if it does not exist
if not os.path.isfile(cur_ws):
    writeMeta("1")

if not os.path.isfile(wslist):
    with open(wslist, 'a') as out:
        out.write("\n")
        out.close()

if not os.path.isfile(wsstr):
    with open(wsstr, 'a') as out:
        out.write("\n")
        out.close()

#Change meta workspace
if args.meta is not None:
    meta = args.meta
    print("change meta: " + meta)
    #Now check to see if the meta ws has a name - if not, add one
    readWsList(meta,0)
    #Now write this out to cur_ws, then write meta
    writeMeta(meta)

#Change workspace within meta workspace
if args.workspace is not None:
    meta = readMeta()
    workspace = args.workspace
    print("change meta workspace: " + meta)
    cmd = 'i3-msg "workspace ' + meta + workspace + ';"'
    print(cmd)
    os.system(cmd)

#Move window in between workspaces within meta workspace
if args.move_window is not None:
    meta = readMeta()
    print("move window between workspaces in current meta: " + meta)
    workspace = args.move_window
    cmd = 'i3-msg "move container to workspace ' + meta + workspace + ';"'
    print(cmd)
    os.system(cmd)

#Move window in between metas to workspace 0
if args.move_window_meta is not None:
    meta = args.move_window_meta
    print("move window to meta: " + meta)
    cmd = 'i3-msg "move container to workspace ' + meta + '0;"'
    print(cmd)
    os.system(cmd)

#Change meta workspace
if args.rename is not None:
    #get meta value from cur_ws
    meta = readMeta()
    #update ws_list dictionary
    #write out cur_ws
    readWsList(meta,1)

if args.prev is not None:
    meta = "%s" % readMeta()
    if int(meta) > 0:
        meta = "%s" % (int(meta) - 1)
    readWsList(meta,0)
    writeMeta(meta)
    # get current workspace number
    subcmd = subprocess.Popen("i3-msg -t get_workspaces | jq -r 'map(select(.focused))[0].name'", stdout=subprocess.PIPE, shell=True)
    output, err = subcmd.communicate()
    returncode = subcmd.wait()
    workspace = 0
    if returncode == 0:
        workspace = "%s" % output.decode("utf-8").strip()[1]
    print("change to: " + meta + workspace)
    cmd = 'i3-msg "workspace ' + meta + workspace + ';"'
    print(cmd)
    os.system(cmd)

if args.next is not None:
    meta = "%s" % readMeta()
    if int(meta) < 9:
        meta = "%s" % (int(meta) + 1)
    readWsList(meta, 0)
    writeMeta(meta)
    # get current workspace number
    subcmd = subprocess.Popen("i3-msg -t get_workspaces | jq -r 'map(select(.focused))[0].name'", stdout=subprocess.PIPE, shell=True)
    output, err = subcmd.communicate()
    returncode = subcmd.wait()
    workspace = 0
    if returncode == 0:
        workspace = "%s" % output.decode("utf-8").strip()[1]
    print("change to: ", meta,  workspace)
    cmd = 'i3-msg "workspace ' + meta + workspace + ';"'
    print(cmd)
    os.system(cmd)

