import sys, os, subprocess

PORT = 8813


def start_sumo(config_file_path):
    # we need to import python modules from the $SUMO_HOME/tools directory
    try:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
        from sumolib import checkBinary
    except ImportError:
        sys.exit(
            "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should"
            " contain folders 'bin', 'tools' and 'docs')")

    # start sumo-gui as server (as subprocess)
    sumoBinary = checkBinary('sumo-gui')
    sumoProcess = subprocess.Popen([sumoBinary, "-c", config_file_path
                                       , "--remote-port", str(PORT), "--start"],
                                   stdout=sys.stdout, stderr=sys.stderr)
    return sumoProcess
