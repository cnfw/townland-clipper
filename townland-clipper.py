import sys
import os.path
import json
from pprint import pprint

counties = ['antrim', 'armagh', 'carlow', 'cavan', 'clare', 'cork', 'derry', 'donegal', 'down', 'dublin', 'fermanagh',
            'galway', 'kerry', 'kildare', 'kilkenny', 'laois', 'leitrim', 'limerick', 'longford', 'louth', 'mayo',
            'meath', 'monaghan', 'offaly', 'roscommon', 'sligo', 'tipperary', 'tyrone', 'waterford', 'westmeath',
            'wexford', 'wicklow']

json_file_path = ''
json_data = None


def get_menu_choice():
    print("\n\nChoose an option from the menu")
    print(41 * '=')
    print("1. View list of townlands by county")
    print("2. Extract townlands by county")
    print("3. Convert geoJSON to GPX")
    print("4. Exit")

    return input("> ")


def get_process_name(menu_choice):
    return {
        '1': 'list-townlands-in-county',
        '2': 'not-ready',
        '3': 'not-ready',
        '4': 'exit',
    }.get(menu_choice, None)


def start_exit_process():
    if input("Are you sure? (y/n)\n> ") == 'y':
        print("Goodbye")
        global json_data
        json_data = None
        sys.exit(0)


def load_json_file(file_path):
    try:
        json_file = open(file_path, encoding='utf8')
    except FileNotFoundError:
        print("That file wasn't found... Please check your file path.")
        return False
    except IsADirectoryError:
        print("Please enter a file path, not a directory path.")
        return False
    except IOError:
        print("There was some problem loading that file...")
        return False
    else:
        # Load file contents into a JSON object
        global json_data
        json_data = json.load(json_file)

        json_file.close()
        return True


def input_path_and_load_file():
    # Start a loop
    while True:
        path_input = input("Enter a file path or 'exit' to leave.\n> ")
        if path_input.upper() == 'EXIT':
            start_exit_process()
        if not load_json_file(path_input.strip('\"')):
            if input("Try again? (y/n)\n> ") != 'y':
                return
            else:
                continue
        else:
            print("File loaded! Returning to the main menu.")
            global json_file_path
            json_file_path = path_input
            break


def get_county_choice():
    print("List of counties:\n")
    for county in counties:
        print(county.capitalize())

    # Start a loop
    while True:
        county_input = input("Enter a county name (case insensitive)\n> ")
        if county_input not in counties and input("Invalid input. Try again? (y/n)") != 'y':
            break

    return county_input.strip()


def print_list_of_townlands_by_county(county):
    print("Townlands in " + county.capitalize())
    townlands = []
    for townland in json_data['features']:
        if townland['properties']['COUNTY'] == county.upper():
            townlands.append(str(townland['properties']['TD_ENGLISH']).lower().capitalize())

    townlands.sort()
    for townland in townlands:
        print(townland)


def main():
    # Start a loop
    while True:
        menu_choice = get_menu_choice()
        process_name = get_process_name(menu_choice)

        if process_name == 'not-ready':
            print("This feature isn't ready yet, sorry!")
        elif process_name == 'list-townlands-in-county':
            county = get_county_choice()
            print_list_of_townlands_by_county(county)
        elif process_name == 'exit':
            start_exit_process()


def print_header():
    print(41 * '=')
    print("Waze UK & Ireland Community")
    print("This script extracts information from")
    print("the huge OSI townland datasets into")
    print("more manageable files.")
    print(41 * '=')
    print("Title: Townland Clipper")
    print("Version: 0.0")
    print("Author: cw1998")
    print("Date: 24/04/18")
    # TODO print("Usage: See -h or --help")
    print("Python Version: 3")
    print(41 * '=')


if __name__ == '__main__':
    print_header()
    input_path_and_load_file()
    main()
