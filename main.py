import sys
from solve_me import TasksCommand


def parseArgs():
    args = [arg.lower() for arg in sys.argv[1:]]
    commands_list = ["add", "ls", "del", "done",  "report"]
    if len(args) < 1 or args[0] not in commands_list:
        return ("help", [])
    return args[0], args[1:]


if __name__ == "__main__":
    tasksCommand = TasksCommand()
    command, args = parseArgs()
    tasksCommand.run(command, args)
