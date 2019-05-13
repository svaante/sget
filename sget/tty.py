import termios
import sys
import fcntl


def put_text(text, run=False):
    tty = sys.stdin
    old_attr = termios.tcgetattr(tty)
    new_attr = termios.tcgetattr(tty)
    new_attr[3] &= ~(termios.ECHO | termios.ICANON)
    termios.tcsetattr(tty, termios.TCSANOW, new_attr)
    for char in text:
        fcntl.ioctl(tty, termios.TIOCSTI, char)
    if run:
        fcntl.ioctl(tty, termios.TIOCSTI, '\n')

    termios.tcsetattr(tty, termios.TCSANOW, old_attr)
