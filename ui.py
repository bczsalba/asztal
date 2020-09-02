#!/usr/bin/env python3

#imports
import os
import shutil
import sys
import re
import json
import time
import signal
import math
import random
import datetime
from getpass import getpass

#used for log file
tstart = datetime.datetime.now()

# detect program exit
def onExit(signum,frame):
    dbg('exiting')
    sys.exit()

signal.signal(signal.SIGINT,onExit)

#importing functions
from asztal import vrs,curdir
from settings import *

daysOfWeek = ['Monday','Tuesday','Wednesday','Thursday','Friday']
cursorUp = '\033[1A'
silence = '\033[1A'+'\033[K'

#color
def getColors():
    c = {}
    if customColors == 'True' and 'colors.py' in os.listdir(curdir):
        import colors as cols
        for name,value in zip(['one','two','three','four','five'],cols.colors):
            c[name] = f'\033[38;5;{value}m'

    else:
        c['one'] = '\033[31m'            #red
        c['two'] = '\033[38;5;166m'      #orange/brown
        c['three'] = '\033[38;5;226m'    #yellow
        c['four'] = '\033[38;5;156m'     #light green
        c['five'] = '\033[32m'           #green
    
    c['fade'] = '\033[38;5;245m'
    return [c['fade'],c['one'],c['two'],c['three'],c['four'],c['five']]

colors = getColors()
cmod = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'italic': '\033[3m',
        'underline': '\033[4m'
}

if not 'animTime' in globals():
    animTime = 10

#=======================================functions==============================================

#clear the screen, has a forced toggle, also show what function called it in soft mode
def clr(f=0):
    global printedLines

    printedLines = 0
    if animation == 'scrolling' and debug == 'False' and not f: return

    if not debug == 'True' or f == 1:
        os.system('cls' if os.name == 'nt' else 'clear')
    else:
        caller = sys._getframe().f_back.f_code.co_name
        print(caller.center(40,'-'))
 
#toggleable print, logging
def dbg(*args,f=0,time=1,show=1):
    _pad = '     '

    info = ' '.join([repr(a) for a in args])
    if (debug == 'True' or f == 1) and show and time: 
        print(f'{_pad}{info}')

    with open(os.path.join(curdir,'log'),'a') as log:
        time_format = (str(datetime.datetime.now()-tstart).split(':')[-1][:7] if time else '\n')
        try:
            for d in info.split('\n'):
                log.write(f'{time_format}: {d}\n')
        except AttributeError:
            for d in repr(info).split('\n'):
                log.write(f'{time_format}: {d}\n')

def qInp(s=''):
    out = input(s+cursorUp)
    print(silence)
    return out

#printing with delay of animTime
def tprint(*args,**kwargs):
    global printedLines
    
    lines = 0
    for a in args:
        lines += a.count('\n')

    printedLines += lines+len(args)
    print(*args,**kwargs)
    if not debug == 'True' and animTime: time.sleep(animTime*0.001)

#go to x,y with ansi cursor codes
def goto(x=0,y=0):
    print(f"\033[{y};{x}H")

#pad bottom to tHeight
def padBottom(offset=0):
    for _ in range(tHeight-offset-2-printedLines):
        tprint('\033[K')

#handles function recalling in scrolling mode, so it doesnt reprint and looks all pretty
def handleRecall():
    if animation == 'classic' or debug == 'True': return
    
    func = sys._getframe().f_back.f_back.f_code.co_name
    caller = sys._getframe().f_back.f_code.co_name

    if caller == func:
        recalled = True
    else:
        recalled = False
    
    if recalled:
        goto(0,0)
        print('\033[K')
        goto(0,0)

try: from settings import tWidth
except Exception: 
    dbg("No tWidth given, defaulting to dynamic.")
    tWidth,tHeight = os.get_terminal_size()

border = (round(tWidth/2)-1)*'-='+'-'

#from https://stackoverflow.com/a/38662876; rid string of ansi sequences
def clean_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

#breaks _inline with (\n_padLen*' ')-s if it's longer than _len
def breakLine(_inline,_padLen=0,_len=tWidth,_separator=' '):
    if len(clean_ansi(_inline )) > _len:
        _line = '' #line with ansi
        _cline = '' #line without ansi

        #iterating through an array of strings without and with ansi characters, doing the same changes to them
        for i,(c,l) in enumerate(zip(clean_ansi(_inline).split(_separator),(_inline.split(_separator)))):

            #if the clean line since last linebreak is not too long
            if len(_cline.split('\n')[-1]+c) < _len:
                #adding the next string to the lines
                _cline += (_separator if not _cline == '' else '') + c
                _line += (_separator if not _line == '' else '') + l
            
            elif not any(nl == '' for nl in [l,c]):
                #adding a newline, padding and the next string to the lines
                _pad = _padLen*' '
                _cline += f'{_separator}\n{_pad}{c}'
                _line += f'{_separator}\n{_pad}{l}'

        #return (' ' if len(_line.split('\n')) >= 1 else '')+_line
        #return (' ' if len(clean_ansi(_inline)) > tWidth else '') + _line
        return _line
    else:
        return _inline

# pads string to center in _len
def padded(_str,_len=tWidth):
    mult = round( (_len-len(clean_ansi(_str)))/2 )
    pad = mult*' '
    return pad+_str

def underline(s,index=None,clr=''):
    out = ''
    for i,c in enumerate(s):
        if index == None or index == i:
            out += cmod['underline']+clr+c+cmod['reset']
        else:
            out += clr+cmod['bold']+c+cmod['reset']
    return out

def makeHint(s,col='',_index=None,noUnderline=False):
    if '-' in s:
        ind = int(s.index('-')+1)
        s = s[:ind-1]+s[ind:]
        ind -= 1

    elif _index:
        ind = _index
    elif noUnderline:
        ind = len(s)+1
    else:
        ind = 0

    
    return cmod['bold']+'[ '+underline(s,ind,cmod['bold']+col)+cmod['bold']+' ]'+cmod['reset']

def spaceHint(hints,spacer=' '):
    spaced = spacer.join(hints)
    if not len(clean_ansi(spacer.join(hints))) > tWidth:
        return padded(spaced)
    else:
        maxLen = max([len(clean_ansi(h)) for h in hints])
        return '\n'.join([int((tWidth-maxLen)/2)*' '+h for h in hints])    

def printBetween(s,_len=tWidth,_char='|',_pad=1,_offset=0,noPrint=False):
    retrstr = _char+' '*_pad+s+cmod['reset']+(_len-len(clean_ansi(s))-3-_pad)*' '+_char
    retrstr = _offset*' '+retrstr
    if noPrint:
        return retrstr
    else:
        tprint(retrstr)

# approximate detection
def approximateInput(inp,lst,index=False):
    for e in lst:
        for i in range(len(e)+1):
            if inp == e[:i].lower():
                i = lst.index(e)
                if index:
                    return i
                else:
                    return e

#=============================display===============================

#title screen, gets/returns selection
def showTitle(_choice=None,bday=False,noPrint=False,localAnimTime=animTime):
    global mode,path,titleArt
    
    if not 'mode' in globals():
        mode = 'offline'
    modeStr = ('' if mode == 'online' else f'({mode})')

    items = [name,f'v{vrs} {modeStr}','grades','recents','timetable','profiles','settings','update']

    # sleep well lil guy
    def wobbly():
        from title_art import wobbly
        small = wobbly[0]
        big = wobbly[1]
        speech = wobbly[2].split('\n')

        for i in range(tWidth):
            #i -= (1 if random.randint(0,10) == 10 else 0)
            wobblyLines = (big if i % 2 == 0 else small).split('\n')
            clr(f=1)
            maxlen = max(len(l) for l in wobblyLines)
            for wi,l in enumerate(wobblyLines):
                l += (maxlen-len(l))*' '

                inRange = (i < maxlen)
                speak = (i == tWidth//2)
                line = (min((i-maxlen),tWidth-maxlen)*' ' if not inRange else '')+(l[len(l)-i:] if inRange else l)+(speech[wi+1] if speak else '')
                wobblyLines[wi] = line
            wobbly = '\n'.join(wobblyLines)

            print((((tHeight//2))-3)*'\n')
            #print(random.randint(0,1)*'\n')
            print(wobbly)
            #print('\n\n-wobble wobble')
            if speak:
                time.sleep(2)
            else:
                time.sleep(random.randint(5,10)/100)
        clr(f=1)
        print(tWidth//2*'\n'+'   Goodnight lil fella...'+'\n'+'   Wobbly (Jun. 15-27, 2020)'+'\n')
        if qInp():
            pass

        return False

    ## needs to be a function so we can easily refresh it
    def getTitleArt():
        from random import randint
        from title_art import titles
        _titleArt = titles[randint(0,len(titles)-1)]
        while any([len(l) > tWidth-1 for l in _titleArt.split('\n')]):
            _titleArt = titles[randint(0,len(titles)-1)]
        return _titleArt

    ## function to handle input
    def handleInput(inp,noInp=False):
        functions = [f.replace('show','').lower() for f in globals() if callable(globals()[f]) and 'show' in f]
        options = [o for o in items[2:]]
        choice = None
        if len(inp) > 1:
            choice = approximateInput(inp,functions)

        if choice == None:
            try:
                choice = options[int(inp)]
            except (ValueError,IndexError) as e:
                #if debug == 'True':
                #    raise e
                return False
        
        fun = globals()['show'+choice.title()]
        clr()
        fun()
        
        if not noInp:
            inp = qInp('')
            if inp == '':
                goBack(1,'')


    if not 'titleArt' in globals():
        ## show birthday sprite
        if bday:
            from title_art import bday
            titleArt = bday
        else:
            titleArt = getTitleArt()
    

    if not _choice and not noPrint:
        ## display ui
        clr()
        dbg('title called')

        titleLines = titleArt.split('\n')
        cols = colors[1:].copy()+colors[1:].copy()
        cols.reverse()

        tprint('\n\n\n\n')
        maxtlen = max(len(l) for l in titleLines)
        maxlen = int(max(len(clean_ansi(l)) for l in items)*1.37)
        
        npad = 1-(maxlen % 2)
        for l in titleLines:
            tprint(' '+padded(cmod['bold']+l+cmod['reset']))

        if len(titleLines) > 2:
            tprint(round(tWidth/2)*' '+'|'+cmod['reset'])
        else:
            tprint('')
        
        borderlen = maxlen-npad

        tprint(cmod['bold']+' '+padded((borderlen)*'-'))
        for i,s in enumerate(items):
            c = (cols[i] if i > 1 else '')
            i -= 1
            index = (str(i-1)+'. ' if i > 0 else '')
            l = ' '+padded(printBetween(index+c+s,_len=borderlen+1,noPrint=True,_char=cmod['bold']+'|'))
            tprint(l)

        tprint(' '+padded((borderlen)*'-')+cmod['reset'])
        padBottom()

    #sets choice
    if _choice == None:
        choice = qInp('')
    else:
        choice = _choice
    dbg(f'choice: {(choice if not choice == "" else "None")}')

    if choice == '':
        showTitle(localAnimTime=0)

    elif not handleInput(choice):
        # refresh title art
        if choice == 'r':
            titleArt = getTitleArt()
            showTitle()
        
        elif choice == 'wobbly':
            wobbly()
            showTitle()

        #unrecognized choice
        else:
            dbg(f'choice else: '+choice)
            showTitle()
    else:
        sys.exit()  

#timetable displayer
def showTimetable(_day=None,_lesson=None):
    clr()
    dbg('showTimetable called with '+str(_day)+' '+str(_lesson))
    import datetime
    from settings import ttdefault

    #def printBetween(s,pad=3):
    #    start = borderIndex*' '+cmod['bold']+'|'+cmod['reset']
    #    mid = pad*' '+s
    #    end = (borderLen-len(clean_ansi(s))-pad-2)*' '+cmod['bold']+'|'+cmod['reset']
    #    tprint(start+mid+end)
    
    ## get closest weekday to d
    def getClosestDay(d=None):
        '''0:monday, 6: sunday'''

        results = []
        for day in range(len(timetable)):
            temp = abs(d-day)
            results.append(temp)

        if results == []:
            return 0

        return results.index(min(results))


    # detect if recalled by itself
    handleRecall()
    
    ## safeguard
    try:
        from marks import timetable
    except Exception as e:
        dbg(str(e))
        return
    
    if len(timetable) == 0:
        for _ in range(0,4):
            day = [
                    {
                        "date": "1970-01-01",
                        "start": "00:00:00",
                        "end": "00:00:00",
                        "subject": "No class for today",
                        "classroom": "Home, probably",
                        "teacher": "no one",
                    }
                ]
            timetable.append(day)

    ## logic to determine needed day and lesson values
    today = datetime.datetime.today().weekday()
    if not _day == None:
       day = getClosestDay(_day)

    else:
        day = getClosestDay(today)
            
    if not _lesson == None:
        lesson = _lesson
    else:
        current = datetime.datetime.now()
        #current = datetime.datetime.strptime('2020-06-04 11:21:00','%Y-%m-%d %H:%M:%S')
        #dbg(current)

        ## if we're looking at today show the ongoing/closest lesson
        if not today == day:
            lesson = 0
        else:
            for i,l in enumerate(timetable[day]):
                #dbg(l)
                start = datetime.datetime.combine(datetime.datetime.today(),datetime.datetime.strptime(l['start'],'%H:%M:%S').time())
                tempTime = current-start
                if not 'minTime' in locals() or (datetime.timedelta(0) < tempTime < minTime):
                    minTime = tempTime
                    lesson = i

    if len(timetable[day]) == 0:
        dbg('no timetable for this day')

    ## printing
    # body lines
    lines = []
    for i,l in enumerate(timetable[day]):
        for key in l.keys():
            l[key] = str(l[key])
        isCurrent = (i == lesson)
        index = cmod['bold']+str(i)+'. '
        subject = (colors[1] if isCurrent else '')+l['subject']
        lines.append(index+subject+cmod['reset'])
        
        # "unfolds" currently selected lesson
        if isCurrent:
            pad = 3
            startend = colors[0]+l['start']+'-'+l['end']+cmod['reset']
            lines.append(pad*' '+startend)
            for v in ['teacher','classroom']:
                line = pad*' '+colors[0]+l[v]+cmod['reset']
                lines.append(line)
    
    # top lines
    maxlen = max([len(clean_ansi(l)) for l in lines])
    borderLen = max(33,maxlen+9)
    dayStr = daysOfWeek[day].lower()
    smolBorder = (dayStr+'-'*(borderLen-len(dayStr))).center(tWidth)
    borderIndex = smolBorder.index(dayStr[0])

    # top print
    tprint('\n')
    tprint(border)
    tprint('\n')
    tprint(cmod['bold']+smolBorder+cmod['reset'])    
    
    # body print
    for l in lines:
        printBetween(2*' '+l,_len=borderLen+1,_offset=borderIndex,_char='|\033[K')
   
    # hint bar
    resetHint = underline('reset',0,colors[1])
    if ttdefault == 'l':
        lessonHint = colors[4]+cmod['bold']+'num: change lesson'+cmod['reset']
        dayHint = underline('d+num: change to day',14,colors[3]+cmod['bold'])
    else:
        dayHint = colors[3]+cmod['bold']+'num: change to day'+cmod['reset']
        lessonHint = underline('l+num: change lesson',14,colors[4]+cmod['bold'])
    
    #hints = '  '.join([locals()[v] for v in locals() if 'hint' in v.lower()])
    hints = [resetHint,lessonHint,dayHint]
    for i,h in enumerate(hints):
        hints[i] = cmod['bold']+'[ '+h+cmod['bold']+' ]'+cmod['reset']


    # constructing dayLegend
    dayLegend = ''
    for i,d in enumerate(daysOfWeek):
        d = d[0].lower()
        if i == day:
            d = colors[4]+d
        dayLegend += cmod['bold']+d+cmod['reset']
    dayLegend += '\033[K'
    
    # bottom print
    tprint(cmod['bold']+borderIndex*' '+(borderLen-len(clean_ansi(dayLegend)))*'-'+dayLegend+'\n\033[K\n\033[K')
    #for h in sorted(hints,key=lambda x: len(clean_ansi(x))):
    #    tprint(padded(h))
    tprint(spaceHint(sorted(hints,key=lambda x: len(clean_ansi(x))))+'\n\033[K')
    tprint(border)
    padBottom()

    
    ## input
    # formatting input to always start with l/d
    inp = ''.join(qInp('').rstrip().split(' '))
    if inp.isdigit():
        inp = ttdefault+inp #formatting it to l/d+inp format depending on ttdefault
    dbg('inp: '+inp)

    # exit
    if inp == '':
        showTitle()
    else:
        # handle input
        if not inp[0] in ['d','l','r']:
            showTimetable()
        else:
            dbg(f'current: l{lesson} | d{day}')
            if inp[0] == 'd':
                try:
                    selectedDay = int(inp[1:])-1
                    selectedLesson = lesson
                except Exception as e:
                    dbg(str(e))
                    showTimetable()
                    
            elif inp[0] == 'l':
                try:
                    selectedLesson = int(inp[1:])
                    selectedDay = day
                except Exception as e:
                    dbg(str(e))
                    showTimetable()
            else:
                showTimetable()

            showTimetable(selectedDay,selectedLesson)

#main displayer function
def showGrades(noInp=False,inp=None):
    global sublist,getAvg
   
    def roundUp(n):
        if n - math.floor(n) < 0.5:
            return math.floor(n)
        return math.ceil(n)

    #grade simulation menu
    def menuSimulate(_sub=None,args=None,_skip=0):
        dbg('menuSimulate called with '+repr(args))
        global allGrades
        clr()

        handleRecall()
        
        ###setup
        #if the function is being called by itself it doesnt reset the values
        if _skip == 0:
            rawInp = ''.join([''.join(a.split(' ')) for a in args])
       
            #if len(rawInp) == 1:
            #    dbg('shits too short')
            #    gradesMenu()
            #    clr()

            #filters out grades from input
            for i,char in enumerate(rawInp):
                if not char.isdigit():
                    _grades = rawInp[i+1:]
                    break
        
            #if no sub is given filters out its index from input
            if _sub == None:
                _index = int(rawInp[:i])
        else:
            _grades = [str(a) for a in args]
      
        #if no sub is provided it gets assigned based on index, grades get assigned based on _grades
        sub = (sublist[_index] if _sub == None else _sub)
        if not 'allGrades' in globals():
            allGrades = [v for v in marks if v['subject'] == sub and v['type'] == 'MidYear' and isinstance(v['value'],int)]
        dbg(f'sub: {sub}\nlen(aG): {len(allGrades)}')
        
        
        ###string assignment/formatting
        #assigning the needed arrays
        simGrades = ([int(g) for g in [clean_ansi(v) for v in _grades]] if '_grades' in locals() else [])
        actGrades = [(cmod['bold'] if v['weight'] == '200%' else '')+str(v['value']) for v in allGrades]
        
        dbg(f'sim,act: {str(simGrades)},{actGrades}')

        #colors, formats grade strings
        actGradesColored = ",".join([f'{colors[int(clean_ansi(g))]}{g}{cmod["reset"]}' for g in actGrades])

        #avg calculations and formatting
        allGradesInt = []
        for v in allGrades:
            for _ in range(int(v['weight'][0])):
                allGradesInt.append(v['value'])
        
        avg = ( sum(allGradesInt+simGrades)/len(allGradesInt+simGrades) if len(allGradesInt+simGrades) > 0 else 0)
        avgValue = f'{colors[int(avg)]}{cmod["bold"]}{avg}{cmod["reset"]}'

        #assigning formatted strings
        avgStr = cmod['bold']+(f'Current average: ' if simGrades == [] else 'Simulated average: ')+cmod['reset'] + avgValue
        subStr = f'{cmod["bold"]}{sub}{cmod["reset"]}: '
        actual = f'{actGradesColored}' 
        simulated = (f',{",".join([cmod["italic"]+colors[0]+str(a) for a in simGrades])}{cmod["reset"]}' if len(simGrades) > 0 else '')
        hints = ['num to add','-num to remove']
        cols = [colors[4],colors[1]]
        hint = '  '.join([makeHint(s,cols[i],noUnderline=True) for i,s in enumerate(hints)])

        #formatting grades with line breaking
        _line = f'{cmod["bold"]}Grades:{cmod["reset"]} '+actual+simulated
        _sep = ','
        _padLen = len(f'Grades: ')
        _len = tWidth-5
        gradesFormatted = breakLine(_line,_padLen,_len,_sep)

        
        ###printing
        tprint('\n\n',padded(subStr))
        tprint(border)
        for l in gradesFormatted.split('\n'):
            printBetween(l)
        
        printBetween('')
        printBetween(avgStr)
        printBetween('')
        
        #body (counts of values)
        for v in [1,2,3,4,5]:
            cnt = simGrades.count(v)
            valstr = f' {v}s: {cmod["bold"]}{colors[v-1]}{cnt}{cmod["reset"]}'
            #if the count is more than 0 it prints
            if not cnt == 0: 
                printBetween(valstr)
        
        #if there is any count printed it prints an extra line for spacing
        if max([simGrades.count(v) for v in [1,2,3,4,5]]) > 0:
                printBetween(' ')

        #help+bottom border
        tprint(border)
        tprint('\033[K')
        tprint(padded(hint))
        padBottom()

        ###input
        #get input, format it so the program doesnt clean exit

        inp = ''.join(qInp('').strip().split(' '))
       
        #input handling
        if not inp == '': #if not exiting
            if inp == 'clr':
                #clr(f=1)
                print('\033[2J')
                del globals()['allGrades']
                menuSimulate(sub,[])

            elif not '-' in inp: #if not trying to remove grades
                for c in inp: #going through inp
                    try: c = int(clean_ansi(c)) #tries to int(c)
                    except: c = 0 #assigns c to 0 if failed to skip the rest of the if gate
                    if 0 < c <= 5: #if c is a valid grade
                        simGrades.append(c) 

            else: #if in remove mode
                try: c = int(inp[inp.index('-')+1]) #tries to int the value after '-'
                except: dbg(f'Invalid input: {inp}');menuSimulate(sub,simGrades,1) #dbg-ing input, recalling function

                if 0 < c <= 5: #if c is a valid grade
                    
                    if c in simGrades:
                        rSim = simGrades[::-1]
                        del simGrades[len(simGrades)-1-rSim.index(c)]
                    else:
                        for i,v in enumerate(reversed(allGrades)):
                            if v['value'] == c:
                                allGrades.remove(allGrades[len(allGrades)-1-i])
                                break
                    
            menuSimulate(sub,simGrades,1) #recalling function with new values

        else:
            dbg('exiting')
            del globals()['allGrades'] #removing allGrades array if exiting so that its not kept for other subjects
            menuInfo(sublist.index(sub))
   
    #grades info menu
    def menuInfo(_choice=None):
        dbg(f'menuInfo called with {_choice}')
        
        #sets choice if not given already
        if _choice == None:
            _choice = qInp('')
        else:
            if not isinstance(_choice,int): #needed to fix a bug where if you entered an invalid value it would clean exit cause python
                for char in _choice:
                    if not char.isdigit() and not char == ' ':
                        mode = char    
                        break
                    else:
                        mode = None
            else:
                mode = None

        dbg(f'choice: {_choice}')

        if mode == 's':
            menuSimulate(args=_choice) 
        
        #tries to assign choice to an element of subjectsList
        try: choice = sublist[int(_choice)]
        except Exception as e:
            dbg(f'Assigning choice: {str(e)}')
            showTitle('0')
        
        clr()

        i = 0 #index in grades
        lines = [] #array of lines

        
        #looping through the elements of the choice subject's list
        for v in [v for v in reversed(marks) if v['subject'] == choice and v['type'] == 'MidYear']:   
            #value
            if isinstance(v['value'],str):
                value = f'{cmod["italic"]}text{cmod["reset"]}'
            else:
                value = f'{cmod["bold"]}{colors[v["value"]-1]}{v["value"]}{cmod["reset"]}'

            #weight
            weight = v['weight']

            #theme
            theme = f'{v["theme"]}{cmod["reset"]}'
            #theme = f'{cmod["italic"]}{v["theme"]}{cmod["reset"]}'

            #date
            date = f'{colors[0]}{v["date"]}{cmod["reset"]}'

            #time
            _time = f'{colors[0]}{cmod["italic"]}{v["time"]}{cmod["reset"]}'
            
            #add to lines
            lines.append(f'{date} ~ {value}*{weight}: {theme}')

        dbg(f'lines: {len(lines)}')

        #going through lines, finding if any are longer than the terminal-1 and reassigning them with linebroken versions
                #length of longest line
        _length = max(len(clean_ansi(l)) for l in lines)
        col = colors[int(getAvg(choice))]
        _avg = col+getAvg(choice,_ret='str')+cmod['reset'] #avg value
        
        #top border
        tprint('\n'+padded(cmod['bold']+f' {choice}: {_avg}'+cmod['reset'])+'\n'+border)
            
        for li,l in enumerate(lines):
            cl = breakLine(l,len(clean_ansi(f'{lines[li].split(":")[0]}  ')),tWidth-5,' ',)
            for n in cl.split('\n'):
                printBetween(n)
            
                if tWidth < 80:
                    printBetween('')

        #bottom border
        tprint(border)
        tprint('\n'+padded(makeHint('simulate',colors[4])))
        padBottom()
        
        #exit
        inp = qInp('')
        
        try: 
            if inp == '':
                showTitle('0')

            if inp.lower()[0] == 's':
                menuSimulate(_sub=choice,args=inp)
            else:
                dbg(sublist.index(choice))
                menuInfo(sublist.index(choice))
        except Exception as e:
            dbg(e)
            if debug == 'True':
                raise e
            if inp == '':
                showTitle('0')
            else:
                pass

    #overall info menu
    def menuOverall(_mode='current',_grades=None,_subjects=None):
        def getCurrent():
            mode = 'current'
            return avgs.copy()

        def getTerm(term):
            grades = []
            for sub in sublist:
                sub = sub.replace('* ','')
                index = None
                for i,e in enumerate(term):
                    if e['subject'] == sub:
                        index = i
                        break
                if not index == None:
                    grades.append(term[index]['value'])
                else:
                    grades.append(cmod['reset']+'.')

            return grades

        def getHalf():
            mode = 'half'
            halfyears = [m for m in marks if m['type'] == 'felevi_jegy_ertekeles']
            return getTerm(halfyears)
            
        def getEnd():
            mode = 'end'
            endyears = [m for m in marks if m['type'] == 'evvegi_jegy_ertekeles']
            return getTerm(endyears)
            
        def getDifference():
            mode = 'difference'
            diff = []
            current = (getEnd() if len(getEnd()) > 0 else avgs)
            for (o,n) in zip(getHalf(),current):
                if n == o:
                    s = colors[o-1]+str(n)+cmod['reset']+' '
                    diff.append(s)
                    continue

                cols = []
                for c in (o,n):
                    cols.append(colors[1] if isinstance(c,str) else colors[c-1])
                gradestr = [cmod['reset']+(colors[0] if n == o else cols[i])+str(c) for i,c in enumerate([o,n])]
                s = '->'.join([g+cmod['reset'] for g in gradestr])
                diff.append(s)
            
            #maxlen = max(len(clean_ansi(d.split('->')[-1])) for d in diff)
            #for i,d in enumerate(diff):
            #    curlen = min(len(clean_ansi(d.split('->')[-1])),6)
            #    dbg(maxlen,curlen)
                #diff[i] = d.center(maxlen-curlen)
            #    diff[i] = d+(maxlen-curlen)*' '
                #print(diff[i])
                

            return diff
        
        def edit():
            mode = 'edit'
            return avgs
        
        handleRecall()

        # set up subjects array and mode
        if not _subjects: subjects = sublist
        else: subjects = _subjects.copy()
        mode = _mode

        # get function from mode str
        fun = [f for f in locals() if mode in f.lower()][0]
        
        # set up grades array
        if _grades:
            grades = _grades.copy()
        else:
            grades = locals()[fun]()
        
        try:
            filtered = [g for g in grades if isinstance(g,int)]
            avg = round(sum(filtered)/len(filtered),4)
            avgstr = colors[round(avg)-1]+str(avg)+cmod['reset']
        except (TypeError,ZeroDivisionError) as e:
            if mode in ['difference','edit']:
                avgstr = ''
            else:
                dbg(str(e))
                avgstr = colors[1]+'TBA'+cmod['reset']

        clr()
        borderLen = longest+12
        
        # get hint array, color and color, print them
        hints = ['half term','current','end of term','difference','ed-it']
        col = [(colors[4] if mode in h.replace('-','') else colors[1]) for h in hints]
        hint = spaceHint([makeHint(h,col=c) for h,c in zip(hints,col)])
        title = 'overall'
        subBorder = cmod['bold']+title
        tprint('\n\n')
        tprint(padded(subBorder+(borderLen-len(clean_ansi(subBorder+avgstr))-1)*'-'+avgstr)+cmod['reset'])
        
        # print all the lines
        for i,(sub,gra) in enumerate(zip(subjects,grades)):
            subject = sub.replace('  ',' ')
            if mode == 'difference': 
                col = ''
            else:
                col = (colors[gra-1] if isinstance(gra,int) else colors[1])
            
            # shorten string values
            if isinstance(gra,str) and len(clean_ansi(gra.strip())) > 3:
                if mode == 'difference':
                    gras = gra.split('->')
                    val = '->'.join(['.',gras[1]])
                else:
                    val = gra[:4]+'..'
            else:
                val = str(gra)+cmod['reset']
            
            # if editing show indexes
            if mode == 'edit': 
                index = (2-len(str(i)))*'0'+str(i)+'. '
            else: 
                index = ''
            
            # construct lines, print them and sleep if needed
            value = col+val
            line = index+subject+': '
            pad = (borderLen-len(clean_ansi(line+value))-5)*' '
            line = line+pad+value+' '
            tprint(padded(printBetween(line,_len=borderLen,noPrint=True,_char=cmod['bold']+'|'+cmod['reset'])))

        # print bottom border
        tprint(padded(cmod['bold']+((borderLen-1)*'-'))+cmod['reset']+'\n')
        
        # print hints
        for h in hint.split('\n'):
            tprint(h)

        padBottom()
        
        # edit input section
        if mode == 'edit':
            choice = qInp('')
            if choice == '':
                menuOverall()
            elif choice.isdigit() and int(choice) in range(len(subjects)):
                sub = subjects[int(choice)]
                old = grades[int(choice)]
                clr(f=1)
                new = input('\n\n'+cmod['bold']+sub+': '+colors[old-1]+str(old)+cmod['reset']+cmod['bold']+' -> '+colors[4])
                tprint(cmod['reset'])
                clr(f=1)
                if new.isdigit() and int(new) in range(1,6):
                    grades[int(choice)] = int(new)
                    if not '* ' in sub:
                        subjects[int(choice)] = '* '+sub
                    menuOverall(_grades=grades,_subjects=subjects)
    
            else:
                inp = choice
         
        ## input
        if not 'inp' in locals(): inp = qInp('')
        valid = [(h[h.index('-')+1] if '-' in h else h[0]) for h in hints]
        dbg(valid)
        if inp.lower() in valid:
            modes = [h.split(' ')[0] for h in hints]
            vIndex = valid.index(inp.lower())
            mode = modes[vIndex].replace('-','')

        elif inp == '':
            if not mode == 'current':
                menuOverall('current')
            else:
                clr()
                globals()['sublist'] = [s.replace('* ','') for s in sublist]
                showGrades()
        menuOverall(_mode=mode)

    #sorting method, returns how many grades the subject has
    def getLen(sub):
        try: return len([m for m in marks if m['subject'] == sub])
        except: return 0
    
    #get avgs from list
    def getAvg(_sub,cm=None,_rnd=2,_ret='float'):
        _vals = []
        _len = 0
        
        #assigning sub name to not have spaces
        #_sub = ''.join(_sub.split(' '))

        #loops through values
        for i,val in enumerate([v for v in marks if v['subject'] == _sub]):
            #detects grades
            value = val['value']
            if not isinstance(value,int):
                continue
            _type = val['type']
            if not _type == 'MidYear':
                continue
            weight = int(val['weight'][0])
            weightedGrade = value * weight
            _vals.append(weightedGrade)
            _len += weight #adds however we added for weight(100%->1,200%->2)
        if _len == 0: _len = 1
        
        #sum of the grades
        _sum = sum(_vals)
        
        #assigns float value, padding
        _avgFloat = round(_sum/_len,_rnd)
        if len(str(_avgFloat)) < _rnd + 2:
            _pad = '0'
        else:
            _pad = ''

        #colorful return value
        if _ret == 'str':
            if cm == 'colored':
                _avgStr = cmod['bold'] + colors[round(_avgFloat)-1] + str(_avgFloat) + _pad + cmod['reset']
            else:
                _avgStr = str(_avgFloat) + _pad

            return _avgStr

        #numerical return value
        elif _ret == 'float':
            return _avgFloat
    
    #handler of color modes
    def colorHandler(_cm):
        #[0]: grade style
        #[1]: weight style 
        if _cm == 'full':
            return 'colored','weighted'
        
        elif _cm == 'partial':
            return 'colored','faded'
        
        elif _cm == 'grade':
            return 'colored','none'
        
        elif _cm == 'weight':
            return 'none','weighted'
        
        elif _cm == 'none':
            return 'none','none'
        
        else:
            return 'none','none'


    #for subSorter in settings so that it can use the builtin len
    globals()['len'] = len 
    #for reversed sorting with getAvg
    locals()['getAvgR'] = getAvg
    #for reversed getLen
    locals()['getLenR'] = getLen
    
    dbg(f'Terminal Width: {tWidth}')
    dbg(f'SubJlist contains {len(subjectsList)} elements.')
    
    #top border
    tprint('\n\n\n'+cmod['bold']+'asztal'.center(tWidth-3)+cmod['reset'])
    tprint(border)

    if not len(subjectsList):
        tprint((tHeight//2-printedLines)*'\n'+cmod['bold']+'No grades available.'.center(tWidth)+cmod['reset'])
        padBottom()
        tprint('\033[3A'+border+'\033[3B')
        return
     
    #gets the longest subject name
    for sub in subjectsList:
        if not 'longest' in locals() or longest < len(sub):
            longest = len(sub)+2
    
    #sorts subs according to criteria, prints them in '| subject |' form
    reverse = (1 if subSorter[-1] == 'R' else 0)
    glDict = (globals() if subSorter in globals() else locals())
    sublist = (subjectsList.copy() if subSorter == 'time' else sorted(subjectsList.copy(),key=glDict[subSorter],reverse=reverse))

    avgs = []
    for i,sub in enumerate(sublist): 
        gradeStyle = colorHandler(colorMode)[0] #colored,none
        weightStyle = colorHandler(colorMode)[1] #weighted,faded,none

        #start of gradestr
        avgs.append(roundUp(getAvg(sub,gradeStyle,_rnd=2)))
        index = ('0' if len(str(i)) < 2 else '')+str(i)
        gradestr = f'{index}. {sub}'+' '*(longest-len(sub))+f'[{getAvg(sub,gradeStyle,_ret="str")}] |: '
        
        #remove text grades
        grades = reversed([v for v in marks if isinstance(v['value'],int) and v['type'] == 'MidYear'])

        #sorting list of grades according to settings
        if gradeSorter == 'time':
            sortedGrades = grades
        elif gradeSorter == 'dec':
            sortedGrades = sorted(grades,reverse=True,key=lambda x: x['value'])
        elif gradeSorter == 'inc':
            sortedGrades = sorted(grades,key=lambda x: x['value'])

        #going through sorted grades, creating colored strings
        for i,v in enumerate(sortedGrades):
            if not v['subject'] == sub:
                continue


            value = v['value']
            if gradeStyle == 'colored':
                value = colors[int(value)]+str(value)+cmod['reset']                    

          
            weight = v['weight']
            if weightStyle == 'weighted':
                if weight == '200%':
                    valStr = cmod['bold']+str(value)+cmod['reset']+' '
                else:
                    valStr = str(value)+' '

            else:
                if weightStyle == 'faded':
                    if weight == '200%':
                        valStr = f'{value}*{colors[0]}{cmod["bold"]}{weight}{cmod["reset"]} '
                    else:
                        valStr = f'{value}*{colors[0]}{weight}{cmod["reset"]} '
                else:
                    valStr = f'{value}*{weight} '

            gradestr += valStr

        broken = breakLine(gradestr,_padLen=longest+14,_len=tWidth-5).split('\n')
        for l in broken:
            printBetween(l)
            #tprint(f'| {l}'+(len(border)-len(clean_ansi(l))-3)*' '+'|')

        #if the subject is in globals and has data the lines get printed
        if tWidth < 90:
            printBetween('')
            #tprint('|'+(len(border)-2)*' '+'|')
            
    #bottom border
    dbg('Overall '+str(sum(avgs)/len(subjectsList)))
    dbg('('+str(sum(avgs))+'/'+str(len(subjectsList))+')')
    tprint(border)
    
    hints = [
                makeHint('num/name for info',colors[4],noUnderline=True),
                makeHint('num+s+[..] for simulate',colors[3],noUnderline=True),
                makeHint('overall menu',colors[1])
            ]
    tprint()
    
    if not noInp:
        for h in spaceHint(hints).split('\n'):
            tprint(h)
   
    padBottom()

    if not noInp:
        inp = qInp('')
        if inp.lower() == 'o':
            menuOverall()
        
        elif not inp == '':
            if not inp.isdigit():
                inp = approximateInput(inp,sublist,index=True)
               
            try: menuInfo(inp)
            except Exception as e:
                if debug == 'True':
                    raise(e)
                dbg(str(e))
                showTitle('0')
        else:
            goBack(1,inp)

#recents display function
def showRecents(): 
    if not len(marks):
        tprint('\n\n\n\n'+border+padded('|'))
        """
        tprint((tHeight//2-printedLines)*'\n'+cmod['bold']+'No grades to iterate over.'.center(tWidth)+cmod['reset'])
        padBottom()
        tprint(border)
        """
        l = "No grades available."
        # -----
        tprint(padded((len(l)+4)*"-"))
        # |   |
        tprint(padded(printBetween('',_len=len(l)+5,noPrint=1)))
        # |...|
        tprint(padded(printBetween(l,_len=len(l)+5,noPrint=1)))
        # |   |
        tprint(padded(printBetween('',_len=len(l)+5,noPrint=1)))
        # -----
        tprint(padded((len(l)+4)*"-"))
        padBottom()
        tprint('\033[3A'+border+'\033[3B')


        return

    for i,mark in enumerate(marks):
        lines = []

        index = str(i)
        subject = cmod['bold']+colors[3]+mark["subject"]+cmod['reset']+':'
        theme = (mark['theme'] if not mark['theme'] == '' else 'None')
        value = (f'{cmod["bold"]}{colors[mark["value"]-1]}{mark["value"]}{cmod["reset"]}' if isinstance(mark["value"],int) else mark["value"]) 
        weight = (f'*{mark["weight"]}{cmod["reset"]}' if not mark["weight"] == 'None' else '')
        valweight = (value if '-' in weight else value+weight)
        _datetime = f'{colors[0]}{mark["date"]} {mark["time"]}{cmod["reset"]}'
        datetime = _datetime

        for e in [subject,theme,valweight,datetime]:
            for t in breakLine(e,_len=tWidth*2/3).split('\n'):
                lines.append(t)

        maxLen = max(len(clean_ansi(l)) for l in lines)

        # top border
        print(padded(index+(maxLen+4-len(index))*'-'))

        # lines
        for l in lines:
            print(padded(printBetween(l,_len=maxLen+5,noPrint=True)))
        
        # bottom border
        bborder = padded((maxLen+4)*'-')
        print(bborder)
        
        # connecting lines
        if not i == len(marks)-1: 
            centerLen = random.randint(len(index)+6,maxLen)
            offset = random.randint(maxLen-15,maxLen+15)
            for _ in range(2):
                print(padded('||',_len=6+tWidth-offset/4))
        
        time.sleep(animTime*0.0005)

#settings menu
def showSettings():
    def writeSettings():
        dbg('writeSettings called')
        dbg(controlLines)
        import importlib
        from asztal import refresh
        import settings as st

        global debug,subSorter,gradeSorter,colorMode,ttDefault,prettyUser

        # write change to file
        shutil.copyfile(os.path.join(curdir,'settings.py'),os.path.join(curdir,'settings_backup'))
        settings = open(os.path.join(curdir,'settings.py')).read()
        with open(os.path.join(curdir,'settings.py'),'w') as f:
            for l in settings.split('\n')[:controlLines]:
                f.write(l+'\n')
            f.write('\n')
            for name in names:
                try:
                    dbg('setting '+name+' to '+str(globals()[name]))
                    if isinstance(globals()[name],str):
                        f.write(name+' = '+'"'+globals()[name]+'"'+'\n')
                    else:
                        f.write(name+' = '+str(globals()[name])+'\n')

                except KeyError as e:
                    dbg(str(e))

        # refresh variables
        settings = importlib.reload(st) 
        for name, val in settings.__dict__.items():
            if not callable(val) and not '__' in name:
                globals()[name] = val

        # refresh dbg in asztal since clr operates on it
        refresh()
        dbg('writeSettings successful.')        

    def invalidChoice():
        dbg('unrecognized choice')
        clr()
        text = '| '+cmod['bold']+'Invalid choice for '+colors[1]+name+cmod['reset']+'.'+' |'
        tprint('\n\n'+border+'\n')
        tprint(cmod['bold']+((len(clean_ansi(text)))*'-').center(tWidth)+cmod['reset'])
        tprint(padded(text))
        tprint(cmod['bold']+((len(clean_ansi(text)))*'-').center(tWidth)+cmod['reset']+'\n')

        tprint('\n\n\n\n\n\n\n\n\n'+border) 

    def isNumber(n):
        try:
            float(n)
            return True
        except:
            return False

    ## setup
    global debug,subSorter,gradeSorter,colorMode,ttDefault,prettyUser
    settings = open(os.path.join(curdir,'settings.py'),'r').read()

    names = []
    options = []
    data = []
    comments = []

    controlLines = 0

    #go through the settings file, filter the proper lines, and display
    for i,l in enumerate(settings.split('\n')):
        if l.startswith('#'):
            controlLines += 1

        if l.startswith('#.'):
            l = l.replace('#. ','')
            names.append(l.split(' : ')[0])
            
            # format option
            option = l.split(' : ')[1].split('-')[0]
            option = option.replace('[','').replace(']','').replace("'",'').split(',')
            options.append(option)
            #dbg(option)

            if not option == ['input']:
                # format data
                dat = l.split(' : ')[1].split('-')[1]
                dat = dat.replace('[','').replace(']','').replace("'",'').strip().split(',')
                data.append(dat)
            else:
                data.append('input')

            #if data[-1] == 'input':
            # format comments
            cmt = l.split(' : ')[1].split('-')[-1]
            cmt = cmt.replace("'",'').strip()
            comments.append(cmt)
        
        #dbg(len(names))
    clr()

    ## main menu
    tprint('\n\n'+border+'\n\n')
    borderLen = 35
    menuBorder = cmod['bold']+('settings'+(borderLen-len('settings'))*'-').center(tWidth)+cmod['reset']
    menuBorderIndex = clean_ansi(menuBorder).index('s')
    padding = menuBorderIndex*' '+'| '

    hint = padded(makeHint('preview grades menu',colors[4])+cmod['reset'])

    tprint(menuBorder)
    lines = []
    for i,n in enumerate(names):
        if len(options[i]) in range(3):
            formatting = [colors[4],colors[1]]
        else:
            formatting = colors.copy()
        
        
        if 'input' in data[i]:
            selected = formatting[0]+str(globals()[n])
        else:
            try:
                selIndex = data[i].index(globals()[n])
            except Exception as e:
                dbg(n+': '+str(e))
                continue
            selected = formatting[selIndex]+options[i][selIndex]
     
        left = padding+f'{cmod["bold"]}{i}. {n}:' 

        midPadding = menuBorderIndex+borderLen-len(clean_ansi(left))-len(clean_ansi(selected))-2
        right = midPadding*' '+f'{selected}{cmod["reset"]}'+' |'
        tprint(left+right)
    
    tprint(cmod['bold']+(borderLen*'-').center(tWidth)+cmod['reset']+'\n')
    tprint(hint)
    tprint('\n\n'+border)
    padBottom()
    
    nameInp = qInp('').strip()
    namesLower = [n.lower() for n in names]
  
    # approximate detection
    nameIndex = None
    if len(nameInp) > 1:
        nameIndex = approximateInput(nameInp,namesLower,index=True)
    
    #if we wanna go back the settings are written to the file
    if nameIndex == None:
        if nameInp == '':
            writeSettings()
            showTitle()
        
        #if valid choice str
        elif nameInp.lower() in [n.lower() for n in names]:
            nameIndex = namesLower.index(nameInp.lower())
        
        #show a preview of grades menu
        elif nameInp.lower() == 'p':
            clr()
            showGrades(noInp=True)
            if qInp(''): pass
            showSettings()

        else:
            try: nameIndex = int(nameInp)
            except Exception as e: dbg(str(e));showSettings()

        # if out of range
        if not nameIndex in range(len(names)):
            dbg(str(nameIndex)+' out of range')
            showSettings()

    name = names[nameIndex]



    ## submenu
    clr()
    tprint('\n\n'+border+'\n\n')
    inputType = ('input' in options[nameIndex])
    subBorderLen = (len(comments[nameIndex])+10 if inputType else borderLen)
    subMenuBorder = cmod['bold']+(name+(subBorderLen-len(name))*'-').center(tWidth)+cmod['reset']
    lilPaddyVert,downPadding = divmod(len(options)-len(options[nameIndex]),2)
    menuBorderIndex = clean_ansi(subMenuBorder).index(name[0])
    padding = menuBorderIndex*' '+'| '

    tprint(subMenuBorder)


    if not inputType: 
        for _ in range(lilPaddyVert): tprint(padding+(subBorderLen-3)*' '+'|')
    
    for i,o in enumerate(options[nameIndex]):
        if 'input' in o:
            o = comments[nameIndex]+': '
            index = ''
            downPadding += 6
        elif len(options[nameIndex]) in range(3):
            formatting = [colors[4],colors[1]]
            index = cmod['reset']+cmod['bold']+str(i)+cmod['reset']+'. '
        else:
            formatting = colors.copy()
            index = cmod['reset']+cmod['bold']+str(i)+cmod['reset']+'. '
        
       

        paddingMid = 2*' '
        left = paddingMid+index+cmod['bold']
        
        paddingEnd = (subBorderLen-len(clean_ansi(left+o))-3)*' '
        tprint(padding+left+formatting[i]+o+cmod['reset']+paddingEnd+'|')
    
    if not inputType:
        for _ in range(lilPaddyVert): tprint(padding+(subBorderLen-3)*' '+'|')
    
    tprint(cmod['bold']+((subBorderLen)*'-').center(tWidth)+cmod['reset']+'\n')
    
    tprint('\n\n\n'+downPadding*'\n'+border+'\n')
    padBottom()
    
    choice = qInp('')
    if choice == '':
        writeSettings()
        globals()['colors'] = getColors()
        showSettings()
    
    for o in options[nameIndex]:
        for i in range(len(o)):
            if choice == o[:i].lower():
                choice = o
                break

    if inputType:
        if isNumber(choice):
            try: 
                globals()[name] = int(choice)
            except ValueError:
                try:
                    globals()[name] = float(choice)
                except:
                    dbg(str(e))
                    invalidChoice()
        else:
            invalidChoice()

    # set selected option
    #if option is string 
    elif choice in options[nameIndex]:
        globals()[name] = data[nameIndex][options[nameIndex].index(choice)]
        writeSettings()

    #if option is digit
    elif choice.isdigit() and int(choice) in range(len(options[nameIndex])):
        globals()[name] = data[nameIndex][int(choice)]
        writeSettings()
    
    #unrecognized
    else:
        invalidChoice()
        if qInp(''):
            showSettings()
   
    clr()
    showSettings()

#profile menu
def showProfiles():
    global createUser,listUsers,editUser 

    clr()
    from usercfg import users
    dbg(f'users: {len(users)}')
    optRaw = ['new','switch','edit','default','remove']
    clrs = [colors[5],colors[4],colors[3],colors[2],colors[1]]

    options = [makeHint(s,clrs[i]) for i,s in enumerate(optRaw)]
    
    tprint('\n\n'+border+'\n\n')
    listUsers(noInp=1,noIndex=1,showDefault=True)

    tprint('\n\n'+padded('  '.join(options)))
    tprint('\n\n'+border)
    padBottom()
    
    #get input
    inp = qInp('')
    if not inp in ['n','s','r','e','d','']: showProfiles()
    if inp == '':
        showTitle()
   
    #create new user
    if inp == 'n':
        clr()

        #if nothing changed
        clr(f=1)
        if users == createUser():
            clr(f=1)
            showProfiles()

        print('\n'+padded(f'Want to switch to {users[-1]["usr"]} now? Y[n] '))
        padBottom()
        if qInp('').lower() == 'y':
            switchUser(users[-1]) 
        else:
            showProfiles()

    #switch user
    elif inp == 's':
        clr() 
        try: del locals()['oldUsr']
        except: pass
        from marks import usr as oldUsr

        tprint('\n\n'+border+'\n\n\n'+padded(cmod['bold']+'Choose profile to switch to:\n\n'+cmod['reset']))
        choice = listUsers(border='\n\n\n'+border,showDefault=False,old=oldUsr)
        padBottom()
        if choice == None:
            showProfiles()

        if switchUser(choice) == None:
            showProfiles()

    #edit user
    elif inp == 'e':
        clr()
        tprint('\n\n'+border+'\n\n\n'+padded(cmod['bold']+'Choose profile to edit:\n\n'+cmod['reset']))
        user = listUsers(border='\n\n'+border+'\n')
        padBottom()
    
        if user == None:
            showProfiles()

        clr()
        tprint('\n\n')
        editUser(user)
        if input('\n'+padded(f'Want to switch to {user["usr"]} now? Y[n] ')).lower() == 'y':
            clr()
            switchUser(user)
        else:
            showProfiles()
        
    #remove mode
    elif inp == 'r':
        clr()

        tprint('\n\n'+border+'\n\n\n'+padded(cmod['bold']+'Choose profile to delete:\n\n'+cmod['reset']))

        choice = listUsers(border='\n\n'+border)
        if choice == None:
            showProfiles()

        clr()
        tprint('\n\n'+border+'\n\n\n\n')
        
        name = (choice['name'] if prettyUser == 'True' and 'name' in choice.keys() else choice['usr'])
        
        
        print(padded(cmod['bold']+int(tWidth/2)*'-'+cmod['reset']))
        print(cmod['bold']+padded(printBetween('Are you sure you want to delete '+colors[1]+name+cmod['reset']+cmod['bold']+'? Y[n]',_len=int(tWidth/2),noPrint=True))+cmod['reset'])
        print(padded(cmod['bold']+int(tWidth/2)*'-'+cmod['reset']))
        #print(padded(f'Are you sure you want to delete {colors[1]}{name}{cmod['reset']}{cmod['bold']}? Y[n] '+cmod['reset'])+'\n\n\n\n\n\n'+border+'\n')
        padBottom()
        if qInp('').lower() == 'y':
            shutil.copyfile(os.path.join(curdir,'usercfg.py'),'usercfg_backup')
            users.remove(users[users.index(choice)])
            with open(os.path.join(curdir,'usercfg.py'),'w') as f:
               f.write(f'users = {json.dumps(users,indent=4)}')
        
        #check if current user is still in the config
        try: del locals()['oldUsr']
        except: pass
        from marks import usr as oldUsr
        
        if not any(u['usr'] == oldUsr for u in users):
            clr()
            tprint(f'\n\n{border}\n\n Your current user {oldUsr} is not in usercfg.py anymore.\n You can keep using the account until restart or you can change it in the profile menu.\n\n{border}')
        else:
            showProfiles()

    #make user default
    elif inp == 'd':
        clr()

        # get input
        tprint('\n\n'+border+'\n\n\n'+padded(cmod['bold']+'Set profile to default:\n\n'+cmod['reset']))

        choice = listUsers(border='\n\n'+border)
        if choice == None:
            showProfiles()

        clr()
        #tprint('\n\n'+border+'\n\n\n\n')

        from usercfg import users
        for u in users:
            if not u == choice:
                u['isDefault'] = 'False'
            else:
                u['isDefault'] = 'True'


        shutil.copyfile('usercfg.py','usercfg_backup')
        with open('usercfg.py','w') as f:
            f.write('users = '+json.dumps(users,indent=4))

        showProfiles()

##update menu
def showUpdate():    
    clr()

    try:
        import update
        #if animTime: time.sleep(animTime)
        tprint('\n\n'+border+'\n')
    except Exception as e:
        dbg('update: '+str(e))
        tprint(f'Error ({e}) during importing of update.')
        return
   
    newVersion,changelog = update.getNew()
    linePad = '    '
    for i,l in enumerate(changelog):
        changelog[i] = linePad+breakLine(l,_len=tWidth-len(linePad)-2,_padLen=len(linePad)+2)

    changelog = '\n'.join(changelog)
    if newVersion > vrs:
        tprint(cmod['bold']+('New version '+str(newVersion)+' available!').center(tWidth)+'\n\n'+'Changelog:'.center(tWidth)+cmod['reset'])
    else:
        tprint(cmod['bold']+'No new version available.'.center(tWidth)+'\n\n'+'Current changelog:'.center(tWidth)+cmod['reset'])

    tprint(colors[0]+linePad+str(newVersion)+':')
    for l in changelog.split('\n'):
        tprint(l)
    tprint(cmod['reset'])

    updateHint = makeHint('update now',colors[4])
    forceHint = makeHint('force update',colors[4])

    if newVersion > vrs:
        hint = updateHint
        conf = 'u'
    else:
        hint = forceHint
        conf = 'f'

    tprint(padded(hint)+cmod['reset'])
    tprint('\n'+border)
    padBottom()
    inp = qInp('').lower()
    
    if inp == conf:
        clr()
        tprint('\n\n'+border+'\n')
        update.start(pad=linePad)
        tprint('\n'+border)
        if qInp('Restart required. Do it now? [Y]n ').lower() != 'n':
            sys.exit()
        else:
            showUpdate()
    else:
        showTitle()

#==========================profile functions===========================
# these need to be outside of showProfiles so that asztal.py has access

##switch user
def switchUser(user):
    global marks,timetable,subjectsList

    clr(f=1)
    from api import Student
    from usercfg import users
    
    import marks
    if marks.usr == user['usr']:
        return

    usr,pwd,ist = user['usr'],user['pwd'],user['ist']
    
    del globals()['marks']
    del globals()['subjectsList']
    del globals()['timetable']
    
    dbg('deleted globals')
    dbg(user['usr'])
    stu = Student(usr,pwd,ist,offline=False)
    tprint('\n\n')
    
    err = stu.start()

    while err:
        tprint('\n')
        user = users[[u['usr'] for u in users].index(usr)]
        usr,pwd,ist = editUser(user)
        clr()
        
        newUser = Student(usr,pwd,ist,offline=False)
        tprint('\n\n')
        err = newUser.start() 
    import marks
    start()

##create new user
def createUser():
    clr()
    tprint('\n\n')
    
    ##trying to import usercfg
    if 'usercfg.py' in os.listdir(os.path.dirname(__file__)):
        try:
            sys.path.insert(0,os.path.dirname(__file__))
            from usercfg import users
        except:
            users = []
    else:
        users = []

    ##ask for user input of usr,pwd,ist
    usr = input(padded('Username: '))
    pwd = getpass(padded('Password: '))
    ist = input(padded('Institute: '))
  
    if all([v == '' for v in [usr,pwd,ist]]):
        return users

    ##store user as json
    #create user dict
    user = {
            'usr': usr,
            'pwd': pwd,
            'ist': ist,
            'isDefault': 'False'
            }

    #convert to json
    users.append(user)

    #store in file
    usersJson = json.dumps(users,indent=4,ensure_ascii=False)
    with open(os.path.join(os.path.dirname(__file__),'usercfg.py'),'wb') as f:
        f.write(f'users = {usersJson}'.encode('utf-8'))

    if 'usercfg' in sys.modules:
        del sys.modules['usercfg']
    
    ##return users data
    return users

##list users to choose from
def listUsers(users=None,noInp=False,noIndex=False,showDefault=True,border=None,old=None):
    #from ui import color,clean_ansi
    from settings import prettyUser


    if users == None:
        from usercfg import users
    users.sort(reverse=True,key=lambda x: x['isDefault'])

    # border
    borderLen = 32+(0 if noIndex else 2)
    borderSmol = cmod['bold']+f"{borderLen*'-'}".center(tWidth)+cmod['reset']
    tprint(borderSmol)
    
    for i,user in enumerate(users):
        default = (colors[2]+'*'+cmod['reset'] if showDefault and user['isDefault'] == 'True' else ' ')
        current = user['usr']

        # get start of borderSmol to base center upon
        for bI,c in enumerate(clean_ansi(borderSmol)):
            if not c == ' ':
                borderStart = bI
                break

        
        paddingLeft = ' '*borderStart
        
        ## index
        # grey out current account to avoid confusion
        if current == old:
            index = f'|{colors[0]} '
        else:
            index = cmod['bold']+'| '+cmod['reset']
        
        #with index number
        if not noIndex:
            index += str(i)+': ' 
        #without index number nothing needs to be done


        ## middle
        # if we can display the user and we also want to
        if 'name' in user.keys() and prettyUser == 'True':
            #mid = name
            mid = ('' if colors[0] in index else cmod['bold'])+int(borderLen/15)*' '+user['name']+cmod['reset']
 
        else:
            #mid = user_info
            if colors[0] in index:
                mid = (int(borderLen/15)-1)*' '+user['usr'] + ' @ ' + user['ist'] + cmod['reset']
            else:
                mid = colors[4]+cmod['bold']+(int(borderLen/15)-1)*' '+user['usr']+cmod['reset'] + cmod['bold']+ ' @ ' + colors[1]+user['ist']+cmod['reset']

 
        ## end
        end = ''
        # if showing default indicator
        if showDefault:
            end += default
        end = ' '*(borderLen-(len(clean_ansi(index+mid+end+default)))-1)+end
        end += cmod['bold']+' |'+cmod['reset']
        
        tprint(paddingLeft+index+mid+end)
    
 
    tprint(borderSmol)
    
    if not border == None:
        tprint(border)
        padBottom()


    if not noInp:
        inp = qInp('')
        if inp == '':
            return None

        try:
            user = users[int(inp)]
        except Exception as e:
            dbg(str(e))
            clr()
            tprint('\n\n')
            listUsers()
   
        return user

##edit user
def editUser(user):
    from usercfg import users
    from ui import color
    
    clr(f=1)
    print('\n\n')
    userIndex = users.index(user)
    for key,value in user.items():
        if not key in ['usr','pwd','ist']:
            continue
        newValue = input(padded(cmod['bold']+colors[4]+value+cmod['reset']+cmod['bold']+': '+cmod['reset']))
        if newValue == '':
            newValue = value
        user[key] = newValue 
    users[userIndex] = user
    shutil.copyfile(os.path.join(curdir,'usercfg.py'),'usercfg_backup')
    with open(os.path.join(curdir,'usercfg.py'),'w') as f:
        f.write('users = '+json.dumps(users,indent=4))
    clr(f=1)
    return user['usr'],user['pwd'],user['ist']
    #print(cmod['bold']+((borderLen-len(clean_ansi(dayLegend)))*'-'+dayLegend).center(tWidth)+cmod['reset'])

#====================================================================

#basically just so that you can go back in menus
def goBack(layer=0,_inp=None):
    dbg(f'navigation called\nlayer: {layer}\npath: {path}')
    
    #setting inp value if not set
    if _inp == None:
        _inp = qInp('')


    #if user wants to go back
    if _inp in ['',' ']:
        #title
        if layer == 0:
            dbg('navigation: 0')
            showTitle()
        #displayGrades/displayRecents
        if layer == 1:
            dbg('navigation: 1')
            showTitle()
        
        #menuGrades
        if layer == 2:
            dbg('navigation: 2')
            dbg(f'path: {path}')
            showTitle(path[-1])

    #unrecognized input is ignored
    else: 
        goBack(layer)

#start method
def start(_mode='online',_debug=0,shortcut=None):
    global dbg,mode,path,user,name,marks,subjectsList,timetable,titleArt
    debug,mode = _debug,_mode

    
    try:
        del sys.modules['marks']
        del globals()['marks']
        del globals()['subjectsList']
        del globals()['timetable']
        del globals()['bday']
        dbg('deleted globals')
    except Exception as e:
        dbg(str(e))
        

    path = []

    if debug == 0:
        clr(f=1)
   
    #importing grades
    try:
        from marks import usr,name,marks,subjectsList,timetable,bday
        from usercfg import users
    except Exception as e: 
        clr()
        tprint(f'Error: {e}')
        sys.exit()

    #adding name to usr if not present already
    userIndex = [u['usr'] for u in users].index(usr)
    
    if not 'name' in users[userIndex].keys():
        users[userIndex]['name'] = name
    shutil.copyfile(os.path.join(curdir,'usercfg.py'),os.path.join(curdir,'usercfg_backup'))
        
    with open(os.path.join(curdir,'usercfg.py'),'wb') as f:
        f.write(b'users = '+json.dumps(users,ensure_ascii=False,indent=4).encode('utf-8'))

    #tprint('\n\n\nUI:')
    showTitle(shortcut,bday)

#=====================================================================
