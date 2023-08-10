#!python3

import sys, os, json, datetime
# from pathlib import Path
from typing import Tuple, Union, List

def parse_single_json_file(filepath:str, include_channel_id:bool=False) -> Union[dict, None]:
    if not filepath.endswith('.json'):
        return

    with open(filepath, 'r') as f:
        a = json.load(f)
    
    if a['type'] not in ('message', 'conversationUpdate'):
        return

    out = dict()
    out['timestamp'] = a['timestamp']
    if include_channel_id:
        out['channel_id'] = a['channelId']
    out['sender'] = a['from']['name']
    try:
        out['text'] = a['text']
    except KeyError:
        if 'attachments' in a:
            temp = []
            for i in a['attachments']:
                try:
                    temp.append(i['content']['text'])
                except KeyError:
                    continue
            if bool(temp):
                out['text'] = '\n'.join(temp)
        else:
            return

    return out

def parse_timestamp(iso_string :str):
    time_part, timezone_part = iso_string.split('+')
    main_part, fractional_part = time_part.split('.')
    fractional_part = fractional_part[:6].ljust(6, '0')  # Padding with zeros to 6 digits
    modified_iso_string = f"{main_part}.{fractional_part}+{timezone_part}"
    dt_object = datetime.datetime.fromisoformat(modified_iso_string)
    return dt_object

def combine_multiple_parse_dicts_to_single_str(dict_list:List[dict], seperator = ' - ') -> str:
    # Sort dict_list in place.
    dict_list.sort(key=lambda x: parse_timestamp(x['timestamp']))

    out = []
    for i in dict_list:
        if 'channel_id' in i:
            temp = f"{i['timestamp']}{seperator}{i['channel_id']}{seperator}{i['sender']}{seperator}{i['text']}"
        else:
            temp = f"{i['timestamp']}{seperator}{i['sender']}{seperator}{i['text']}"
        out.append(temp)

    return '\n'.join(out)

def extract_common_path_unique_paths(path_1:str, path_2:str) -> Tuple[str, str, str]:
    try:
        common_path = os.path.commonpath((path_1, path_2))
    except ValueError:
        common_path = None

    unique_path_1 = os.path.relpath(path_1, common_path) if common_path else path_1
    unique_path_2 = os.path.relpath(path_2, common_path) if common_path else path_2
    
    return common_path, unique_path_1, unique_path_2

def parse_transcript_tree(target_folder:str, save_folder, create_first_target_folder:bool=False, include_channel_id:bool=False) -> None:
    x, _, _ = extract_common_path_unique_paths(target_folder, save_folder)
    assert x != target_folder, 'save_folder is a folder within target_folder. This will make the code targeting wrong files. Exiting.'

    if create_first_target_folder:
        x = os.path.join(save_folder, os.path.basename(target_folder))
        os.makedirs(x, exist_ok=True)
        save_folder = x

    for folder, sub_folders, files in os.walk(target_folder):
        _, _, unique_target_path_2 = extract_common_path_unique_paths(target_folder, folder)

        # Folder case
        if len(files) == 0:
            if unique_target_path_2 != '.':
                os.makedirs(os.path.join(save_folder, unique_target_path_2), exist_ok=True)
        
        # Parse all files to single file case.
        else:
            temp_dict_list = []
            for file in files:
                print(f'parsing file = {file}')
                temp_out =  parse_single_json_file(os.path.join(folder, file), include_channel_id)
                if bool(temp_out):
                    temp_dict_list.append(temp_out)
            conv_text = combine_multiple_parse_dicts_to_single_str(temp_dict_list)

            x = os.path.basename(unique_target_path_2)
            if (unique_target_path_2 == '.') or x == unique_target_path_2:
                temp_save_folder = save_folder
            else:
                temp_save_folder = os.path.join(save_folder, os.path.dirname(unique_target_path_2))

            save_name = f'{os.path.basename(folder)}_conv.txt'

            with open(os.path.join(temp_save_folder, save_name), 'w') as f:
                f.write(conv_text)

if __name__ == '__main__':
    try:
        target_folder = sys.argv[1]
    except IndexError:
        target_folder = None
    
    try:
        save_folder = sys.argv[2]
    except IndexError:
        save_folder = None
    
    try:
        create_first_target_folder = sys.argv[3]
    except IndexError:
        create_first_target_folder = False # default behaviour
    
    try:
        include_channel_id = sys.argv[4]
    except IndexError:
        include_channel_id = False # default behaviour
    
    if not bool(target_folder) or not bool(save_folder):
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw() # Hide the root window

        if not bool(target_folder):
            print('Please select target folder to parse data from.')
            target_folder = filedialog.askdirectory()
        
        if not bool(save_folder):
            print('Please select folder to save folder data to.')
            save_folder = filedialog.askdirectory()

    print('Beginning parsing data.')
    parse_transcript_tree(target_folder, save_folder, create_first_target_folder, include_channel_id)
    print('Finished parsing data.')
