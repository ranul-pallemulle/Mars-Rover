import sys
from coreutils.diagnostics import Diagnostics as dg
import coreutils.resource_manager as mgr
import coreutils.configure as cfg
import coreutils.unit as unit
from interfaces.opmode import OpMode, OpModeError
from coreutils.parser import parse_entry, CommandPrefixes, CommandError
from coreutils.tcpsocket import TcpSocket, TcpSocketError
import coreutils.launcher as launcher
from coreutils.launcher import LauncherError
from threading import Thread

usage_str = "Usage: python3 start_rover.py <port> \n       \
python3 start_rover.py <port> <settings> \n       \
python3 start_rover.py --as-unit <unitname> \n       \
python3 start_rover.py --as-unit <unitname> <settings> \n"

def main(argv):
    '''Rover operation starts here! Wait for a connection from a remote
    computer, interpret commands received and take appropriate action.
    '''
    if len(argv) < 2 and len(argv) > 4:
        dg.print(usage_str)
        sys.exit(1)
        
    if argv[1] == '--as-unit':  # running in unit mode
        process_as_unit(argv)
        return
        
    # Proceed as main unit if --as-unit not specified
    try:
        port = int(argv[1])     # port to receive commands on
    except ValueError:
        dg.print("Port number should be an integer")
        sys.exit(1) # exit with error code
        
    try:        
        if len(argv) == 3:      # settings file specified
            cfg.Configuration.settings_file(argv[2])
        else:                   # use the default settings file (settings.xml)
            cfg.Configuration.settings_file()
    except cfg.ConfigurationError as e: # error related to settings file
        dg.print(str(e) + "\nExiting...")
        sys.exit(1)

    try:
        OpMode.opmodes_initialise() # check for available operational modes
    except OpModeError as e:
        dg.print(str(e) + "\nExiting...")
        sys.exit(1) # exit with error code
    if OpMode.get_all():        # list of registered modes is not empty
        dg.print("Found operational modes: ")
    for name in OpMode.get_all_names(): # print registered names of all modes
        dg.print('  '+name)
        
    try:
        mgr.global_resources.initialise() # get all resources ready
                                          # (motors, camera, etc)
    except mgr.ResourceError as e:
        dg.print(str(e) + "\nExiting...")
        sys.exit(1) # exit with error code

    dg.initialise() # start diagnostics

    unit.activate_main_unit_services()
        
    # start operation
    while (True):
        dg.print("Waiting for connection...")
        try:
            main_sock = wait_for_remote(port)
            host,_ = main_sock.get_ip_address()
            cfg.overall_config.set_ip(host)
        except TcpSocketError as e: # connection error
            dg.print(str(e))
            cleanup()
            continue # wait for connection again
        shutdown = run(main_sock)
        if shutdown:
            break
    cleanup()
    dg.close()
    sys.exit(0) # shutdown


def wait_for_remote(port):
    sock = TcpSocket(port)
    sock.wait_for_connection() # wait for remote connection
    dg.print("Connected.")
    return sock


def run(main_socket):
    while(True):
        try:
            comm_str = main_socket.read() # wait for a command
            if comm_str is None:
                dg.print("Connection lost")
                cleanup()
                # sys.exit(1)
                return False
            result = parse_entry(comm_str) # command received; interpret it
        except TcpSocketError as e:        # connection error occurred
            dg.print(str(e))
            cleanup()
            # sys.exit(1)
            return False
        except CommandError as e: # received command could not be interpreted
            main_socket.reply(str(e)) # send reply to remote with error message
            dg.print(str(e))
        else:                   # command successfully interpreted
            reply = "ACK"
            try:
                main_socket.reply(reply)
            except TcpSocketError as e: # connection error occurred
                dg.print(str(e))
                cleanup()
                # sys.exit(1)
                return False
            if result[0] == "PING": # ping request received
                continue # do nothing
            elif result[0] == "SHUTDOWN":
                return True
            action_thread = Thread(target=call_action,args=[result])
            action_thread.start() # carry out action directed by the received
                                  # command, in a separate thread.


def call_action(arg_list):
    '''Based on command, do something.'''
    try:
        if arg_list[0] == CommandPrefixes.START: # start an operational mode
            launcher.launch_opmode(arg_list[1], arg_list[2:])
        elif arg_list[0] == CommandPrefixes.STOP: # stop an operational mode
            launcher.kill_opmode(arg_list[1], arg_list[2:])
        else:                   # command is to be passed to a specific mode
            mode_name = arg_list[0]
            mode = OpMode.get(mode_name) # get mode using its registered
                                         # name. Throws OpModeError if mode_name
                                         # is invalid.
            if mode.is_running():
                mode.submode_command(arg_list[1:]) # pass command to the mode
            else:
                dg.print("{} not active. Start {} before passing submode commands.".format(mode_name, mode_name))
    except (LauncherError, OpModeError) as e: # error carrying out action
        dg.print(str(e))
        return                  # terminate thread - stop processing current command
    except Exception as e:      # unhandled exception: something is really wrong
        dg.print(str(e))
        sys.exit(1)


def cleanup():
    '''Run cleaning up functions so that all threads can stop for a clean exit.'''
    launcher.release_all()
    unit.deactivate_main_unit_services()

def process_as_unit(argv):
    if len(argv) != 3 and len(argv) != 4:
        dg.print(usage_str)
        sys.exit(1)

    unitname = argv[2]

    try:
        if len(argv) == 4:
            cfg.Configuration.settings_file(argv[3])
        else:
            cfg.Configuration.settings_file()
    except cfg.ConfigurationError as e:
        dg.print(str(e) + "\nExiting...")
        sys.exit(1)

    cfg.overall_config.running_as_unit = True

    try:
        unit.register_unit_name(unitname)
    except unit.UnitError as e:
        dg.print(str(e) + "\nExiting...")
        sys.exit(1)
    dg.print("Running as unit with name {}".format(unitname))
    
    # try:
    #     OpMode.opmodes_initialise() # check for available operational modes
    # except OpModeError as e:
    #     dg.print(str(e) + "\nExiting...")
    #     sys.exit(1)
    # if OpMode.get_all():        # list of registered modes is not empty
    #     dg.print("Found operational modes: ")
    # for name in OpMode.get_all_names(): # print registered names of all modes
    #     dg.print('  '+name)
        
    try:
        mgr.global_resources.initialise() # get all resources ready
                                          # (motors, camera, etc)
    except mgr.ResourceError as e:
        dg.print(str(e) + "\nExiting...")
        sys.exit(1)        


if __name__ == '__main__':
    main(sys.argv)
