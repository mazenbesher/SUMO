import cmd
import re

from stop_simulator_shell import helpers


class StopSimulatorShell(cmd.Cmd):
    intro = "Type help or ? to list commands.\n"

    sumo_process = None

    # the simulation status
    status = "Not started"

    # regular expersions
    reg_exp = {
        "step": re.compile("s(\d*)"),
        "color": re.compile("c(\d*)([r|b|g|y])"),
        "local_accident": re.compile("la(\d*) after(\d*)"),
        "temporal_accident": re.compile("ta(\d*) after(\d*) at(\d*)"),
        "resume": re.compile("r(\d*)"),
        "follow": re.compile("f(\d*)")
    }

    # commands
    def do_start(self, arg):
        """start SUMO with given file config"""
        self.sumo_process = helpers.start_sumo(arg)

    def do_connect(self):
        """connect to the started GUI"""

    #
    def update_prompt(self):
        if self.status == "Not started":
            self.prompt =

        # self.prompt = "(Step %d)" % self.current_step


if __name__ == "__main__":
    StopSimulatorShell().cmdloop()
