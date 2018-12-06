# script runs on boot. Does network setup to receive commands from
# remote computer. Runs parser on these commands and takes action
# accordingly.
# Note that when run on boot, this runs as a service under systemd.
# stdout and stderr visible through journalctl
import sys
from coreutils.parser import parse, CommandTypes, CommandError
from sockets.tcpsocket import TcpSocket, TcpSocketError
import coreutils.launcher

def main(argv):
    if len(argv) != 2:
        print("Usage: python3 start_rover.py <port>")
        sys.exit(1)
    try:
        port = int(argv[1])
    except ValueError:
        print("Port number should be an integer")
        sys.exit(1)
    try:
        main_sock = TcpSocket(port)
        main_sock.wait_for_connection()
    except TcpSocketError as e:
        print(str(e))
        sys.exit(1)
    while(True):
        try:
            comm_str = main_sock.read()
            result = parse(comm_str)
        except TcpSocketError as e:
            print(str(e))
            sys.exit(1)
        except CommandError as e:
            main_sock.reply(str.encode(str(e)))
            print(str(e))
        else:
            reply = "ACK\n"
            main_sock.reply(str.encode(reply))
            print(result)
            call_action(result)

def call_action(arg_list):
    try:
        if arg_list[0] == CommandTypes.START_JOYSTICK:
            coreutils.launcher.launch_joystick(arg_list)
        elif arg_list[0] == CommandTypes.STOP_JOYSTICK:
            coreutils.launcher.kill_joystick(arg_list)
        elif arg_list[0] == CommandTypes.TOGGLE_JOYSTICK:
            coreutils.launcher.toggle_joystick(arg_list)
    except Exception as e:
        print(str(e))
        sys.exit(1)
        
if __name__ == '__main__':
    main(sys.argv)
