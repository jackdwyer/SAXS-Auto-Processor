import sys, subprocess

process = subprocess.Popen(['echo', "HEY"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output,error = process.communicate()

print "OUT"


print output

