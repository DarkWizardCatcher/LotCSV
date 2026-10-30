# Living off the CSV

```
$$\                 $$\      $$$$$$\   $$$$$$\  $$\    $$\ 
$$ |                $$ |    $$  __$$\ $$  __$$\ $$ |   $$ |
$$ |      $$$$$$\ $$$$$$\   $$ /  \__|$$ /  \__|$$ |   $$ |
$$ |     $$  __$$\\_$$  _|  $$ |      \$$$$$$\  \$$\  $$  |
$$ |     $$ /  $$ | $$ |    $$ |       \____$$\  \$$\$$  / 
$$ |     $$ |  $$ | $$ |$$\ $$ |  $$\ $$\   $$ |  \$$$  /  
$$$$$$$$\\$$$$$$  | \$$$$  |\$$$$$$  |\$$$$$$  |   \$  /   
\________|\______/   \____/  \______/  \______/     \_/    
                                                           
```

This project aims to streamline work of detection engineers and threat hunters. It's purpose is to gather different data sources from Living off the Land oprojects and gathers them into .csv files to easily work with them inside various security tools like SIEM. There is feature which adds "is_legit" column. Cou can use it while filtering lines by setting true or false values. 

You can check how exported .csv files look in [directory](https://github.com/DarkWizardCatcher/LotCSV/tree/main/export)

You can find nice source for all Living off the Land projects at https://lolol.farm/

## How to use

To retrieve all implemented projects follow these steps: 

```
git clone https://github.com/DarkWizardCatcher/LotCSV.git
cd LotCSV
pip install -r requirements.txt
python LotCSV.py -a -alp
```

Otherwise use `python LotCSV.py -h` to get help.

## Done
- [x] https://www.bootloaders.io/
- [x] https://gtfobins.github.io/
- [x] https://hijacklibs.net/
- [x] https://lofl-project.github.io/
- [x] https://lolad-project.github.io/
- [x] https://lolrmm.io/
- [x] https://lolbas-project.github.io/
- [x] https://www.loldrivers.io/
- [x] https://lolc2.github.io/
- [x] https://lottunnels.github.io/
- [x] https://lolesxi-project.github.io/LOLESXi/
- [x] https://lots-project.com
- [x] https://www.iana.org/assignments/service-names-port-numbers/
- [x] https://www.loobins.io
- [x] https://github.com/ReversecLabs/lolcerts
- [x] https://lolapps-project.github.io
- [x] https://lotwebhooks.github.io/index.html
- [x] https://wadcoms.github.io
- [x] https://boostsecurityio.github.io/lotp/

## ToDo
- [ ] https://filesec.io
- [ ] https://malapi.io
- [ ] https://wtfbins.wtf/
- [ ] https://0xanalyst.github.io/Project-Lost/