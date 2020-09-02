#!/usr/bin/env python3

import sys,json,os,datetime,subprocess,shutil,time

#to avoid asztal creating files from where its ran
curdir = os.path.dirname(os.path.realpath(__file__))

#clear log file
open(os.path.join(curdir,'log'),'w').close

#====================functions=======================

#this refreshes the debug value for the main file i think?
def refresh():
    global debug
    from settings import debug

#======================init=========================

#import settings, create file if failed
try: from settings import debug
except Exception as e:
    dbg(str(e))

    files = os.listdir(curdir)
    if 'settings_backup' in files:
        shutil.copyfile('settings_default','settings.py')
        time.sleep(0.1)
        from settings import debug 
    elif 'settings_default' in files:
        shutil.copyfile('settings_default','settings.py')
        time.sleep(0.1)
        from settings import debug
    
    else:
        print('No settings.py in directory and no default_settings found.\n Check log for info.')
        with open(os.path.join(curdir,'log'),'a') as f:
            f.write(f'no settings in directory ({curdir}): {repr(files)}')
        if input('Run update.py to solve this issue? [Y]n ').lower in ['y','']:
            import update
            update.start()
        else:
            sys.exit()

#get version number
try:
    vrs = float(
            subprocess.Popen(
                ['cat' ,os.path.join(curdir,'changelog')],
                stdout=subprocess.PIPE
            )
            .communicate()[0]
            .decode('utf-8')
            .split('\n')[0]
            .replace(':','')
    )
except:
    vrs = 0.0

#======================main==========================

if __name__ == '__main__':
    import ui
    from ui import createUser,editUser,listUsers,tWidth,tHeight,dbg,clr
    from api import Student
    clr(1)

    ##initialize student object based on offline mode
    if len(sys.argv) > 1 and 'o' in sys.argv[1]:
        offline = True
    else:
        offline = False
    
    clr()
    dbg('INIT :',time=0)

    #get user data
    try:
        try:
            from usercfg import users
        except:
            if 'usercfg_backup' in os.listdir(curdir):
                shutil.copyfile(os.path.join(curdir,'usercfg_backup'),os.path.join(curdir,'usercfg.py'))
                time.sleep(0.2)
                from usercfg import users
            else:
                #if none is present create with createUser
                users = createUser()
                clr(f=1)

        #add default attribute to users
        change = False
        for i,u in enumerate(users):
            if not 'isDefault' in u.keys():
                users[i]['isDefault'] = 'False'
                change = True
        
        #add change to usercfg, make backup
        if change:
            shutil.copyfile(os.path.join(curdir,'usercfg.py'),os.path.join(curdir,'usercfg_backup'))
            with open(os.path.join(curdir,'usercfg.py'),'w') as f:
                f.write('users = '+json.dumps(users,indent=4))
                

        #if there's one user move forward
        if len(users) == 1:
            usr,pwd,ist = users[0]['usr'],users[0]['pwd'],users[0]['ist']

        #if theres more than one try to choose default
        if len(users) > 1:
            found = False
            for u in users:
                if u['isDefault'] == 'True':
                    usr,pwd,ist = u['usr'],u['pwd'],u['ist']
                    break

            #if theres no default use the first one in the list
            else:
                usr,pwd,ist = users[0]['usr'],users[0]['pwd'],users[0]['ist']
                
                #print('\n\n')
                #usr,pwd,ist,_ = [i for i in listUsers().values()]
            clr()

        
        ##create student object
        userIndex = [u['usr'] for u in users].index(usr)
        user = Student(usr,pwd,ist,offline=offline,logger=dbg)


        ##detect and fix errors in user
        print('\n\n')
        err = user.start()
        while err:
            print('\n')
            for u in users:
                if u['isDefault'] == 'True':
                    user = u
            usr,pwd,ist = editUser(user)
            clr()
            
            user = Student(usr,pwd,ist,offline=offline,logger=dbg)
            print('\n\n')
            err = user.start()

    except Exception as e:
        raise e



    ##start ui based on shortcut
    shortcut = None
    if len(sys.argv) > 1:
        #shortcuts: [grades,recents,timetable,profiles,settings]
        opt = sys.argv[1]
        options = ['m','r','t','p','s']
        shortcuts = [str(i) for i in range(len(options))]
        
        for s,o in zip(shortcuts,options):
            if o in opt:
                shortcut = s
    
    dbg('UI :',time=0)
    mode = ('offline' if user.maci == 'offline' else 'online')
    ui.start(shortcut=shortcut,_mode=mode)
