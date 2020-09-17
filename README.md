# Asztal: A Terminal GUI client for the e-Kreta system
<p align=center>
    <img src=https://github.com/bczsalba/asztal-images/blob/master/title.png alt=title width=80%>
</p>

## Installation:

#### Android:
 - I recommend using Termux and following the [Desktop](#Desktop) instructions.
 - If you edit the .bashrc file and add the path to your asztal.py you can repurpose the app to just serve as a way to run it.

#### iOS:
- Technically it should work with any python interpreter, however they are usually paid.
	
#### Desktop:
 - Just `git clone` and run asztal&#46;py
 - ...or for a more hands-off approach:
 
```bash
# Linux & MacOS
# this code will install asztal in your home directory
cd $HOME
git clone https://github.com/bczsalba/asztal
cd asztal
sudo python3 -m pip install requests
```
After this, you can launch asztal by running `cd $HOME/asztal && python3 asztal.py` in a terminal.

<details><summary><b>Additional quality of life fixes</b></summary>
<br>

- to start asztal by entering `asztal` into a bash terminal:  
```bash
echo "alias asztal='cd $HOME/asztal && python3 asztal.py'" >> $HOME/.bashrc && bash
```
	
- or create a desktop shortcut (MacOS):
```bash
# create 'shortcut' icon
echo -e '#!/bin/bash\npython3 $HOME/asztal/asztal.py' >> $HOME/Desktop/asztal.command
# make executable // will need administrator password
sudo chmod +x $HOME/Desktop/asztal.command
```
</details>

## Menus
<h3 align=center> Grades: </h3>

---

<p align=center>
    <img src=https://github.com/bczsalba/asztal-images/blob/master/grades.png width=90% alt=grades>
</p>

---


Lists all grades in a selected order using a selected style and sorting method for both grades and subjects. (more on that in [settings](#settings))
 
From the "main" menu there are 3 additional submenus:
 
**Overall**:
- accessed by `o` in the Grades menu
- shows rounded average of all subjects
- allows for editing each value
- once available, shows half and end of term grades, along with comparison to current grades
 
**Info**: 
- shows info on all individual grades:
`Theme: Value*Weight - Date`
	
**Simulate**:
 - can be accessed in 2 ways:
     - `<subject_index>s<grades_to_add(*optional)>`
     - select a subject in `Overall` and do `s<grades_to_add*>`
    
- examples:
     - to add 3 fives to the 6th subject from main: `6s555`
     - or do the same from the 6th subject's menu: `s555`
	
<h3 align=center> Timetable: </h3>

---

<p align=center>
    <img src=https://github.com/bczsalba/asztal-images/blob/master/timetable.png alt=timetable>
</p>

---

Shows a menu displaying the user's timetable. Input takes the value 'ttdefault' into consideration. 

A single digit input sets the value specified in [ttdefault](#settingspy), while `('d' or 'l')+digit` sets the value for either the day or lesson.

Can be overwritten by [forcett.py](#extras)
	
	
<h3 align=center> Profiles: </h3>

---

<p align=center>
    <img src=https://github.com/bczsalba/asztal-images/blob/master/profiles.png alt=profiles>
</p>

---

A menu to add, delete and manage kreta profiles used by asztal, uses [usercfg](#usercfgpy) to store data.

Has an option, [prettyUser](#settingspy) to show name instead of student ID.
	
	
<h3 align=center> Settings: </h3>

---

<p align=center>
    <img src=https://github.com/bczsalba/asztal-images/blob/master/settings.png alt=settings>
</p>

---

Allows for changing some values to shift how asztal works, stores data in [settings](#settingspy).
	
	
<h3 align=center> Update: </h3>

---

<p align=center>
    <img src=https://github.com/bczsalba/asztal-images/blob/master/update.png alt=update>
</p>

---

Shows the most recent changelog, allows for either updating if a new version is available or force-updating if not.
The [update script](updatepy) can be called without running asztal if some settings were to go awry.

**All menus that feature a selection of sorts accept an index or the first 2 characters of the choice, except for timetable as I haven't felt like it would be of much use.**  
<br>

# Technicalities
## Asztal has 3 scripts:
	
### asztal&#46;py:
Launches the program, handles api.py and starts the ui.
	
### api&#46;py:
Based on the methods of both boapps' documentation and some of the Filc source code, logs users in and gets their data.
	
### ui&#46;py:
Probably like 90% of the actual code, handles every part of the... well.. ui.
	
### update&#46;py:
Handles updating asztal, and as sometimes things go wrong this is callable without running everything else to force update all files.
	
## Additionally it creates some extra files:

### marks&#46;py:
Created by api.py, stores data on the currently logged in user.

	
### \*usercfg&#46;py:
Stores data of all users in a json format, but isn't encrypted.

Yes, it doesn't make much sense storing it in a json format and no, I do not know why I did it.
	
	
### \*settings&#46;py:
Self-explanatory, stores the settings for asztal.

**important**: the comments on it are used for printing and value detection, so editing them will likely break some parts of asztal. If this happens to you, you can reset the settings by just deleting both settings&#46;py and settings_backup.
	
	
### log:
Keeps track of whatever is going on in the program, useful if something goes wrong but probably won't be of much use to anyone not working on the code.

	
**files denoted with "\*" also keep backups of themselves, so if something is invalid Asztal doesn't die.**

# Extras

There are some extra features not immediately apparent:
- the option `-o` will force the program to not connect to Kreta servers, thus opening quicker but it won't use up-to-date grades.
- creating a json-formatted file titled `forcett.py` will make asztal use that file as a source of the timetable.

```json
~/asztal/forcett.py |
---------------------

timetable = [
    [
        {
            "start": "16:20",
            "end": "19:30",
            "subject": "Mathematics",
            "classroom": "Second corridor on the left",
            "teacher": "Albert Einstein"
        },
	...
    ]
]
```

# Sources
| Sources & Contributions  |                                        |
|--------------|---------------------------------------------------:|
| Original API |  [BoA](https://github.com/boapps/e-kreta-api-docs) |
| Extra Help   |  [Filc](https://filcnaplo.hu)                      |
| New API      |  [Me](https://github.com/bczsalba/ekreta-v2-docs)  |
