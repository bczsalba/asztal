# Asztal: A python implementation of the Kreta API compiled by boapps.
<img src=https://github.com/bczsalba/asztal-images/blob/master/title.gif a=title>

The program itself doesn't have 100% of Kreta's functionality, as I only wrote it because I got fed up with how bad the official Kreta app was. This version is way faster and was really just a good exercise to start my coding adventure. Writing it took way longer than anticipated, but I'm proud of the end result. 


Again, as this was my first try at proper programming there are some oversights and just generally bad practices, so do keep that in mind, but I have been using it fully instead of Kreta or other apps, so I think it's quite useful.


As I haven't been able to make an Android, iOS or even web version it is only available as this program, but it can be on all platforms:
	
##### Android:
 - I recommend using Termux and installing asztal there, probably with a git clone. If you edit the .bashrc and add the path to your asztal.py file you can repurpose the terminal to just serve as a way to run it.

##### iOS:
 - Should work with any Python interpreter available, and has in the past been tested (and written in) Pythonista, a payed Python editor app. Again, just import the files to the app's folder and run it from there.
	
##### Desktop:
 - Just `git clone` and run asztal&#46;py
 - ...or for a more hands-off approach:
 
```
# this code will install asztal in your home directory, and create a launcher on your desktop.
# replace <extension> with 'command' for MacOS, 'sh' for anything else
cd $HOME
git clone https://github.com/bczsalba/asztal
cd asztal
echo '#!/bin/bash\n$HOME/asztal/asztal.py' >> $HOME/Desktop/asztal.<extension>
sudo chmod +x $HOME/Desktop/asztal.<extension>
sudo chmod +x $HOME/asztal/asztal.py
python3 asztal.py
```

The mobile versions are not ideal, but again I haven't been able to figure out a way to run it in a better way. If you have an idea you think would work, please contact me and tell me about it.


# Features
Asztal features 5 main profiles:
	
### Grades:
<img src=https://github.com/bczsalba/asztal-images/blob/master/grades.png alt=grades>

Lists all grades in a selected order using a selected style and sorting method for both grades and subjects. (more on that in [settings](#settings))
 
From the "main" menu there are 3 additional submenus:
 
 ##### overall:
- shows rounded average of all subjects
  allows for editing each value
- once available, shows half and end of term grades, along with the halfterm's difference from either current or end of year.
 
##### info: 
- shows info on all individual grades, like time of registry, theme, value and weight.
	
##### simulate:
 - can be accessed directly from the "main" menu in the format:
         ```<subject_index>s<grades_to_add(optional)> ```
- or through info of either subject in the same format excluding the index as it's given.
    
- examples:
-- to add 3 fives to the 6th subject from main: `6s555`
-- or from the 6th subject's menu: `s555`
	
### Recents:
<img src=https://github.com/bczsalba/asztal-images/blob/master/recents.png alt=recents>

Shows all grades sorted by time of registry in a single print from top to bottom.
	
### Timetable:
<img src=https://github.com/bczsalba/asztal-images/blob/master/timetable.png alt=timetable>

Shows a menu displaying the user's timetable. Input takes the value 'ttdefault' into consideration. 

A single digit input sets the value specified in ttdefault, while `('d' or 'l')+digit` sets the value for either the day or lesson.

Can be overwritten by [forcett.py](#extras)
	
	
### Profiles:
<img src=https://github.com/bczsalba/asztal-images/blob/master/profiles.png alt=profiles>

A menu to add, delete and manage kreta profiles used by asztal, uses [usercfg](#usercfgpy) to store data.
	
	
### Settings:
<img src=https://github.com/bczsalba/asztal-images/blob/master/settings.png alt=settings>

Allows for changing some values to shift how asztal works, stores data in [settings](#settingspy).
	
	
### Update:
<img src=https://github.com/bczsalba/asztal-images/blob/master/update.png alt=update>

Shows the most recent changelog, allows for either updating if a new version is available or force-updating if not.
The [update script](updatepy) can be called without running asztal if some settings were to go awry.

**All menus that feature a selection of sorts accept an index or the first 2 characters of the choice, except for timetable as I haven't felt like it would be of much use.**  

# Technicalities
Asztal has 3 scripts:
	
### asztal&#46;py:
Launches the program, handles api.py and starts the ui.
	
### api&#46;py:
Based on the methods of both boapps' documentation and some of the Filc source code, logs users in and gets their data.
	
### ui&#46;py:
Probably like 90% of the actual code, handles every part of the... well.. ui.
	
### update&#46;py:
Handles updating asztal, and as sometimes things go wrong this is callable without running everything else to force update all files.
	

### Additionally it creates some extra files:

#### marks&#46;py:
Created by api.py, stores data on the currently logged in user.

	
#### \*usercfg&#46;py:
Stores data of all users in a json format, however as it is unencrypted its not great, but as all but one people I've known use the default values it didn't seem too important.

Yes, it doesnt make much sense storing it in a json format and no, I do not know why I did it.
	
	
#### \*settings&#46;py:
Self-explanatory, stores the settings for asztal.

**important**: the comments on it are used for printing and value detection, so editing them will likely break some parts of asztal.
	
	
#### log:
Keeps track of whatever is going on in the program, useful if something goes wrong but probably won't be of much use to anyone not working on the code.

	
**files denoted with "\*" also keep backups of themselves, so if something is invalid it dynamically rolls back.**

# Extras

There are some extra features not immediately apparent:
- `./asztal.py -o` will force the program to not connect to Kreta servers, thus opening quicker but it won't use up-to-date grades.
- creating a json-formatted file titled `forcett.py` will make asztal use that file as a source of the timetable.
```
~/asztal/forcett.py
--------------------

timetable = [
	[
        {
            "start": "16:20:00",
            "end": "7:30:00",
            "subject": "Mathematics",
            "classroom": "Second corridor on the left",
            "teacher": "Albert Einstein"
        },
	...
    ]
]
```


# Disclaimer
Has only been tested for 2 schools, and it didn't want to work with the non-kreta one. Not sure why this is, but I'll be looking to fix it. 
(if you try it with any school please let me know if it worked or not)
