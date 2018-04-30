#!/usr/bin/python

import sys
import os
import getpass
import json
import urllib2
import base64
import fileinput
import stat
import subprocess
import re

username = ""
password = ""

def cmd(cmd_list):
    p = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return filter(lambda x: len(x) > 0, re.split('\n', out))

def write_script_header(f):
    f.write("#!/bin/bash\n")
    f.write("\n")
    f.write("# Use which ever suits your project\n")
    f.write("USERNAME=%s\n" % username)
    f.write('# read -p "Username: " USERNAME\n')
    f.write('read -s -p "Password for $USERNAME: " PASSWORD\n\n')
    f.write('echo\n\n')

def write_locale_section(f, project_id, loc, locale_filenameformat, target):
    url = "\"https://api.phraseapp.com/api/v2/projects/%s/locales/%s/download?file_format=%s\"" % (project_id, loc[u'id'], target)
    locale_file = locale_filenameformat % loc[u'code'].lower()

    f.write("# fetch locale for %s (%s)\n" % (  loc[u'name'], loc[u'code'] ))
    f.write('echo -en "Fetching %s (to %s) ... "\n' % ( loc[u'name'], locale_file))
    f.write("curl -u $USERNAME:$PASSWORD %s > %s 2>/dev/null\n" % ( url, locale_file ))
    f.write('if [ "$?" -eq 0 ]\n')
    f.write('then\n')
    f.write("\techo OK\n")
    f.write('else\n')
    f.write("\techo -e \"\\nFailed to fetch!, aborting.\"\n")
    f.write("\texit 1\n")
    f.write('fi\n\n\n')

def get_json(path):
    global username
    global password

    request = urllib2.Request("https://api.phraseapp.com/api/v2/%s" % path)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    result = urllib2.urlopen(request)
    content = result.read()
    #print content
    return json.loads(content)

def ask_for_targets(project_id, suggested_targets):
    print("Which formats would you like to export for?")
    for (i, e) in enumerate(suggested_targets):
        print("[%d] %s" % (i, e))

    selected_index = raw_input("Please choose an index from the array above, use comma-separated or, empty for all: ")

    if selected_index == "":
        selected_range = range(0, len(suggested_targets))
    else:
        selected_range = json.loads('[%s]' % selected_index)

    return map(lambda x: suggested_targets[x], selected_range)

def ask_for_locales(project_id):
    content = get_json("projects/%s/locales" % project_id)

    for (i,x) in enumerate(content):
        if x[u'default']:
            print "[%d] %s (%s) is default locale" % (i, x[u'name'], x[u'code'])
        else:
            print "[%d] %s (%s)" % (i, x[u'name'], x[u'code'])
    print("")

    selected_index = raw_input("Select locales from the list above, use comma-separated or, empty for all: ")
    if selected_index == "":
        selected_range = range(0, len(content))
    else:
        selected_range = json.loads('[%s]' % selected_index)

    return map(lambda x: content[x], selected_range)

def ask_for_project_id():
    content = get_json("projects/")
    if len(content) <= 0:
        print("No project found!")
        exit(1)

    print "Found projects:"

    for (i,x) in enumerate(content):
        print "[%d] %s > %s" % (i, x[u'account'][u'name'], x[u'name'])
    print("")

    selected_index = raw_input("Please choose an index from the array above: ")
    if selected_index == "":
        selected_index = 0

    return content[int(selected_index)][u'id']

def ask_for_scriptfile():
    return raw_input("Script file to create: ")

def ask_for_locations_for_targets(targets):
    locations = []
    for target in targets:
        locations += [ raw_input("Write template path for %s: " % target) ]
    return locations

def main():
    global username
    global password

    if len(sys.argv) != 2:
        print "Usage: %s: USERNAME" % sys.argv[0]
        exit(1)

    # Set the global username and password
    username = sys.argv[1]
    password = getpass.getpass()

    # Use the API to get the project ID
    # and then ask the user for what project they want to use
    project_id = ask_for_project_id()

    # Ask the user for which targets they'd like to export
    targets = ask_for_targets(project_id, ["strings", "xml"])

    # Ask the user for which locales they'd like to export
    content = ask_for_locales(project_id)

    # Ask there user where the create script should be
    script_file = ask_for_scriptfile()

    # Ask the user where the different targets should be exported
    locations = ask_for_locations_for_targets(targets)

    # Export the header to the script
    with open(script_file, 'w') as f:
        write_script_header(f)

    # Export the content, which will fetch the differnt locales
    # for the different export-formats selected
    for (i,locale) in enumerate(content):
        with open(script_file, 'a') as f:
            for (j, location) in enumerate(locations):
                write_locale_section(f, project_id, locale, location, targets[j])

    os.chmod(script_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

if __name__ == "__main__":
    main()
