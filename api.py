#!/usr/bin/env python3
#strftime reference: https://strftime.org/
import requests,json,datetime,sys,os
import http.client as httplib
import time as timeModule
from random import randint

tWidth = os.get_terminal_size()[0]
verboseGlobal = True
log = None

def dbg(s):
    if verboseGlobal == True:
        _str = f'[{str(datetime.datetime.now().time())[:-7]}]: {s}'
        pad = int(tWidth/2-_str.index(': ')-3)*' '
        print(pad+_str)

        if log == None:
            return
        else:
            log(s,show=0)

def connected():
    conn = httplib.HTTPConnection("8.8", timeout=1)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def Bearer(user,pwd,ist): 
    headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'User-Agent': 'hu.ekreta.student/1.0.5/Android/0/0'
    }
    data = {
        'userName': user,
        'password': pwd,
        'institute_code': ist,
        'grant_type': 'password',
        'client_id': "kreta-ellenorzo-mobile"
    }

    try:
        maci = requests.post('https://idp.e-kreta.hu/connect/token', headers=headers, data=data)
    except requests.exceptions.ConnectionError:
        if not connected():
            return 'offline'
        else:
            print('Invalid institute name.'.center(tWidth))
            return 'err: invalid_institute'

    #maci = requests.post('https://{}.e-kreta.hu/idp/api/v1/Token'.format(ist), headers=headers)
    if maci:
        try:
            maci = json.loads(maci.text)['access_token']
        except KeyError as e:
            print(str(e))
            return 'err: invalid_response'
        except Exception as e:
            dbg(str(e))
            print('Bad response from Kreta, the server is likely offline.'.center(tWidth))
            print(f'For more info check {ist}.ekreta.hu.'.center(tWidth))
            if input(''): pass
            return 'offline'
    else:
        print(maci.text.center(tWidth))

    dbg('Maci acquired.')
    
    return maci

class Student:
    def __init__(self,usr=None,pwd=None,ist=None,verbose=None,timetable=True,jsonLocation=os.path.join(os.path.dirname(__file__),'marks.py'),offline=False,logger=None):
        global log
        if not logger == None:
            log = logger
        
        ##assigning verbose boolean for dbg prints 
        global  verboseGlobal 
        if not verbose == None:
            verboseGlobal = verbose
        
        ##store user data
        self.usr = usr
        self.pwd = pwd
        self.ist = ist

        self.jsonLocation = jsonLocation
        self.offline = offline
        
    def start(self):
        if not self.offline:
            self.maci = Bearer(self.usr,self.pwd,self.ist)
        else:
            self.maci = 'offline'
       
        if 'err: ' in self.maci:
            return self.maci


        ##checking if something went wrong during maci
        if self.maci == 'offline':
            dbg(f'Offline mode, maci: {self.maci}')

            ##assign attributes based on old file
            try:
                import marks
                self.name = marks.name
                self.marks = marks.marks
                self.subjectsList = marks.subjectsList
                try: self.timetable = marks.timetable
                except: pass
                return
            
            except Exception as e:
                print(str(e))
                return

        ##defining headers for marks and timetable to use
        self.headers = {
                "Authorization": "Bearer "+self.maci,
                "User-Agent": "hu.ekreta.student/1.0.5/Android/0/0"
        }

        ##getting marks, timetable
        self.marks,self.subjectsList = self.getMarks()
        try:
            import forcett
            self.timetable = forcett.timetable
        except:
            self.timetable = Timetable(self).get()

        self.getInfo()

        ##saving data
        self.serialize()
        dbg('API initialized.')

    #get marks, return a list
    def getMarks(self):
        ##make connection
        dbg('Getting marks...')
        marksResponse = requests.get(f'https://{self.ist}.ekreta.hu/ellenorzo/V3/Sajat/Ertekelesek', headers=self.headers)                
        self.marksText = marksResponse.text
        
        with open('sample_marks','w') as f:
            f.write(self.marksText)

        ##filter data
        marks = []
        subjectsList = []
        mk = json.loads(self.marksText)

        dbg('Sorting marks...')
        for mark in mk:
            subject = mark['Tantargy']['Nev']
            theme = mark['Tema']
            _type = mark['Tipus']['Nev']
            value = mark['SzamErtek']
            if value == None:
                value = mark['SzovegesErtek']

            weight = mark['SulySzamErteke']
            teacher = mark['Teacher']
            dateFull = mark['RogzitesDatuma']
            date = dateFull.split('T')[0]
            time = dateFull.split('T')[1][:-4]
            
            if _type == 'felevi_jegy_ertekeles':
                theme = 'Half term result'
                weight = 100

            elif _type == 'evvegi_jegy_ertekeles':
                theme = 'End of term result'
                weight = 100


            ## add subject to subjectsList if not in there already
            if not subject in subjectsList and subject:
                subjectsList.append(subject)

            ## create marks dict
            if subject:
                marks.append(
                        {
                            'subject': subject,
                            'theme': theme,
                            'type': _type,
                            'value': value,
                            'weight': weight,
                            'date': date,
                            'time': time
                        }
                )


        ##sort data
        marks.sort(key=lambda x: [x['date'],x['time']])
        
        ##return a list containing mark dicts
        return marks,subjectsList

    #get info about user
    def getInfo(self):
        # returns info about the student
        response = requests.get(
                'https://'+self.ist+'.ekreta.hu/ellenorzo/V3/Sajat/TanuloAdatlap',
                headers = self.headers,
        )
        
        info = json.loads(response.text)
        self.name = info['Nev']
        
        #get birthday
        self.bdayDate = info['SzuletesiDatum'].split('T')[0].split('-')[1:]
        self.bdayDate[1] = str(int(self.bdayDate[1])+1)
        if len(self.bdayDate[1]) == 1:
            self.bdayDate[1] = '0'+self.bdayDate[1]

        self.bdayDate = '-'.join(self.bdayDate)

        today = str(timeModule.strftime('%m-%d'))
        self.isBday = (today == self.bdayDate) 

    ##store data in a json file self.jsonLocation (assigned at creation)
    def serialize(self):
        with open(self.jsonLocation,'wb') as mks:
            mks.write(b'# these are needed because im importing the module and not json\n')
            mks.write(b'null = None\n')
            mks.write(b'false = False\n')
            mks.write(b'true = True\n\n')

            ##convert lists to json
            mksJson = json.dumps(self.marks,ensure_ascii=False,indent=4)
            subListJson = json.dumps(self.subjectsList,ensure_ascii=False,indent=4)
            ttJson = json.dumps(self.timetable,ensure_ascii=False,indent=4)

            ##write json to file
            mks.write(b'# data\n')
            mks.write((f'usr = \'{self.usr}\'\n').encode('utf-8'))
            mks.write((f'name = \'{self.name}\'\n\n').encode('utf-8'))
            mks.write((f'bday = {self.isBday}\n\n').encode('utf-8'))
            mks.write((f'marks = {mksJson}\n\n').encode('utf-8'))
            mks.write((f'subjectsList = {subListJson}\n\n').encode('utf-8'))
            mks.write((f'timetable = {ttJson}').encode('utf-8'))

    ##on delete delete imported module if exists
    def __del__(self):
        if 'marks' in sys.modules:
            del sys.modules['marks']

class Timetable:
    def __init__(self,student,start=None,end=None):
        self.parent = student 
        self.ist = self.parent.ist

        #if we dont have both dates we get them
        if any((val == None for val in [start,end])):
            self.start,self.end,self.currentDay = self.getDates()
    
    def getDates(self):
        import datetime 

        ##get current day, current weekday int, store current day
        startDate = datetime.date.today()
        start = datetime.date.today().weekday()
        current = str(startDate)


        ##while we're not on a monday continue
        while not start == 0:
            startDate = startDate-datetime.timedelta(days=1)
            start = startDate.weekday()
        endDate = startDate+datetime.timedelta(days=6)


        ##return start,end
        return startDate,endDate,current

    def get(self):
        ##separate on and offline mode
        if not self.parent.offline == False:
            from marks import timetable
            return timetable
            

        ##make connection
        dbg('Getting timetable...') 
        headers = self.parent.headers
        params = {
            'datumTol': f'{self.start}',
            'datumIg': f'{self.end}'
        }

        ttResponse = requests.get(
                f'https://{self.ist}.ekreta.hu/ellenorzo/V3/Sajat/OrarendElemek', 
                headers=headers, 
                params=params
        )

        ##filter data
        days = []
        dbg('Sorting timetable...')
        tt = json.loads(ttResponse.text)
        day = []
        for lesson in tt: 
            # reset days
            if lesson['Oraszam'] == 1:
                day = []
            
            startdate = lesson['KezdetIdopont']
            date = startdate.split('T')[0]
            start = startdate.split('T')[1][:-1]
            end = lesson['VegIdopont'].split('T')[1][:-1]
            subject = lesson['Tantargy']
            classroom = lesson['TeremNeve']
            teacher = lesson['TanarNeve']
            theme = lesson['Tema'] 
            

            ##create day dict
            day.append(
                {
                'date': date,
                'start': start,
                'end': end,
                'subject': subject,
                'classroom': classroom,
                'teacher': teacher,
                'theme': theme,
                'isCurrent': self.isCurrent(start,end,date)
                }
            )

            ##add day if not in days already
            if not day in days:
                days.append(day)

        ##return a compound list containing each days lessons
        return days

    def isCurrent(self,_start,_end,_date):
        ##convert start,end to datetime objects
        start = datetime.datetime.strptime(_start, '%H:%M:%S').time()
        end = datetime.datetime.strptime(_end, '%H:%M:%S').time()

        #get current
        currentDay = _date
        current = datetime.datetime.now().time()

        #return if current is between start&end and the days match
        return (True if (start < current < end and currentDay == self.currentDay) else False)

