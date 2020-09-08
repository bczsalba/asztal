#!/usr/bin/python3
import requests,os,subprocess,zipfile
zipLocation = os.path.join(os.path.realpath(os.path.dirname(__file__)),'asztal.zip')

def download_url(url, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

def getNew():
    os.chdir(f'{os.path.realpath(os.path.dirname(__file__))}')
    download_url('http://butorhaz.hopto.org/asztal.zip',zipLocation)
    with zipfile.ZipFile(zipLocation, 'r') as zp:
        files = zipfile.ZipFile.infolist(zp)
        for file in files:
            if file.filename.startswith('changelog'):
                with open(file.filename, 'wb') as f:
                    f.write(zp.read(file.filename))
    response = subprocess.Popen(['cat' ,'changelog'],stdout=subprocess.PIPE).communicate()[0].decode('utf-8').split(':\n')
    #response = response.split('\n')

    version = response[0]
    changelog = '\n'.join(response[1:]).split('\n')

    #changelog = ' '+'\n '.join(['  '+l for l in changelogRaw])
    #print(changelog)
    os.system(f'rm {zipLocation}')

    return float(version),changelog

def start(pad=''):
    print(pad+'Starting update...')
    download_url(f'http://butorhaz.hopto.org/asztal.zip',zipLocation)
    os.chdir(f'{os.path.realpath(os.path.dirname(__file__))}')
    for f in ['changelog','__pycache__','log','asztal.py','init.py','ui.py','settings_default']:
        print(pad+f' Removing {f}..')
        os.system(f'rm -rf {f}')
    print(pad+' Unzipping...')
    os.system(f'unzip -u {zipLocation} > /dev/null;rm {zipLocation}')
    version = subprocess.Popen(['cat' ,'changelog'],stdout=subprocess.PIPE).communicate()[0].decode('utf-8').split('\n')[0].replace(':','')
    print(pad+f'Asztal updated to version {version}')

if __name__ == '__main__':
    getNew()
    start()
