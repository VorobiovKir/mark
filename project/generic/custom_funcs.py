from django.conf import settings


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

    file_info = clear_str.split('/')

    try:
        res_dict[file_info[1]][file_info[2]][file_info[3]].append(file_info[4])
    except:
        if file_info[1] in res_dict:
            if file_info[2] in res_dict[file_info[1]]:
                res_dict[file_info[1]][file_info[2]].update({
                    file_info[3]: [file_info[4]]
                })
            else:
                res_dict[file_info[1]].update({
                    file_info[2]: {
                        file_info[3]: [file_info[4]]
                    }})
        else:
            res_dict.update({
                file_info[1]: {
                    file_info[2]: {
                        file_info[3]: [file_info[4]]
                    }
                }
            })

    return res_dict


def sorted_by_time(clear_file_list):
    """sorted list by time

    get clean file list and return list sorted by year, month, day

    Returns:
        [list] -- list clean file
    """
    return sorted(clear_file_list,
                  key=lambda x: (x.split('/')[1],
                                 settings.FOLDER_NAME_MONTH.index(
                                    x.split('/')[2]),
                                 x.split('/')[3]))

# def sorted_clear_dict(clear_dict):
#     for key in clear_dict.keys():
#         sorted(clear_dict[key]
#
