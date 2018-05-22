import re
import warnings

from cyutils.address.road_types import STREET_NAMES
from cyutils.address.road_types import STREET_ABBREVIATION_TO_NAME


street_desc = "ST\.?|SAINT|KING|QUEEN|UPPER|LOWER|HALF|GREAT|WEST|EAST|NORTH|SOUTH|OLD"
street_names = '|'.join(STREET_NAMES)
street_loc = "NORTH[,]|SOUTH[,]|EAST[,]|WEST[,]"
ROAD_PATTERN = r"((\b({}) )?[A-Za-z']+ ({})\b( {})?)"
ROAD_PATTERN = re.compile(ROAD_PATTERN.format(street_desc,
                                              street_names,
                                              street_loc))

POSTCODE_PATTERN = re.compile(r'(\b[A-Z]{1,2}[0-9][0-9A-Z]? ?([0-9][A-Z]{2}))')

number_prefix = 'UNIT|UNITS|FLAT|FLATS'
numeric_part_1 = '\d*-?\d+[A-Z/]*'
numeric_part_2 = '(-\d*[A-Z]*)?'
NUMBER_PATTERN = r"((\b({}) )?({})+({}))"
NUMBER_PATTERN = re.compile(NUMBER_PATTERN.format(number_prefix,
                                                  numeric_part_1,
                                                  numeric_part_2))


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
    capture_groups = ROAD_PATTERN.findall(full_address)
    if capture_groups:
        name, _type = process_capture_groups(capture_groups)
        return '{} {}'.format(name, _type)
    return ''


def postcode(full_address):
    return capture_address_element(POSTCODE_PATTERN, full_address)


def number(full_address):
    warning_message = (
        """ \n This parser should be used with the knowledge that this
            function is open to four significant vulnerabilities:
               1) `number()` will parse the first numeric characters it
                  an address string contains (read from left to right).
                  If the address string has:
                    a) no building number
                    b) numeric characters unrelated to addressable
                       information at the start of the address string
               2) Address numbers separated by `&` or `,` will not be parsed
               3) Building names that include numeric characters are
                  incorrectly parsed as building numbers\n """
    )
    warnings.warn(warning_message)
    return capture_address_element(NUMBER_PATTERN, full_address)


def capture_address_element(regex_object, full_address):
    full_address = normalise_address(full_address)
    capture_groups = regex_object.findall(full_address)
    if capture_groups:
        return capture_groups[0][0]
    return ''


def normalise_address(address):
    return re.sub('\s+', ' ', str(address).upper()).replace(' ,', ',')
