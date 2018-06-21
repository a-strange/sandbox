"""
Parser module for common address type transformations, i.e. normalising an
address string, extracting building number or expanding street type
abbreviations.

Example
-------
    >>> var = parser.street_address('privet dr')
    >>> var
    PRIVET DRIVE

Functions
---------
"""
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
    """
    For a list of matched ROAD_PATTERN objects, remove any commas, split on
    whitespace and if the last token is an abbreviation of a road type, replace
    it with the full string.

    :param list[tuple[str]] group: matched ROAD_PATTERN capture groups
    :returns: (concatenated address, extended abbreviation)
    :rtype: tuple[str, str]
    """
    group = group[0][0].replace(',', '')
    group = group.split(' ')
    street_type = group[-1]
    street_name = ' '.join(group[:-1])
    if street_type in STREET_ABBREVIATION_TO_NAME.keys():
        street_type = STREET_ABBREVIATION_TO_NAME[street_type]
    return street_name, street_type


def street_address(full_address):
    """
    Parse a street address string, normalising the string and replacing
    common abbreviations with expanded strings.

    .. doctest::
        >>> street_address('privet dr')
        PRIVET DRIVE

    :param str full_address: street address to parse
    :returns: parsed street address
    :rtype: str
    """
    full_address = normalise_address(full_address)
    capture_groups = ROAD_PATTERN.findall(full_address)
    if capture_groups:
        name, _type = process_capture_groups(capture_groups)
        return '{} {}'.format(name, _type)
    return ''


def postcode(full_address):
    """
    Parse a UK style postcode from a string.

    .. doctest::
        >>> postcode('9 Bywater St Chelsea, London SW3 4XD')
        SW3 4XD

    :param str full_address: string to parse
    :returns: matched postcode
    :rtype: str
    """
    return capture_address_element(POSTCODE_PATTERN, full_address)


def number(full_address):
    """
    Parse a building number from a string. Prints a warning related to use.

    .. doctest::
        >>> number('221 Baker Street')
        221

    :param str full_address: string to search for a building number
    :returns: matched building number
    :rtype: str
    """
    warning_message = """\n
        This parser should be used with the knowledge that this
        function is open to four significant vulnerabilities:
           1) `number()` will parse the first numeric characters it
              an address string contains (read from left to right).
              If the address string has:
                a) no building number
                b) numeric characters unrelated to addressable
                   information at the start of the address string
           2) Address numbers separated by `&` or `,` will not be parsed
           3) Building names that include numeric characters are
              incorrectly parsed as building numbers\n
    """
    warnings.warn(warning_message)
    return capture_address_element(NUMBER_PATTERN, full_address)


def capture_address_element(regex_object, full_address):
    """
    Search a string for the first instance of a regex pattern, returning the
    matched string. Return empty string if no match.

    :param _sre.SRE_Pattern regex_object: compiled regex pattern
    :param str full_address: string to search
    :returns: matched element or empty string
    :rtype: str
    """
    full_address = normalise_address(full_address)
    capture_groups = regex_object.search(full_address)
    if capture_groups:
        return capture_groups[0]
    return ''


def normalise_address(address):
    """
    Perform a normalisation of a string, replacing any whitespace characters
    with a single space, removing spaces prior to commas and uppercasing
    the string.

    :param str address: string to be normalised
    :returns: normalised string
    :rtype: str
    """
    return re.sub('\s+', ' ', str(address).upper()).replace(' ,', ',')
