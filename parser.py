import re

from cyutils.address.road_types import STREET_NAMES
from cyutils.address.road_types import STREET_ABBREVIATION_TO_NAME


street_desc = "ST\.?|SAINT|KING|QUEEN|UPPER|LOWER|HALF|GREAT|WEST|EAST|NORTH|SOUTH|OLD"
street_names = '|'.join(STREET_NAMES)
street_loc = "NORTH[,]|SOUTH[,]|EAST[,]|WEST[,]"
ROAD_PATTERN = r"((\b({}) )?[A-Za-z']+ ({})\b( {})?)"
ROAD_PATTERN = ROAD_PATTERN.format(street_desc, street_names, street_loc)
POSTCODE_PATTERN = r'(\b[A-Z]{1,2}[0-9][0-9A-Z]? ?([0-9][A-Z]{2}))'


def process_capture_groups(group):
    group = group[0][0].replace(',', '')
    group = group.split(' ')
    street_type = group[-1]
    street_name = ' '.join(group[:-1])
    if street_type in STREET_ABBREVIATION_TO_NAME.keys():
        street_type = STREET_ABBREVIATION_TO_NAME[street_type]
    return street_name, street_type


def street_address(full_address):
    full_address = normalise_address(full_address)
    capture_groups = re.findall(ROAD_PATTERN, full_address)
    if capture_groups:
        name, _type = process_capture_groups(capture_groups)
        return '{} {}'.format(name, _type)
    return ''


def postcode(full_address):
    full_address = normalise_address(full_address)
    capture_groups = re.findall(POSTCODE_PATTERN, full_address)
    if capture_groups:
        return capture_groups[0][0]
    return ''


def normalise_address(address):
    return re.sub('\s+', ' ', str(address).upper()).replace(' ,', ',')
