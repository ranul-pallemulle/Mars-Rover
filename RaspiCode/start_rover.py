# script runs on boot. Does network setup to receive commands from
# remote computer. Runs parser on these commands and takes action
# accordingly.
# Note that when run on boot, this runs as a service under systemd.
# stdout and stderr visible through journalctl
import sys
import coreutils.resource_manager as mgr
from coreutils.parser import parse, CommandTypes, CommandError
from coreutils.tcpsocket import TcpSocket, TcpSocketError
from coreutils import launcher
from threading import Thread

def main(argv):
    '''
    Rover operation starts here! 
    Create a TcpSocket to communicate with remote computer. Parse
    received commands and feed into call_action.
    '''
    if len(argv) != 2:
        print("Usage: python3 start_rover.py <port>")
        sys.exit(1)
    try:
        port = int(argv[1])
    except ValueError:
        print("Port number should be an integer")
        sys.exit(1)
    try:
        mgr.global_resources.initialise()
    except mgr.ResourceError as e:
        print(str(e) + "\nExiting...")
        sys.exit(1)
    print("Waiting for connection...")
    try:
        main_sock = TcpSocket(port)
        main_sock.wait_for_connection()
    except TcpSocketError as e:
        print(str(e))
        sys.exit(1)
    print("Connected.")
    while(True):
        try:
            comm_str = main_sock.read()
            if comm_str is None:
                print("Connection lost")
                launcher.release_all()
                sys.exit(1)
            result = parse(comm_str)
        except TcpSocketError as e:
            print(str(e))
            launcher.release_all()
            sys.exit(1)
        except CommandError as e:
            main_sock.reply(str(e))
            print(str(e))
        else:
            reply = "ACK"
            try:
                main_sock.reply(reply)
            except TcpSocketError as e:
                print(str(e))
                launcher.release_all()
                sys.exit(1)
            action_thread = Thread(target=call_action,args=[result])
            action_thread.start()

def call_action(arg_list):
    '''First element of arg_list should be a command. Based on
    command, do something.'''
    try:
        if arg_list[0] == CommandTypes.START_JOYSTICK:
            launcher.launch_joystick(arg_list)
        elif arg_list[0] == CommandTypes.STOP_JOYSTICK:
            launcher.kill_joystick(arg_list)
        elif arg_list[0] == CommandTypes.START_ARM:
            launcher.launch_arm(arg_list)
        elif arg_list[0] == CommandTypes.STOP_ARM:
            launcher.kill_arm(arg_list)
    except launcher.LauncherError as e:
        print(str(e))
        return
    except Exception as e:
        print(str(e))
        sys.exit(1)
        
if __name__ == '__main__':
    main(sys.argv)
