#!/usr/bin/python
import os, sys

class DenhacPidfile:

    # Treated as static vars
    pid     = os.getpid()
    pidfile = '/tmp/' + os.path.basename(sys.argv[0]) + '.pid'

    def __init__(self):
        pass

    def is_pid_running(pid):
        """ Check For the existence of a unix pid. """
        try:
            os.kill(DenhacPidfile.pid, 0)        # Sig 0 is "are you there, process? What's your status?"
        except OSError:
            return False
        else:
            return True

    def createPidFile():
        if os.path.isfile(DenhacPidfile.pidfile):
            pidFromFile = int(open(DenhacPidfile.pidfile).read())

            if DenhacPidfile.is_pid_running(pidFromFile):
                raise Exception("Another instance of this script is running under PID " + str(pidFromFile))

        # Write out our own PID now if we're continuing
        open(DenhacPidfile.pidfile, 'w').write(str(DenhacPidfile.pid))

    def removePidFile():
        if os.path.isfile(DenhacPidfile.pidfile):
            os.remove(DenhacPidfile.pidfile)

    # Python 2.x way of declaring static functions
    is_pid_running = staticmethod(is_pid_running)
    createPidFile  = staticmethod(createPidFile)
    removePidFile  = staticmethod(removePidFile)
