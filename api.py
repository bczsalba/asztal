#!/usr/bin/env python3
#strftime reference: https://strftime.org/
import requests,json,datetime,sys,os
import http.client as httplib
import time as timeModule
from random import randint

from ui import tWidth

# totally legally yoinked from filc source
randomDeviceNames = [
    "coral",
    "flame",
    "clark",
    "walleye",
    "a6eltemtr",
    "gracelte",
    "klte",
    "kwifi",
    "zerofltectc",
    "heroqltecctvzw",
    "a50",
    "beyond1",
    "H8416",
    "SOV38",
    "a6lte",
    "OnePlus7",
    "flashlmdd",
    "hammerhead",
    "mako",
    "lucye",
    "bullhead",
    "griffin",
    "h1",
    "HWBKL",
    "HWMHA",
    "HWALP",
    "cheeseburger",
    "bonito",
    "crosshatch",
    "taimen",
    "blueline"
  ]

device = randomDeviceNames[randint(0,len(randomDeviceNames)-1)]
verboseGlobal = True

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
    print('hey')
    conn = httplib.HTTPConnection("8.8", timeout=1)
    try:
        conn.request("HEAD", "/")
        conn.close()
        print('yay')
        return True
    except Exception as e:
        #print(e)
        #if input(''):
        #    pass
        conn.close()
        return False

def Bearer(user,pwd,ist): 
    clientID = "919e0c1c-76a2-4646-a2fb-7085bbbf3c56"

    headers = {
            'HOST': f'{ist}.e-kreta.hu',
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'User-Agent': f'Kreta.Ellenorzo/2.9.10.2020031602 (Android; {device} 0.0)'
            }
    data = {
        'institute_code': ist,
        'userName': user,
        'password': pwd,
        'grant_type': 'password',
        'client_id': clientID
        }

    try:
        maci = requests.post('https://{}.e-kreta.hu/idp/api/v1/Token'.format(ist), headers=headers, data=data)
    except requests.exceptions.ConnectionError:
        if not connected():
            return 'offline'
        else:
            print('Invalid institute name.'.center(tWidth))
            return 'err: invalid_institute'

    #maci = requests.post('https://{}.e-kreta.hu/idp/api/v1/Token'.format(ist), headers=headers)
    try:
        maci = json.loads(maci.text)['access_token']
    except KeyError:
        print('Invalid login credentials.'.center(tWidth))
        return 'err: invalid_response'
    except Exception as e:
        dbg(str(e))
        print('Bad response from Kreta, the server is likely offline.'.center(tWidth))
        print(f'For more info check {ist}.ekreta.hu.'.center(tWidth))
        if input(''): pass
        return 'offline'

    dbg('Maci acquired.')
    
    #try:
    #    maci = maci.text.split('"')[3]
    #except:
    #    return 'offline'
    
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
        
        #dbg(usr+pwd+ist)

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
                'HOST': f'{self.ist}.e-kreta.hu',
                'User-Agent': f'Kreta.Ellenorzo/2.9.10.2020031602 (Android; {device} 0.0)',
                'Authorization': 'Bearer {}'.format(self.maci)
                }
        
        ##getting marks, timetable
        self.marks,self.subjectsList = self.getMarks()
        try:
            import forcett
            self.timetable = forcett.timetable
        except:
            self.timetable = Timetable(self).get()

        ##saving data
        self.serialize()
        dbg('API initialized.')

    #get marks, return a list
    def getMarks(self):
        ##make connection
        dbg('Getting marks...')
        marksResponse = requests.get(f'https://{self.ist}.e-kreta.hu/mapi/api/v1/Student', headers=self.headers)                
        self.marksText = marksResponse.text
        
        #with open('sample_marks','w') as f:
        #    f.write(self.marksText)


        ##filter data
        marks = []
        subjectsList = []
        mk = json.loads(self.marksText)
        self.name = mk['Name']
        
        #get birthday
        self.bdayDate = mk['DateOfBirthUtc'].split('T')[0].split('-')[1:]
        self.bdayDate[1] = str(int(self.bdayDate[1])+1)
        if len(self.bdayDate[1]) == 1:
            self.bdayDate[1] = '0'+self.bdayDate[1]

        self.bdayDate = '-'.join(self.bdayDate)

        today = str(timeModule.strftime('%m-%d'))
        self.isBday = (today == self.bdayDate) 
        #self.isBday = True



        dbg('Sorting marks...')
        for mark in mk['Evaluations']:
            subject = mark['Subject']
            theme = mark['Theme']
            _type = mark['Type']
            value = mark['NumberValue']
            if value == 0:
                value = mark['Value']

            weight = mark['Weight']
            teacher = mark['Teacher']
            date = mark['CreatingTime'].split('T')[0]
            time = mark['CreatingTime'].split('T')[1][:-4]
            
            if not _type == 'MidYear':
                theme = 'Term'
                weight = '100%'

            ##add subject to subjectsList if not in there already
            if not subject in subjectsList and not subject == None:
                subjectsList.append(subject)

            ##create marks dict
            if not subject == None:
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

    ##store data in a json file self.jsonLocation (assigned at creation)
    def serialize(self):
        with open(self.jsonLocation,'wb') as mks:
            ##convert lists to json
            mksJson = json.dumps(self.marks,ensure_ascii=False,indent=4)
            subListJson = json.dumps(self.subjectsList,ensure_ascii=False,indent=4)
            ttJson = json.dumps(self.timetable,ensure_ascii=False,indent=4)

            ##write json to file
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
        params = (('fromDate', f'{self.start}'),('toDate', f'{self.end}'))#headers is global
        ttResponse = requests.get(f'https://{self.ist}.e-kreta.hu/mapi/api/v1/Lesson', headers=headers, params=params)


        ##filter data
        days = []
        dbg('Sorting timetable...')
        tt = json.loads(ttResponse.text)
        for lesson in tt: 
            #reset days
            if lesson['Count'] == 1:
                day = []

            date = lesson['StartTime'].split('T')[0]
            start = lesson['StartTime'].split('T')[1]
            end = lesson['EndTime'].split('T')[1]
            subject = lesson['Subject']
            classroom = lesson['ClassRoom']
            teacher = lesson['Teacher']
            theme = lesson['Theme'] 
            

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
        return (1 if (start < current < end and currentDay == self.currentDay) else 0)
