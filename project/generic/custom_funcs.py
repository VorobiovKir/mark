import json

from collections import OrderedDict

from django.conf import settings


def dropbox_get_note(client, path):
    """Dropbox get note

    Method get note's text

    """
    try:
        with client.get_file(path) as f:
            result = f.read()
    except:
        result = ''

    return result


def format_date(clear_str, res_dict=None):
    """format date

    Function get clear string {ex. /2016/jan/14/deez_something.txt} and
    return dict:
        ex. {'2016': {
            'jan': {
                '14': [deez_something.txt]
            }
        }}

    Returns:
        [dict] -- dictionary for formating timeliner
    """
    if not res_dict:
        res_dict = {}

    res_dict = OrderedDict(res_dict)

    file_info = clear_str.lower().split('/')

    try:
        res_dict[file_info[1]][file_info[2]][file_info[3]].append(clear_str)
    except:
        if file_info[1] in res_dict:
            if file_info[2] in res_dict[file_info[1]]:
                res_dict[file_info[1]][file_info[2]].update({
                    file_info[3]: [clear_str]
                })
            else:
                res_dict[file_info[1]].update({
                    file_info[2]: {
                        file_info[3]: [clear_str]
                    }})
        else:
            res_dict.update({
                file_info[1]: {
                    file_info[2]: {
                        file_info[3]: [clear_str]
                    }
                }
            })

    return res_dict


def sorted_by_time(clear_file_list):
    """sorted list by time

    get clean file list and return list sorted by Year, Month, Day

    Returns:
        [list] -- sorted list clean file
    """
    return sorted(clear_file_list,
                  key=lambda x: (x.split('/')[1],
                                 settings.FOLDER_NAME_MONTH.index(
                                    x.split('/')[2]),
                                 x.split('/')[3]))


def format_get_dict_full_info(clear_file_list, client):
    """Format get dict full info

    Method get note and return object
    format {
        path:
        project:
        tag:
        time:
        date:
        text:
    }
    """
    dict_key = 1
    res_dict = {}
    for file_name in clear_file_list:
        date, name = file_name.split('/deez_')
        info = name.split('_')
        res_dict[dict_key] = {
            'path': file_name,
            'project': info[0],
            'tag': info[1],
            'time': info[2],
            'date': date,
            'text': dropbox_get_note(client, file_name)
        }
        dict_key += 1
    return res_dict


def format_get_list_full_info(clear_file_list, client):
    """Format get list full info

    Method get note and return object
    format {
        path:
        project:
        tag:
        time:
        date:
        text:
    }
    """
    res_dict = []
    for file_name in clear_file_list:
        date, name = file_name.split('/deez_')
        info = name.split('_')
        res_files = []

        if client.search('.meta/files/{}/'.format(date), 'files_{}'.format(name)):
            file_path = '.meta/files/{}/files_{}'.format(date, name)
            files = dropbox_get_note(client, file_path)
            if files:
                print files
                res_files = json.loads(files)

        res_dict.append({
            'path': file_name,
            'project': info[0],
            'tag': info[1],
            'time': info[2],
            'date': date,
            'text': dropbox_get_note(client, file_name),
            'files': res_files
        })
    return res_dict
