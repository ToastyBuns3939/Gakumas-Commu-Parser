import re


class ParsingString:
    def __init__(self, string: str):
        self.string = string

    def retrieve(self, pattern: re.Pattern[str] | str):
        # Attempts to match the string with the pattern
        # Removes the whole match from the string,
        # and returns the first group of the match
        # Note re.match only matches the start of the string
        match = re.match(pattern, self.string)
        if not match:
            raise Exception(
                f"Failed to retrieve pattern\n{pattern}\n"
                + f"from string\n{self.string}"
            )
        self.string = self.string[match.end() :]
        return match.group(1)

    def peek(self, pattern: re.Pattern[str] | str):
        match = re.match(pattern, self.string)
        return bool(match)

    def is_empty(self):
        return self.string == ""


type PropertyValue = str | CommuGroup


class CommuGroup:
    def __init__(self, group_type: str):
        self.group_type = group_type
        self.properties: dict[str, list[PropertyValue]] = {}

    def append_property(self, key: str, value: PropertyValue):
        if key not in self.properties:
            self.properties[key] = [value]
        else:
            self.properties[key].append(value)

    def get_property(self, key: str, defaultValue: PropertyValue):
        if key not in self.properties:
            return defaultValue
        found_properties = self.properties[key]
        if len(found_properties) == 1:
            return found_properties[0]
        else:
            raise Exception(f"More than one property with key '{key}' found in group!")

    def get_property_list(self, key: str):
        return self.properties[key]

    def modify_property(self, key: str, value: PropertyValue):
        if key in self.properties:
            self.properties[key] = [value for _ in self.properties[key]]

    @classmethod
    def from_commu_line(cls, text_to_parse: str):
        parsing_string = ParsingString(text_to_parse.strip())
        group = parse_group(parsing_string)
        if not parsing_string.is_empty():
            raise Exception("Additional text found on the end of text to parse!")
        return group

    def __str__(self):
        parts = [self.group_type] + [
            f"{key}={property_value_to_string(value)}"
            for key, values in self.properties.items()
            for value in values
        ]
        return "[" + " ".join(parts) + "]"


def unescape_string(string: str):
    return string.replace("\\n", "\n")


def escape_string(string: str):
    return string.replace("\n", "\\n")


def property_value_to_string(value: PropertyValue):
    if isinstance(value, str):
        return escape_string(value)
    else:
        return str(value)


def parse_group_type(parsing_string: ParsingString):
    return parsing_string.retrieve(r"([a-z]+)(?=[ \]])")


# This function gobbles up the = as well!
def parse_key(parsing_string: ParsingString):
    return parsing_string.retrieve(r"([A-Za-z]+)=")


def parse_string_data(parsing_string: ParsingString):
    # The first match-group consists of any character except
    # linebreak, backslash, square brackets, and equals, unless they are
    # in the combinations '\n' or '\='
    return parsing_string.retrieve(r"((?:[^\n\\\[\]=]|\\n|\\=)+)(?=[ \]])")


def parse_json_data(parsing_string: ParsingString):
    return parsing_string.retrieve(r"(\\\{\S+\\\})(?=[ \]])")


def parse_animation_curve_json_data(parsing_string: ParsingString):
    return parsing_string.retrieve(r"(AnimationCurve::\\\{\S+\\\})(?=[ \]])")


def parse_group(parsing_string: ParsingString) -> CommuGroup:
    parsing_string.retrieve(r"(\[)")
    group_type = parse_group_type(parsing_string)
    group = CommuGroup(group_type)
    while not parsing_string.peek(r"\]"):
        parsing_string.retrieve(r"( )")
        key = parse_key(parsing_string)
        value: PropertyValue
        if parsing_string.peek(r"\["):
            value = parse_group(parsing_string)
        elif parsing_string.peek(r"AnimationCurve::\\\{"):
            value = parse_animation_curve_json_data(parsing_string)
        elif parsing_string.peek(r"\\\{"):
            value = parse_json_data(parsing_string)
        else:
            value = unescape_string(parse_string_data(parsing_string))
        group.append_property(key, value)
    parsing_string.retrieve(r"(\])")
    return group
