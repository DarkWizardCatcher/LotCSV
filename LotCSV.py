import os
import yaml
import requests
import json
from bs4 import BeautifulSoup
import sys
import random
import urllib.parse

def GetRepository(url: str) -> None:
    directory = url.split("/")[4]
    if not os.path.exists(directory):
        print(" \033[1;90m[\033[1;33m+\033[1;90m]\033[0m Cloning repository...")
        os.system(f"git clone {url}")
    else:
        print(" \033[1;90m[\033[1;33m+\033[1;90m]\033[0m Pulling repository...")
        os.system(f"cd {directory} && git pull")
    print()

def FindFiles(path: str, extension: str, exclude: list[str] = []) -> list[str]:
    """
    Crawls through specified directory and returns files with specific extenstion. You can also exclude directories and files.
    """
    found_files = []
    for root, dirs, files in os.walk(path):
        if not any(excl in root for excl in exclude):
            for file in files:
                if file.endswith(extension) and not any(excl in file for excl in exclude):
                    found_files.append(os.path.join(root, file))
    found_files.reverse()
    return found_files

def ReadFiles(files: list[str]) -> tuple[list[str], list[dict]]:
    """
    Reads files from FindFiles.
    """
    values = []
    keys = []
    def recursive_parse(data: dict | list | str, collected_data: dict, parent_key: str = "") -> None:
        if isinstance(data, dict):
            for key, val in data.items():
                new_key = f"{parent_key}_{key}" if parent_key else key
                if new_key.strip() not in keys: keys.append(new_key.strip())
                recursive_parse(val, collected_data, new_key.strip())
        elif isinstance(data, list):
            for item in data: recursive_parse(item, collected_data, parent_key)
        else:
            if "{'" not in str(data) and "'}" not in str(data):
                if parent_key in collected_data:
                    if isinstance(collected_data[parent_key], list): collected_data[parent_key].append(data)
                    else: collected_data[parent_key] = [collected_data[parent_key], data]
                else: collected_data[parent_key] = data
    for file in files:
        print(f" \033[1;90m[\033[1;36m~\033[1;90m] \033[0mReading: {file}                                  ", end="\r")
        with open(file, "r", errors="ignore") as f:
            try:
                contents = yaml.safe_load(f.read())
                collected_data = {}
                recursive_parse(contents, collected_data)
                values.append(collected_data)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML file {file}: {e}")
    return keys, values

def ReadMDFiles(files: list[str]) -> tuple[list[str], list[dict]]:
    values = []
    keys = []
    def recursive_parse(data: dict | list | str, collected_data: dict, parent_key: str = "") -> None:
        if isinstance(data, dict):
            for key, val in data.items():
                new_key = f"{parent_key}_{key}" if parent_key else key
                if new_key not in keys: keys.append(new_key)
                recursive_parse(val, collected_data, new_key)
        elif isinstance(data, list):
            for item in data: recursive_parse(item, collected_data, parent_key)
        else:
            if "{'" not in str(data) and "'}" not in str(data):
                if parent_key in collected_data:
                    if isinstance(collected_data[parent_key], list): collected_data[parent_key].append(data)
                    else: collected_data[parent_key] = [collected_data[parent_key], data]
                else: collected_data[parent_key] = data
    for file in files:
        print(f" \033[1;90m[\033[1;36m~\033[1;90m] \033[0mReading: {file}                                  ", end="\r")
        with open(file, "r", errors="ignore") as f:
            content_raw = f.read().splitlines()
            content_raw.pop(len(content_raw)-1)
            content = "\n".join([str(i) for i in content_raw])
            try:
                contents = yaml.safe_load(content)
                collected_data = {}
                recursive_parse(contents, collected_data)
                values.append(collected_data)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML file {file}: {e}")
    return keys, values

def WriteExportCsv(output: str, values: list[dict], keys: list[str]) -> bool:
    """
    Exports collected data from yml file into csv.
    """
    def sanitize(val: list | tuple):
        if isinstance(val, (list, tuple)):
            val = "[" + "-|-".join(f"''{str(item)}''" for item in val) + "]"
        else:
            val = str(val)
        val = val.replace('"', '""')                        # Escape double quotes
        val = val.replace('\n', ' ').replace('\r', ' ')     # Remove newlines
        return val.strip()
    with open(output, "w", encoding="utf-8", errors="ignore") as f:
        head = '"' + '","'.join([k.strip() for k in keys]) + '","is_legit"' + '\n'
        f.write(head)
        for value in values:
            line_items = []
            for key in keys:
                val = value.get(key, "")
                sanitized = sanitize(val)
                line_items.append(sanitized)
            line = '"' + '","'.join(line_items) + '","false"' + '\n'
            f.write(line)
    print(f"\n \033[1;90m[\033[1;32m+\033[1;90m]\033[0m Output file\033[1;90m:\033[0m \033[1;93m{output}\033[0m")
    return os.path.exists(output)

def StringifyExistingCsv(content: str,output: str) -> bool:
    """
    Just makes csv as strings.
    """
    result = []
    for line in content.splitlines():
        row = []
        value = ""
        in_quotes = False
        i = 0
        while i < len(line):
            char = line[i]
            if char == '"' and (i == 0 or line[i - 1] != "\\"):
                in_quotes = not in_quotes
            elif char == "," and not in_quotes:
                row.append(value.strip())
                value = ""
            else:
                value += char
            i += 1
        row.append(value.strip())
        result.append([str(cell) for cell in row])

    with open(output,"w", encoding="utf-8", errors="ignore") as f:
        for j,i in enumerate(result):
            f.write('"' + '","'.join(i) + '","is_legit"'+"\n") if j == 0 else f.write('"' + '","'.join(i) + '","false"'+"\n")
    print(f" \033[1;90m[\033[1;32m+\033[1;90m]\033[0m Output file\033[1;90m:\033[0m \033[1;93m{output}\033[0m")
    return os.path.exists(output)

def ReadSpecificYml(path: str) -> None:
    keys, values = ReadFiles([path])
    print(values)
    print("\n\n -------------------------------------------- \n\n")
    print(keys)

def GetLOLC2(output: str) -> bool:
    def ParseJSON(contents: str) -> tuple[list[dict], list[str]]:
        values = []
        keys = []

        content = json.loads(contents)
        for i in content:
            collected_data = {}
            collected_data["name"] = i
            if not "name" in keys: keys.append("name")
            for j in content[i]:
                if not j in keys: keys.append(j)
                if "descriptionUrl" in j:
                    with open("lolc2.github.io/"+content[i][j],"r",encoding="utf-8",errors="ignore") as f:desc_raw = f.read().splitlines()
                    for l,k in enumerate(desc_raw):
                       if not k.startswith("###") and not ("![" in k and "](" in k) and len(k)>2 and not l>5: desc = k;break
                    collected_data[j] = desc
                else:
                    if isinstance(content[i][j], list):
                        collected_data[j] = []
                        for k in content[i][j]:
                            collected_data[j].append(k)
                    else:
                        collected_data[j, content[i][j]]
            values.append(collected_data)
        return values, keys
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting LOLC2")
    GetRepository("https://github.com/lolc2/lolc2.github.io")

    with open("lolc2.github.io/c2_data.json","r",encoding="utf-8",errors="ignore") as f:
        contents = f.read()
    values, keys = ParseJSON(contents)
    return WriteExportCsv(output, values, keys)


def GetGTFOBins(output: str) -> bool:
    def WriteExportMdCsv(output: str, values: list[dict], keys: list[str], md_files: list[str]) -> bool:
        def sanitize(val: list | tuple):
            if isinstance(val, (list, tuple)):
                val = "[" + "-|-".join(f"''{str(item)}''" for item in val) + "]"
            else:
                val = str(val)
            val = val.replace('"', '""')                        # Escape double quotes
            val = val.replace('\n', ' ').replace('\r', ' ')     # Remove newlines
            return val.strip()
        with open(output, "w", encoding="utf-8", errors="ignore") as f:
            head = '"Name","' + '","'.join([k.strip() for k in keys]) + '","is_legit"' + '\n'
            f.write(head)
            for i,value in enumerate(values):
                line_items = []
                for key in keys:
                    val = value.get(key, "")
                    sanitized = sanitize(val)
                    line_items.append(sanitized)
                line = f'"{md_files[i].split("/")[2].split(".md")[0]}' + '","'.join(line_items) + '","false"' + '\n'
                f.write(line)
        print(f"\n \033[1;90m[\033[1;32m+\033[1;90m]\033[0m Output file\033[1;90m:\033[0m \033[1;93m{output}\033[0m")
        return os.path.exists(output)
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting GTFOBins")
    GetRepository("https://github.com/GTFOBins/GTFOBins.github.io")

    md_files = FindFiles("GTFOBins.github.io/_gtfobins/",".md")
    keys, values = ReadMDFiles(md_files)
    return WriteExportMdCsv(output,values,keys,md_files)

def GetLOLBAS(output: str) -> bool:
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting LOLBAS")
    GetRepository("https://github.com/LOLBAS-Project/LOLBAS")

    yml_files = FindFiles("LOLBAS/yml/",".yml",["HonorableMentions"])
    keys, values = ReadFiles(yml_files)
    return WriteExportCsv(output,values,keys)


def GetLOLDrivers(output: str) -> bool:
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting LOLDrivers")
    content = requests.get("https://www.loldrivers.io/api/drivers.csv").text
    with open(output,"w",errors='ignore') as f:
        for j,i in enumerate(content.splitlines()):
            f.write( i + ',"is_legit"'+"\n") if j == 0 else f.write( i + ',"false"'+"\n")

    print(f" \033[1;90m[\033[1;32m+\033[1;90m]\033[0m Output file\033[1;90m:\033[0m \033[1;93m{output}\033[0m")
    return os.path.exists(output)

def GetHijackLibs(output: str) -> bool:
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting HijackLibs")
    GetRepository("https://github.com/wietze/HijackLibs")

    yml_files = FindFiles("HijackLibs/yml/",".yml")
    keys, values = ReadFiles(yml_files)
    return WriteExportCsv(output,values,keys)

def GetBootloaders(output: str) -> bool:
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting Bootloaders")
    content = requests.get("https://www.bootloaders.io/api/bootloaders.csv").text
    return StringifyExistingCsv(content,output)

def GetLOFLCAB(output: str) -> bool:
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting LOFLCAB")
    GetRepository("https://github.com/LOFL-Project/LOFLCAB/")

    yml_files = FindFiles("LOFLCAB/yml/",".yml")
    keys, values = ReadFiles(yml_files)
    return WriteExportCsv(output,values,keys)

def GetLOLAD(output: str) -> bool:
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting LOLAD")
    content = requests.get("https://lolad-project.github.io/").text

    soup = BeautifulSoup(content,"html.parser")
    keys = []
    for tag in soup.tr:
        if len(tag.string.strip()) > 0: keys.append(tag.string.strip().replace(" ","_"))
    rows = soup.find_all("tr")
    values = []
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) == 4:
            command_data = {
                keys[0]: cols[0].text.strip(),
                keys[1]: cols[1].text.strip(),
                keys[2]: cols[2].text.strip(),
                keys[3]: cols[3].find("a")["href"] if cols[3].find("a") else ""
            }
            values.append(command_data)
    return WriteExportCsv(output, values, keys)

def GetLOLRMM(output: str) -> bool:
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting LOLRMM")
    content = requests.get("https://lolrmm.io/api/rmm_tools.csv").text
    return StringifyExistingCsv(content,output)

def GetLOTTunnels(output:str) -> bool:
    def WriteExportMdCsv(output: str, values: list[dict], keys: list[str], md_files: list[str]) -> bool:
        def sanitize(val: list | tuple):
            if isinstance(val, (list, tuple)):
                val = "[" + "-|-".join(f"''{str(item)}''" for item in val) + "]"
            else:
                val = str(val)
            val = val.replace('"', '""')                        # Escape double quotes
            val = val.replace('\n', ' ').replace('\r', ' ')     # Remove newlines
            return val.strip()
        with open(output, "w", encoding="utf-8", errors="ignore") as f:
            head = '"' + '","'.join([k.strip() for k in keys]) + '","is_legit"' + '\n'
            f.write(head)
            for i,value in enumerate(values):
                line_items = []
                for key in keys:
                    val = value.get(key, "")
                    sanitized = sanitize(val)
                    line_items.append(sanitized)
                line = f'"' + '","'.join(line_items) + '","false"' + '\n'
                f.write(line)
        print(f"\n \033[1;90m[\033[1;32m+\033[1;90m]\033[0m Output file\033[1;90m:\033[0m \033[1;93m{output}\033[0m")
        extracted = []
        for i in values:
            if isinstance(i["Detection_Domain"], list):
                for k in i["Detection_Domain"]:
                    data = {}
                    data["Name"] = i["Name"]
                    data["Domain"] = k
                    extracted.append(data)
            else:
                data = {}
                data["Name"] = i["Name"]
                data["Domain"] = i["Detection_Domain"]
                extracted.append(data)
        with open(output.split(".csv")[0]+"_domain.csv", "w", encoding="utf-8", errors="ignore") as f:
            f.write('"Name","Domain","is_legit"\n')
            for i,value in enumerate(extracted):
                line_items = []
                for key in ["Name","Domain"]:
                    val = value.get(key, "")
                    sanitized = sanitize(val)
                    line_items.append(sanitized)
                line = f'"' + '","'.join(line_items) + '","false"' + '\n'
                f.write(line)
        print(f"\n \033[1;90m[\033[1;32m+\033[1;90m]\033[0m Output file\033[1;90m:\033[0m \033[1;93m{output.split('.csv')[0]}_domain.csv\033[0m")
        return os.path.exists(output) and os.path.exists(output.split(".csv")[0]+"_domain.csv")


    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting LOTTunels")
    GetRepository("https://github.com/LOTTunnels/LOTTunnels.github.io")

    md_files = FindFiles("LOTTunnels.github.io/_lottunnels/Binaries/",".md")
    keys, values = ReadMDFiles(md_files)
    return WriteExportMdCsv(output,values,keys,md_files)

def GetLOLESXi(output: str) -> bool:
    def WriteExportMdCsv(output: str, values: list[dict], keys: list[str], md_files: list[str]) -> bool:
        def sanitize(val: list | tuple):
            if isinstance(val, (list, tuple)):
                val = "[" + "-|-".join(f"''{str(item)}''" for item in val) + "]"
            else:
                val = str(val)
            val = val.replace('"', '""')                        # Escape double quotes
            val = val.replace('\n', ' ').replace('\r', ' ')     # Remove newlines
            return val.strip()
        with open(output, "w", encoding="utf-8", errors="ignore") as f:
            head = '"Name"' + '","'.join([k.strip() for k in keys]) + '","is_legit"' + '\n'
            f.write(head)
            for i,value in enumerate(values):
                line_items = []
                for key in keys:
                    val = value.get(key, "")
                    sanitized = sanitize(val)
                    line_items.append(sanitized)
                line = f'"' + '","'.join(line_items) + '","false"' + '\n'
                f.write(line)
        print(f"\n \033[1;90m[\033[1;32m+\033[1;90m]\033[0m Output file\033[1;90m:\033[0m \033[1;93m{output}\033[0m")
        return os.path.exists(output)
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting LOLESXi")
    GetRepository("https://github.com/LOLESXi-Project/LOLESXi/")

    md_files = FindFiles("LOLESXi/_lolesxi/Binaries/",".md")
    keys, values = ReadMDFiles(md_files)
    return WriteExportMdCsv(output,values,keys,md_files)

def GetLOLCerts(output: list[str]) -> bool:
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting LOLCerts")
    GetRepository("https://github.com/ReversecLabs/lolcerts/")

    all_results = []

    for i in output:
        yml_files = FindFiles(f"lolcerts/{i.split("/")[1].split("_")[1][:-4]}/",".yml")
        keys, values = ReadFiles(yml_files)
        all_results.append(WriteExportCsv(i,values,keys))

    return True if not False in all_results else False

def GetLotsProject(output: str, additional_info: bool = False) -> bool:
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting Lots-Project") if not additional_info else print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting Lots-Project (Additional)")
    content = requests.get("https://lots-project.com/").text
    soup = BeautifulSoup(content,"html.parser")
    values = []

    for row in soup.find_all("tr")[1:]:
        cols = row.find_all("td")
        tags = [span.text.strip() for span in cols[1].find_all("div")]
        link = "https://lots-project.com"+row.find_all("a")[0]["href"]
        if additional_info:
            keys = ["Website","Tags","Service Provider","Info_Phishing","Info_C&C","Info_Exfiltration","Info_Download","Info_Sample"]
            soup1 = BeautifulSoup(requests.get(link).text,"html.parser")
            divs = soup1.find_all("div", class_="detail-container")
            additonal = {}
            for i in divs:
                print(f" \033[1;90m[\033[1;36m~\033[1;90m] \033[0mGetting ({cols[0].text.strip()}): {link}                                              ", end="\r")
                if "Tags" in i.get_text(): pass
                elif "Phishing" in i.get_text():
                    div2 = i.find("div", class_="content")
                    if div2: additonal["phishing"] = div2.string.strip()
                elif "Command and Control" in i.get_text():
                    div2 = i.find("div", class_="content")
                    if div2: additonal["c2"] = div2.string.strip()
                elif "Exfiltration" in i.get_text():
                    div2 = i.find("div", class_="content")
                    if div2: additonal["exfil"] = div2.string.strip()
                elif "Download" in i.get_text():
                    div2 = i.find("div", class_="content")
                    if div2: additonal["download"] = div2.string.strip()
                elif "Sample" in i.get_text():
                    div2 = i.find("div", class_="content")
                    if div2:
                        try: additonal["sample"] = div2.find("a", class_="link").string.strip()
                        except: additonal["sample"] = "None"
            if len(cols) == 3:
                command_data = {
                    keys[0]: cols[0].text.strip(),
                    keys[1]: tags,
                    keys[2]: cols[2].text.strip(),
                    keys[3]: additonal["phishing"],
                    keys[4]: additonal["c2"],
                    keys[5]: additonal["exfil"],
                    keys[6]: additonal["download"],
                    keys[7]: additonal["sample"]
                }
                values.append(command_data)
        else:
            keys = ["Website","Tags","Service Provider","Info"]
            if len(cols) == 3:
                command_data = {
                    keys[0]: cols[0].text.strip(),
                    keys[1]: tags,
                    keys[2]: cols[2].text.strip(),
                    keys[3]: link.strip()
                }
                values.append(command_data)
    return WriteExportCsv(output, values, keys)

def GetLotWebhooks(output: str) -> bool:
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting LOTWebhooks")
    content = requests.get("https://lotwebhooks.github.io").text
    soup = BeautifulSoup(content,"html.parser")
    values = []
    keys = ["Webhook Name", "URL", "Type", "Reference"]
    rows = soup.find_all("tr")
    values = []
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) == 4:
            command_data = {
                keys[0]: cols[0].text.strip(),
                keys[1]: cols[1].text.strip(),
                keys[2]: cols[2].text.strip(),
                keys[3]: cols[3].text.strip()
            }
            values.append(command_data)
    return WriteExportCsv(output, values, keys)

def GetLooBins(output: str) -> bool:
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting LOOBins")
    GetRepository("https://github.com/infosecB/LOOBins")

    yml_files = FindFiles("LOOBins/LOOBins/",".yml")
    keys, values = ReadFiles(yml_files)
    return WriteExportCsv(output,values,keys)

def GetLOLApps(output: str) -> bool:
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting LOLAPPS")
    GetRepository("https://github.com/LOLAPPS-Project/LOLAPPS/")

    yml_files = FindFiles("LOLAPPS/yml/",".yml")
    keys, values = ReadFiles(yml_files)
    return WriteExportCsv(output,values,keys)

def GetWADComs(output: str) -> bool:
    def WriteExportMdCsv(output: str, values: list[dict], keys: list[str], md_files: list[str]) -> bool:
        def sanitize(val: list | tuple):
            if isinstance(val, (list, tuple)):
                val = "[" + "-|-".join(f"''{str(item)}''" for item in val) + "]"
            else:
                val = str(val)
            val = val.replace('"', '""')                        # Escape double quotes
            val = val.replace('\n', ' ').replace('\r', ' ')     # Remove newlines
            return val.strip()
        with open(output, "w", encoding="utf-8", errors="ignore") as f:
            head = '"Name","' + '","'.join([k.strip() for k in keys]) + '","is_legit"' + '\n'
            f.write(head)
            for i,value in enumerate(values):
                line_items = []
                for key in keys:
                    val = value.get(key, "")
                    sanitized = sanitize(val)
                    line_items.append(sanitized)
                line = f'"{md_files[i].split("/")[2].split(".md")[0]}","' + '","'.join(line_items) + '","false"' + '\n'
                f.write(line)
        print(f"\n \033[1;90m[\033[1;32m+\033[1;90m]\033[0m Output file\033[1;90m:\033[0m \033[1;93m{output}\033[0m")
        return os.path.exists(output)
    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting WADComs")
    GetRepository("https://github.com/WADComs/WADComs.github.io")

    md_files = FindFiles("WADComs.github.io/_wadcoms/",".md")
    keys, values = ReadMDFiles(md_files)
    return WriteExportMdCsv(output,values,keys,md_files)

def GetPortList(output: str) -> bool:
    def GetFirst4(contents: str) -> tuple[list[dict], list[str]]:
        values = []
        keys = []
        c=0
        for j,i in enumerate(contents.splitlines()):
            collected_data = {}
            if j==0:
                for l,k in enumerate(i.split(",")):
                    if l < 4: keys.append(k)
            else:
                for l,k in enumerate(i.split(",")):
                    if l < 4:
                        collected_data[keys[l]] = k
                try:
                    if len(collected_data["Port Number"])>0 and isinstance(int(collected_data["Port Number"]),int):
                        values.append(collected_data)
                except: pass
        return values, keys


    print(" \033[1;90m[\033[1;96m~\033[1;90m]\033[0m Starting PortList")
    values, keys = GetFirst4(requests.get("https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv").text)

    return WriteExportCsv(output,values,keys)

def HandleSysArgs(help_menu: bool = False) -> None:
    global selected_sources, all_sources, additional_lots_project
    all_sources = False
    selected_sources = []
    additional_lots_project = False

    valid_sources = ["bootloaders", "gtfobins", "hijacklibs", "lolapps", "lolc2", "lolcerts", "loflcab", "lolad", "lolbas", "loldrivers", "lolrmm", "lottunnels", "lolesxi", "lots_project", "lots_project_additional", "loobins", "lotwebhooks", "wadcoms", "port_list"]

    version = "1.1.2"

    logo_col1 = random.randrange(60, 255); logo_col2 = random.randrange(60, 255); logo_col3 = random.randrange(60, 255)
    logo = f"\033[1;38;2;{logo_col1};{logo_col2};{logo_col3}m"+fr"""
$$\                 $$\      $$$$$$\   $$$$$$\  $$\    $$\ 
$$ |                $$ |    $$  __$$\ $$  __$$\ $$ |   $$ |
$$ |      $$$$$$\ $$$$$$\   $$ /  \__|$$ /  \__|$$ |   $$ |
$$ |     $$  __$$\\_$$  _|  $$ |      \$$$$$$\  \$$\  $$  |
$$ |     $$ /  $$ | $$ |    $$ |       \____$$\  \$$\$$  / 
$$ |     $$ |  $$ | $$ |$$\ $$ |  $$\ $$\   $$ |  \$$$  /  
$$$$$$$$\\$$$$$$  | \$$$$  |\$$$$$$  |\$$$$$$  |   \$  /   
\________|\______/   \____/  \______/  \______/     \_/    
                                                           """+f"\033[0;90mver: {version}\033[0m\n"

    helpmenu = f"""{logo}\n\nHelp menu:
    -h   , --help                         |   get some help
    -v   , --version                      |   get tool version
    -a   , --all                          |   get all sources and convert to csv
    -alp , --additional_lots_project      |   get more info from lots_project (making more traffic to the website) - needs to be added when requesting additional info!
    -g   , --get_specific                 |   get specific sources: {', '.join([i.strip() for i in valid_sources])}
    """
    if help_menu:print(helpmenu+"\n \033[0;31mERROR | Invalid argument \033[0m\n"); exit(0)

    for i, arg in enumerate(sys.argv):
        if arg.lower() == "-h" or arg.lower() == "--help":print(helpmenu); exit(0)
        elif arg.lower() == "-v" or arg.lower() == "--version":print(f"version: {version}"); exit(0)
        elif arg.lower() == "-alp" or arg.lower() == "--additional_lots_project":additional_lots_project=True
        elif arg.lower() == "-a" or arg.lower() == "--all":all_sources=True
        elif arg.lower() == "-g" or arg.lower() == "--get_specific":
            selected_sources = str(sys.argv[int(i+1)]).split(",")
            for i in selected_sources:
                if i not in valid_sources:
                    print(f"\n \033[0;31mERROR | Unknown selected source: {i} \033[0m")
                    exit(0)

        elif len(sys.argv) < 2: print(f"{helpmenu}\n\n \033[0;31m WARNING | Specify arguments \033[0m \n"); exit(0)


if __name__ == "__main__":
    HandleSysArgs()

    sources = {
        "bootloaders": lambda: GetBootloaders("export/bootloaders.csv"),
        "gtfobins": lambda: GetGTFOBins("export/gtfobins.csv"),
        "hijacklibs": lambda: GetHijackLibs("export/hijacklibs.csv"),
        "lolapps": lambda: GetLOLApps("export/lolapps.csv"),
        "lolc2": lambda: GetLOLC2("export/lolc2.csv"),
        "loflcab": lambda: GetLOFLCAB("export/loflcab.csv"),
        "lolad": lambda: GetLOLAD("export/lolad.csv"),
        "lolbas": lambda: GetLOLBAS("export/lolbas.csv"),
        "loldrivers": lambda: GetLOLDrivers("export/loldrivers.csv"),
        "lolrmm": lambda: GetLOLRMM("export/lolrmm.csv"),
        "lottunnels": lambda: GetLOTTunnels("export/lottunnels.csv"),
        "lolcerts": lambda: GetLOLCerts(["export/lolcerts_malicious.csv", "export/lolcerts_leaked.csv"]),
        "lolesxi": lambda: GetLOLESXi("export/lolesxi.csv"),
        "lots_project": lambda: GetLotsProject("export/lots_project.csv"),
        "lots_project_additional": lambda: GetLotsProject("export/lots_project_additional.csv", True),
        "loobins": lambda: GetLooBins("export/loobins.csv"),
        "lotwebhooks": lambda: GetLotWebhooks("export/lotwebhooks.csv"),
        "wadcoms": lambda: GetWADComs("export/wadcoms.csv"),
        "port_list": lambda: GetPortList("export/port_list.csv")
    }

    if not os.path.exists("export"): os.mkdir("export")

    if len(selected_sources)>0:
        if additional_lots_project and "lots_project" in selected_sources:
            selected_sources.pop(selected_sources.index("lots_project"))
            if not "lots_project_additional" in selected_sources: selected_sources.append("lots_project_additional")
        elif not additional_lots_project and "lots_project_additional" in selected_sources:
            print(f"\n \033[0;31mWARNING | You cannot fetch 'additional_lots_project': add -alp to fetch it\n\033[0m")
            selected_sources.pop(selected_sources.index("lots_project_additional"))
            if not "lots_project" in selected_sources: selected_sources.append("lots_project")
        for i in selected_sources: print(f" \033[1;90m[\033[1;32mDONE\033[1;90m]\033[0m {i}") if sources[i]() else print(f" \033[1;90m[\033[1;31mFAILED\033[1;90m]\033[0m {i}")
    elif sources:
        if additional_lots_project: del sources["lots_project"]
        elif not additional_lots_project: del sources["lots_project_additional"]
        for i in sources: print(f" \033[1;90m[\033[1;32mDONE\033[1;90m]\033[0m {i}") if sources[i]() else print(f" \033[1;90m[\033[1;31mFAILED\033[1;90m]\033[0m {i}")
    else:
        HandleSysArgs(True)