# Asztal: A Terminal TUI client for the e-Kreta system
<p align=center>
    <img src=https://github.com/bczsalba/asztal-images/blob/master/title.png alt=title width=80%>
</p>

## Installation:

**Android**:
 - I recommend using Termux and following the [Desktop](#Desktop) instructions

#### iOS:
- Technically it should work with any python interpreter, however they are usually paid.
	
#### Desktop:
 - `git clone`
 - ...or for a more hands-off approach:
 
```bash
# Linux & MacOS
# this code will install asztal in your home directory
cd $HOME
git clone https://github.com/bczsalba/asztal
cd asztal
sudo python3 -m pip install requests
# After this, you can launch asztal by running `python3 asztal.py` in a terminal.
```

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

## Functionality

- Overview of grades, and info on each
- Grade simulation system
- Timetable display
- Multi-profile support
- Lots of configurability
- Self-contained update method

## Extra features

There are some extra features not immediately apparent:
- the option `-o` will force the program to source info from storage
- `forcett.py` with the right syntax will be used as timetable, not Kreta info

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

## Images
<p align=center>
    <img src=https://github.com/bczsalba/asztal-images/blob/master/grades.png width=49% alt=grades>
    <img src=https://github.com/bczsalba/asztal-images/blob/master/recents.png width=49% alt=grades>
    <img src=https://github.com/bczsalba/asztal-images/blob/master/timetable.png width=49% alt=timetable>
    <img src=https://github.com/bczsalba/asztal-images/blob/master/settings.png width=49% alt=settings>
    <img src=https://github.com/bczsalba/asztal-images/blob/master/update.png width=49% alt=update>
</p>


## Sources
| Sources & Contributions  |                                        |
|--------------|---------------------------------------------------:|
| Original API |  [BoA](https://github.com/boapps/e-kreta-api-docs) |
| Extra Help   |  [Filc](https://filcnaplo.hu)                      |
| Updated API  |  [Me](https://github.com/bczsalba/ekreta-docs-v2)  |
