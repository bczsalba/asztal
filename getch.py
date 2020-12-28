# taken and edited from https://code.activestate.com/recipes/134892/
# fun note: it was posted 18 years ago and still works!
# originally written by Danny Yoo

import os, sys, tty, codecs, select, termios, re
from contextlib import contextmanager

# functions for future multiline support
def clean_ansi(s):
    return re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]').sub('', s)

def real_length(s):
    return len(clean_ansi(s))

def break_line(_inline,_len,_pad=0,_separator=' '):
    if _len == None or _separator not in _inline:
        return [_inline]

    # check if line is over length provided
    if real_length(_inline) > _len:
        clean = clean_ansi(_inline)
        current = ''
        control = ''
        lines = []
        pad = lambda l: (_pad*' ' if len(l) else '')

        for i,(clen,real) in enumerate(zip(clean.split(_separator),_inline.split(_separator))):
            # dont add separator if no current
            sep = (_separator if len(current) else "") 

            # add string to line if not too long
            if len(pad(lines)+control+_separator+clen) <= _len:
                current += sep + real
                control += sep + clen

            # add current to lines
            elif len(current):
                lines.append(pad(lines)+current)
                current = real
                control = clen

        # add leftover values
        if len(current):
            lines.append(pad(lines)+current)

        return lines

    # return original line in array
    else:
        return _inline.split('\n')


# this needs to be here in order to have arrow keys registered
# from https://github.com/kcsaff/getkey
class OSReadWrapper(object):
    """Wrap os.read binary input with encoding in standard stream interface.
    We need this since os.read works more consistently on unix, but only
    returns byte strings.  Since the user might be typing on an international
    keyboard or pasting unicode, we need to decode that.  Fortunately
    python's stdin has the fileno & encoding attached to it, so we can
    just use that.
    """
    def __init__(self, stream, encoding=None):
        """Construct os.read wrapper.
        Arguments:
            stream (file object): File object to read.
            encoding (str): Encoding to use (gets from stream by default)
        """
        self.__stream = stream
        self.__fd = stream.fileno()
        self.encoding = encoding or stream.encoding
        self.__decoder = codecs.getincrementaldecoder(self.encoding)()

    def fileno(self):
        return self.__fd

    @property
    def buffer(self):
        return self.__stream.buffer

    def read(self, chars):
        buffer = ''
        while len(buffer) < chars:
            try:
                buffer += self.__decoder.decode(os.read(self.__fd, 1))
            except KeyboardInterrupt:
                buffer = "SIGTERM"
                break
        return buffer

class InputField:
    """ Example of use at the bottom of the file """
    def __init__(self,pos=None,linecap=0,default="",xlimit=None,ylimit=None):
        # set up instance variables
        self.lines = break_line(default,xlimit)
        self.xcursor = len(self.lines[-1])
        self.ycursor = len(self.lines)-1
        self.value = default
        self.selected = '' 
        self.selected_start = 0
        self.selected_end = 0

        # TODO
        self.linecap = linecap
        self.xlimit = xlimit
        self.ylimit = ylimit

        # set position as needed
        if pos == None:
            _,tHeight = os.get_terminal_size()
            self.x = 0
            self.y = tHeight-len(self.lines)+1
        else:
            self.x,self.y = pos

        # disable cursor
        self.set_cursor(False)
        # print
        self.print()

    def send(self,key):
        # delete char before cursor
        if key == "BACKSPACE":
            if self.xcursor > 0:
                index = self.get_index()
                left = self.value[:index-1]
                right = self.value[index:]
                self.value = left+right
                self.lines = break_line(self.value,self.xlimit)
                self.xcursor -= 1

        # move left
        elif key == "ARROW_LEFT":
            self.xcursor = max(self.xcursor-1,0)

        # move right
        elif key == "ARROW_RIGHT":
            self.xcursor = min(self.xcursor+1,len(self.lines[self.ycursor]))

        # TODO: history navigation, toggleable
        elif key == "ARROW_DOWN":
            self.ycursor = min(len(self.lines)-1,self.ycursor+1)

        elif key == "ARROW_UP":
            self.ycursor = max(0,self.ycursor-1)
            

        # TODO
        elif key == '\n':
            pass

        else:
            # TODO
            if key == "ENTER":
                if self.allow_multiline:
                    key = "\n"
                else:
                    key = ""

            # add character at cursor
            ## get index in value
            index = self.get_index()

            left = self.value[:index]
            right = self.value[index:]
            old_lines = self.lines
            self.value = left+key+right

            new = self.lines[self.ycursor]+key

            self.lines = break_line(self.value,self.xlimit)
            diff = len(self.lines) - len(old_lines)
            self.ycursor += diff
            self.xcursor += len(key)
            if diff:
                self.xcursor = 0
            #line = self.lines[self.ycursor]
            print('\033[0;130H',self.lines)

            #self.xcursor = min(self.xcursor+1,len(line)-1)

                
    def get_index(self,xy=None):
        if xy == None:
            x = self.xcursor
            y = self.ycursor
        else:
            x,y = xy

        return sum(len(w) for w in self.lines[:y]) + x


    # enable/disable (terminal) cursor
    def set_cursor(self,value):
        if value:
            print('\033[?25h')
        else:
            print('\033[?25l')

    # reset self.value
    def clear_value(self):
        self.wipe()
        self.value = ''
        self.cursor = len(self.value)
        self.print()

    # set value, cursor location, pass highlight
    def set_value(self,target,cursor=None,highlight=True):
        # clear space
        self.wipe()

        # set new value
        self.value = target

        # set cursor auto
        if (cursor == None and len(self.value)) or (cursor and cursor > len(self.value)-1):
            self.cursor = max(len(self.value)-1,0)
    
        # set cursor manual
        elif cursor:
            self.cursor = cursor

        # print self
        self.print(highlight=highlight)
 
    # clear the space occupied by input currently
    def wipe(self):
        for i,l in self.lines:
            y = len(lines)-1-i
            sys.stdout.write(f'\033[{self.y-y};{self.x}H'+(len(l)+2)*' ')
        sys.stdout.flush()

    # print self, flush and show highlight if set
    def print(self,flush=True,highlight=True):
        # set up two sides 
        lines = self.lines.copy()
        cursor_line = self.lines[self.ycursor]
        index = self.get_index()
        right = self.value[index+1:]
        leftindex = sum(len(l) for l in lines[:self.ycursor])
        #left = self.value[leftindex:index]
        left = lines[self.ycursor][:self.xcursor]

        # get char under cursor to highlight
        if self.xcursor > len(cursor_line)-1 or len(cursor_line) == 0:
            charUnderCursor = ' '
        else:
            charUnderCursor = cursor_line[self.xcursor]

        # set highlighter according to highlight param
        highlighter = ('\033[47m\033[30m' if highlight else '')

        # construct line
        line = left + highlighter + charUnderCursor + '\033[0m' + right

        lines[self.ycursor] = line

        for i,l in enumerate(reversed(lines)):
            # clear current
            sys.stdout.write(f'\033[{self.y-i};{self.x}H' + ' '*(len(l)+2))
            # write to stdout
            sys.stdout.write(f'\033[{self.y-i};{self.x}H'+l)

        # flush if needed
        if flush:
            sys.stdout.flush()

    def select(self,start=None,end=None):
        from client import dbg

        if start > end:
            temp = end
            end = start
            start = temp

        if start == None or start < 0:
            start = self.cursor
        if end == None or end > len(self.value)-1:
            end = len(self.value)-1

        end += 1

        left = self.value[:start]
        selected = self.value[start:end]
        right = self.value[end:]

        highlight = '\033[47m\033[30m'

        self.selected = selected
        self.selected_start = start
        self.selected_end = end
        
        self.wipe()

        line = left+highlight+selected+'\033[0m'+right

        # write to stdout
        sys.stdout.write(f'\033[{self.y};{self.x}H'+line)
        sys.stdout.flush()


class _Getch:
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()
        self.keycodes = self.impl.keycodes
        

    def __call__(self):
        key = self.impl()

        # return human-readable name if found
        if key in self.keycodes.keys():
            return self.keycodes[key]
        else:
            return key

class _GetchUnix:
    def __init__(self):
        import tty, sys, select
        self.keycodes = {
            # SIGNALS: not captured currently
            "\x03": "SIGTERM",
            "\x1a": "SIGHUP",
            "\x1c": "SIGQUIT",
            # CONTROL KEYS
            "\x0e" : "CTRL_N",
            # TEXT EDITING
            "\x7f": "BACKSPACE",
            "\x1b": "ESC",
            "\n": "ENTER",
            "\r": "ENTER",
            "\t": "TAB",
            # MOVEMENT
            "\x1b[A": "ARROW_UP",
            "\x1b[B": "ARROW_DOWN",
            "\x1b[C": "ARROW_RIGHT",
            "\x1b[D": "ARROW_LEFT",
        }
        self.stream = OSReadWrapper(sys.stdin)

    @contextmanager
    def context(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        try:
            yield
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def get_chars(self):
        with self.context():
            yield self.stream.read(1)

            while select.select([sys.stdin,], [], [], 0.0)[0]:
                yield self.stream.read(1)

    def __call__(self):
        buff = ''
        for c in self.get_chars():
            buff += c

        return buff

class _GetchWindows:
    def __init__(self):
        import msvcrt
        # TODO: add more compatibility
        self.keycodes = {
            "\x1b": "ESC",
            "\n": "ENTER",
            "\r": "ENTER",
            "\x7b": "BACKSPACE",
        }

    def __call__(self):
        global key

        import msvcrt
        return msvcrt.getch()


# clean namespace
getch = _Getch()

# example code
if __name__ == "__main__":
    infield = InputField(default="Welcome!",xlimit=10)
    #infield.print()

    while True:
        key = getch()
        # catch ^C signal to exit
        if key == "SIGTERM":
            # re-show cursor (IMPORTANT!)
            infield.set_cursor(True)
            break
        else:
            infield.send(key)
        infield.print()
