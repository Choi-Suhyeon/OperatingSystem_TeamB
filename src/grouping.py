from tabulate import tabulate
from functools import reduce

import argparse
import csv
import sys
import os

DATA_FILE = "user_group_data.csv"

def parse_args():
    def is_valid_args(command, target, args):
        if target not in ('usr', 'grp'):
            return False

        match command:
            case 'list':
                return not args

            case 'add' | 'rem':
                return len(args) >= 2

            case _:
                return False

    parser = argparse.ArgumentParser(description="Process user and group commands.")

    parser.add_argument('command', choices=['list', 'add', 'rem'], help='The command to execute.')
    parser.add_argument('target', choices=['usr', 'grp'], help='The target type (user or group).')
    parser.add_argument('args', nargs='*', help='Additional arguments based on the command and target.')

    result = parser.parse_args()

    if not is_valid_args(result.command, result.target, result.args):
        print(f'{os.path.basename(sys.argv[0])} : error: invalid arguments', file=sys.stderr)
        sys.exit(1)

    return result

def read_data():
    data = {}

    if not os.path.exists(DATA_FILE):
        return data

    with open(DATA_FILE, 'r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            user       = row['user']
            groups     = row['groups'].split(',') if row['groups'] else []
            data[user] = groups

    return data

def write_data(data):
    with open(DATA_FILE, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["user", "groups"])

        for user, groups in data.items():
            writer.writerow([user, ",".join(groups)])

def list_users(data):
    return tabulate(sorted([[u, ', '.join(sorted(gs))] for u, gs in data.items()], key=lambda x: x[0]), tablefmt='rst', headers=('User', 'Groups'))

def list_groups(data):
    users_in_groups = {}

    for u, gs in data.items():
        for g in gs:
            users_in_groups.setdefault(g, []).append(u)

    return tabulate(sorted([[g, ', '.join(sorted(us))] for g, us in users_in_groups.items()], key=lambda x: x[0]), tablefmt='rst', headers=('Group', 'Users'))

def add_group(data, args):
    [group_name, *users] = args

    if group_name in {group for groups in data.values() for group in groups}:
        return None

    for u in users:
        try:
            data[u].append(group_name) 
        except:
            return None

    return data

def remove_group(data, args):
    [group_name, *users] = args

    for u in users:
        try:
            data[u].remove(group_name)
        except:
            continue

    return data
    

def add_user(data, args):
    [user_name, *groups] = args

    data.setdefault(user_name, []).extend(groups)

    data[user_name] = list(set(data[user_name]))

    return data

def remove_user(data, args):
    [user_name, *groups] = args

    if user_name not in data.keys():
        return None

    for g in groups:
        try:
            data[user_name].remove(g)
        except:
            continue

    if not data[user_name]:
        data.pop(user_name)
    
    return data

if __name__ == "__main__":
    parsed_args     = parse_args() 
    user_group_data = read_data()

    match (parsed_args.command, parsed_args.target):
        case ('list', 'usr'):
            print(list_users(user_group_data))

        case ('list', 'grp'):
            print(list_groups(user_group_data))

        case ('add', 'usr'):
            if (data := add_user(user_group_data, parsed_args.args)) is not None:
                write_data(data)
            else:
                print('command failed', file=sys.stderr)

        case ('add', 'grp'):
            if (data := add_group(user_group_data, parsed_args.args)) is not None:
                write_data(data)
            else:
                print('command failed', file=sys.stderr)

        case ('rem', 'usr'):
            if (data := remove_user(user_group_data, parsed_args.args)) is not None:
                write_data(data)
            else:
                print('command failed', file=sys.stderr)

        case ('rem', 'grp'):
            if (data := remove_group(user_group_data, parsed_args.args)) is not None:
                write_data(data)
            else:
                print('command failed', file=sys.stderr)

