# Asztal
## A python implementation of the Kreta API compiled by boapps.


### The program itself doesn't have 100% of Kreta's functionality, as I only wrote it because I got fed up with how bad the official Kreta app was. This version is way faster and was really just a good exercise to start my coding adventure. Writing it took way longer than anticipated, but I'm proud of the end result. 


### Again, as this was my first try at proper programming there are some oversights and just generally bad practices, so do keep that in mind, but I have been using it fully instead of Kreta or other apps, so I think it's quite useful.


### As I haven't been able to make an Android, iOS or even web version it is only available as this program, but it can be on all platforms:
	
#### Android:
		I recommend using Termux and installing asztal there, probably with a git clone. If you edit the .bashrc and add the path to your asztal.py file you can repurpose the terminal to just serve as a way to run it.

#### iOS:
		Should work with any Python interpreter available, and has in the past been tested (and written in) Pythonista, a payed Python editor app. Again, just import the files to the app's folder and run it from there.
	
#### Desktop:
		Just `git clone` and run asztal.py
	
	The mobile versions are not ideal, but again I haven't been able to figure out a way to run it in a better way. If you have an idea you think would work, please contact me and tell me about it.


# Features
## Asztal features 5 main profiles:
	
### Grades:
#### Lists all grades in a selected order using a selected style. (more on that later) From the "main" menu there are 3 additional submenus:
##### - overall:
###### Shows rounded average of all subjects, allows for editing each value, and once available also shows half and end of term grades, along with the halfterm's difference from either current or end of year.
##### - info:
###### Shows info on all individual grades, like time of registry, theme, value and weight.
			
##### - simulate:
###### Can be accessed directly from the "main" menu in the format:
###### \<subject\_index\>s\<grades\_to\_add(optional)> -> 06s555
###### or through info of either subject in the same format excluding the index as it's given.
	
### Recents:
#### Shows all grades sorted by time of registry in a single print from top to bottom. Probably the simplest menu of the program.

	
### Timetable:
#### Shows a menu displaying the user's timetable. Input takes the value 'ttdefault' into consideration. A single digit input sets the value specified in ttdefault, while ('d' or 'l')+digit sets the value for either the day or lesson.
	
	
### Profiles:
#### A menu to add, delete and manage kreta profiles used by asztal, pretty self explanatory.
	
	
### Settings:
#### Allows for changing some values to shift how asztal works.
	
	
### Update:
#### Shows the most recent changelog, allows for either updating if a new version is available or force-updating if not.

## All menus that feature a selection of sorts accept an index or the first 2 characters of the choice, except for timetable as I haven't felt like it would be of much use.


### Technicalities
## Asztal has 3 scripts:
	
### asztal.py:
#### launches the program, handles api.py and starts the ui.
	
### api.py:
#### based on the methods of both boapps' documentation and some of the Filc source code, logs users in and gets their data.
	
### ui.py:
#### probably like 90% of the actual code, handles every part of the... well.. ui.
	
### update.py:
#### just for a sneaky twist this handles updating asztal, and as sometimes things go wrong this is callable without running everything else to force update all files.
	

## Additionally it creates some extra files:

### marks.py:
#### created by api.py, stores data on the currently logged in user.

	
### \*usercfg.py
#### stores data of all users in a json format, however as it is unencrypted its not great, but as all but one people I've known use the default values it didn't seem too important.
#### note: yes, it doesnt make much sense storing it in a json format and no, I do not know why I did it.
	
	
### \*settings.py:
#### self-explanatory, stores the settings for asztal.
#### note: the comments on it are used for printing and value detection, so don't edit them if you don't know what you're doing.
	
	
### log:
####keeps track of whatever is going on in the program, useful if something goes wrong but probably won't be of much use to anyone not working on the code.

	
####+ files denoted with "\*" also keep backups of themselves, so if something is invalid it dynamically rolls back.


### Disclaimer
#### Has only been tested for 2 schools, and it didn't want to work with the non-kreta one. Not sure why this is, but I'll be looking to fix it. (if you try it with any school please let me know if it worked or not)
