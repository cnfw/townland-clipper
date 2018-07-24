import os
import sys
import argparse
import ijson
import simplejson as json

counties = ['carlow', 'cavan', 'clare', 'cork', 'donegal', 'dublin', 'galway', 'kerry', 'kildare', 'kilkenny', 'laois',
            'leitrim', 'limerick', 'longford', 'louth', 'mayo', 'meath', 'monaghan', 'offaly', 'roscommon', 'sligo',
            'tipperary', 'waterford', 'westmeath', 'wexford', 'wicklow']

gaeltacht_counties = ['donegal', 'mayo', 'galway', 'kerry', 'cork', 'waterford', 'meath']

json_file_path = ''
json_file = None
json_data = None
total_number_of_townlands = 61098  # From Wikipedia


def write_progress(count, total=total_number_of_townlands, text=''):
    bar_len = 50  # one notch for every 2%
    filled_length = int(round(bar_len * count / float(total)))

    percent_complete = round(100.0 * count / float(total), 1)
    bar_text = '=' * filled_length + '-' * (bar_len - filled_length)

    # Clear previous line
    sys.stdout.write('[%s] %s%s %s\r' % (bar_text, percent_complete, '%', text))
    sys.stdout.flush()


def load_json_file(file_path=None):
    if file_path is None:
        file_path = json_file_path
    try:
        global json_file
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
        json_data = ijson.items(json_file, 'features.item')

        return json_data


def list_counties():
    print("List of counties:")
    for x, y, z in zip(counties[::3][0], counties[1::3][0], counties[2::3][0]):
        print('{:<15}{:<15}{:<}'.format(x.capitalize(), y.capitalize(), z.capitalize()))

    print('Note that the counties in Northern Ireland are not included here.')


def round_list(coord_list, round_to=4):
    for i, coord in enumerate(coord_list):
        if type(coord) is list:
            round_list(coord, round_to=4)
        else:
            coord_list[i] = round(coord, round_to)


def clean_townland_dict(townland_dict, keep_gaeilge=False):
    # Remove unused properties
    new_properties = {
        'NAME_ENGLISH': str(townland_dict['properties']['TD_ENGLISH'])
    }
    if keep_gaeilge and str(townland_dict['properties']['COUNTY']).lower() in gaeltacht_counties:
        new_properties['NAME_GAEILGE'] = str(townland_dict['properties']['TD_GAEILGE'])

    townland_dict['properties'] = new_properties

    # Remove some coordinate precision
    round_list(townland_dict['geometry']['coordinates'])

    return townland_dict


def extract_townlands_by_county(county, output_directory, index=0, total=total_number_of_townlands,
                                reduce=False, gaeilge=False):
    # To save changing to upper case in each for loop iteration
    county_upper = county.upper()

    # Make up a list of townlands in the given county
    json_file_iterator = load_json_file(json_file_path)
    townlands_dict_features = []

    for townland in json_file_iterator:
        write_progress(index, total=total, text=county_upper)
        index += 1
        if townland['properties']['COUNTY'] == county_upper:
            if reduce:
                clean_townland_dict(townland, gaeilge)
            townlands_dict_features.append(townland)

    # Put the new townland list into a new dictionary in the same format as original
    townlands_dict = {
        'type': 'FeatureCollection',
        'features': townlands_dict_features
    }

    # Write the dictionary to a file in JSON representation
    new_file_path = '{0}\\townlands_{1}{2}{3}.geojson'.format(output_directory, 'reduced_' if reduce else '',
                                                              'with_gaeilge_' if gaeilge and reduce else '', county)

    with open(new_file_path, 'w') as o_file:
        json.dump(townlands_dict, o_file)


def is_input_valid(parser, values):
    # Validate arguments #
    input_valid = True
    # Make sure there is a path
    if not values.path:
        parser.error("Path not supplied")
        input_valid = False

    # Load up the file
    global json_file_path
    json_file_path = values.path
    print(json_file_path)
    if not load_json_file():
        input_valid = False

    # Check output directory is a directory
    if not os.path.isdir(values.output_directory):
        parser.error("Output supplied is not a directory.")
        input_valid = False

    # Make sure specific county wasn't specified with all
    if values.all and values.county:
        parser.error("--all and --county supplied. Only one should be supplied")
        input_valid = False

    # Make sure county specified is valid (if a county was specified)
    if values.county and str(values.county).lower() not in counties:
        parser.error('County specified was invalid. Check and try again (run --counties to see list of valid counties')
        input_valid = False

    return input_valid


def main():
    parser = setup_parser()
    values = parser.parse_args()
    if values.info:
        print_header()
        sys.exit(0)

    if values.counties:
        list_counties()
        sys.exit(0)

    # Throw in the towel if something went wrong
    if not is_input_valid(parser, values):
        sys.exit(1)

    # Warn user that this might take a while
    print("Depending on the size of the input file, this could take a very long time. Please be patient!")

    # Work out what to do
    if values.county:
        print("Extracting {0} townland information from {1}".format('reduced' if values.reduce else 'full',
                                                                   str(values.county).capitalize()))
        extract_townlands_by_county(values.county, values.output_directory, reduce=values.reduce,
                                    gaeilge=values.gaeilge)

    elif values.all:
        print("Extracting {0} townland information for all counties.".format('reduced' if values.reduce else 'full'))
        index = 0
        for county in counties:
            print("Now extracting " + county.upper())
            index += 1
            extract_townlands_by_county(county, values.output_directory, reduce=values.reduce, gaeilge=values.gaeilge,
                                        index=index * total_number_of_townlands,
                                        total=len(counties) * total_number_of_townlands)


def print_header():
    print(41 * '=')
    print("Waze UK & Ireland Community")
    print("This script extracts information from")
    print("the huge OSI townland datasets into")
    print("more manageable files.")
    print(41 * '=')
    print("Title: Townland Clipper")
    print("Version: 0.1")
    print("Author: cw1998")
    print("Date: 24/04/18")
    print("Updated: 27/04/2018")
    print("Usage: See -h or --help")
    print("Python Version: 3")
    print(41 * '=')


def setup_parser():
    parser = argparse.ArgumentParser(
        description='This script extracts information from the huge OSI townland datasets.')

    parser.add_argument('path', nargs='?', help='Path to file')
    parser.add_argument('-o', '--output', dest='output_directory', default=os.getcwd(),
                        help='Place to put the processed file(s). Defaults to working directory.')
    parser.add_argument('-c', '--county', type=str, help='Specify which county to extract from the file.')
    parser.add_argument('-r', '--reduce', action='store_true', help='Reduce geometry precision to save file size.')
    parser.add_argument('-a', '--all', action='store_true', help='Process all counties')
    parser.add_argument('-g', '--gaeilge', '--irish', action='store_true',
                        help='Keep Gaeilge townland spellings for Gaeltacht areas when --reduce is provided.')
    parser.add_argument('--counties', action='store_true', help='Print a list of counties supported then exit.')
    parser.add_argument('--info', action='store_true', help='Show some information about the programme.')

    return parser


def cleanup():
    global json_data
    global json_file
    json_data = None
    json_file.close()


if __name__ == '__main__':
    main()
    cleanup()

    sys.exit(0)
