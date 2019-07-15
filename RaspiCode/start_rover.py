import sys
from coreutils.diagnostics import Diagnostics as dg
import coreutils.resource_manager as mgr
import coreutils.configure as cfg
from interfaces.opmode import OpMode, OpModeError
from coreutils.parser import parse_entry, CommandPrefixes, CommandError
from coreutils.tcpsocket import TcpSocket, TcpSocketError
import coreutils.launcher as launcher
from coreutils.launcher import LauncherError
from threading import Thread

def main(argv):
    '''Rover operation starts here! Wait for a connection from a remote
    computer, interpret commands received and take appropriate action.
    '''
    if len(argv) != 2 and len(argv) != 3:
        print("Usage: python3 start_rover.py <port> \n       \
python3 start_rover.py <port> <settings>")
        sys.exit(1)
        
    try:
        port = int(argv[1])     # port to receive commands on
    except ValueError:
        print("Port number should be an integer")
        sys.exit(1)
        
    try:        
        if len(argv) == 3:      # settings file specified
            cfg.Configuration.settings_file(argv[2])
        else:                   # use the default settings file (settings.xml)
            cfg.Configuration.settings_file()
    except cfg.ConfigurationError as e: # error related to settings file
        print(str(e) + "\nExiting...")
        sys.exit(1)
        
    try:
        OpMode.opmodes_initialise() # check for available operational modes
    except OpModeError as e:
        dg.print(str(e) + "\nExiting...")
        sys.exit(1)
    if OpMode.get_all():        # list of registered modes is not empty
        dg.print("Found operational modes: ")
    for name in OpMode.get_all_names(): # print registered names of all modes
        dg.print('  '+name)
        
    try:
        mgr.global_resources.initialise() # get all resources ready
                                          # (motors, camera, etc)
    except mgr.ResourceError as e:
        dg.print(str(e) + "\nExiting...")
        sys.exit(1)
        
    dg.initialise()             # start diagnostics connection

    dg.print("Waiting for connection...")
    try:
        main_sock = TcpSocket(port)
        main_sock.wait_for_connection() # wait for remote connection
    except TcpSocketError as e:
        dg.print(str(e))
        sys.exit(1)
        
    dg.print("Connected.")
    
    while(True):
        try:
            comm_str = main_sock.read() # wait for a command
            if comm_str is None:
                dg.print("Connection lost")
                cleanup()
                sys.exit(1)
            result = parse_entry(comm_str) # command received; interpret it
        except TcpSocketError as e:        # connection error occurred
            dg.print(str(e))
            cleanup()
            sys.exit(1)
        except CommandError as e: # received command could not be interpreted
            main_sock.reply(str(e)) # send reply to remote with error message
            dg.print(str(e))
        else:                   # command successfully interpreted
            reply = "ACK"
            try:
                main_sock.reply(reply)
            except TcpSocketError as e: # connection error occurred
                dg.print(str(e))
                cleanup()
                sys.exit(1)
            if result[0] == "PING": # ping request received
                continue # already ACKed
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
    dg.close()

        
if __name__ == '__main__':
    main(sys.argv)
