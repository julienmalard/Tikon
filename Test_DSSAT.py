import subprocess
# easy_install pexpect

# subprocess.call("C:\DSSAT45\DSCSM046.EXE MZCER046 B Resultados_DSSAT\DSSBatch.v45")
# subprocess.call("F:\Plagas_prueba.txt")

dssat = subprocess.Popen("C:\DSSAT46\DSCSM046.EXE MZCER046 B DSSBatch.v45",
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         cwd = "F:\Julien\PhD\Python\Resultados_DSSAT",
#                         bufsize=0,
#                         universal_newlines=True,
                         )
#print(dssat.poll())
#dssat.communicate(input="F:\Plagas_prueba.txt")
print(dssat.communicate(input=b"F:\Plagas_prueba.txt"))

día = 0
dssat.stdin.write(b"F:\Plagas_prueba.txt")
test = dssat.stdin.write(b"F:\Plagas_prueba.txt")
print(dssat.stdout)
print(test)
print(día)
dssat.poll()
día += 1




#dssat.terminate

#com.stdin.write("ss")
##
##from subprocess import Popen, PIPE
##
#### shell out, prompt
##def shell(args, input=''):
##    ''' uses subprocess pipes to call out to the shell.
##
##    args:  args to the command
##    input:  stdin
##
##    returns stdout, stderr
##    '''
##    p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
##    stdout, stderr = p.communicate(input=input)
##    return stdout, stderr
##
##prueba = shell("C:\DSSAT45\DSCSM046.EXE MZCER046 B Resultados_DSSAT\DSSBatch.v45",
##      input = 'F:\Plagas_prueba.txt')
##print(prueba)
