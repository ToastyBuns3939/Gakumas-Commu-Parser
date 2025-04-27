import json

description_defaults = {
    "produceDescriptionType": "ProduceDescriptionType_Unknown",
    "examDescriptionType": "ExamDescriptionType_Unknown",
    "examEffectType": "ProduceExamEffectType_Unknown",
    "produceCardCategory": "ProduceCardCategory_Unknown",
    "produceCardMovePositionType": "ProduceCardMovePositionType_Unknown",
    "produceStepType": "ProduceStepType_Unknown",
    "targetId": "",
    "text": "",
}

descriptions: dict[str, dict] = {}
other_descriptions: list[dict] = []


def strip_defaults(description):
    for key, value in description_defaults.items():
        if description[key] == value:
            description.pop(key)


def get_other_index(description):
    try:
        return other_descriptions.index(description)
    except ValueError:
        other_descriptions.append(description)
        index = len(other_descriptions) - 1
        descriptions[f"~other:{index}"] = description
        return index


def is_plain_string(description):
    if (
        description.get("produceDescriptionType", "")
        != "ProduceDescriptionType_PlainText"
    ):
        return False
    if "text" not in description:
        description["text"] = ""
    return description.keys() == {"produceDescriptionType", "text"}


def is_diff_string(description):
    if (
        description.get("produceDescriptionType", "")
        != "ProduceDescriptionType_DiffText"
    ):
        return False
    if "text" not in description:
        description["text"] = ""
    return description.keys() == {"produceDescriptionType", "text"}


exam_customise_head = "ExamDescriptionType_Customize"


def is_exam_customize(description):
    if description.get("produceDescriptionType", "") != "ProduceDescriptionType_Exam":
        return False
    if not (description.get("examDescriptionType", "").startswith(exam_customise_head)):
        return False
    if "text" not in description:
        description["text"] = ""
    return description.keys() == {
        "produceDescriptionType",
        "examDescriptionType",
        "text",
    }


def get_hash(description):
    target_id = description.get("targetId", "")
    if target_id != "":
        return f"id:{target_id}"
    elif is_plain_string(description):
        return f"plaintext:{description["text"]}"
    elif is_diff_string(description):
        return f"difftext:{description["text"]}"
    elif is_exam_customize(description):
        custom_type = description["examDescriptionType"][len(exam_customise_head) :]
        return f"custom:{custom_type}:{description["text"]}"
    else:
        return ""


def get_id(description):
    id = get_hash(description)
    if id != "":
        if id not in descriptions:
            descriptions[id] = description
        if descriptions[id] != description:
            return get_other_index(description)
        return id
    return get_other_index(description)


desc_primary_key_suffixes = [
    ".produceDescriptionType",
    ".examDescriptionType",
    ".examEffectType",
    ".produceCardCategory",
    ".produceCardMovePositionType",
    ".produceStepType",
    ".targetId",
]


def get_description_primary_key(primary_keys):
    desc_primary_key_suffix = desc_primary_key_suffixes[0]
    desc_primary_keys = [
        key[: -len(desc_primary_key_suffix)]
        for key in primary_keys
        if key.endswith(desc_primary_key_suffix)
    ]
    if len(desc_primary_keys) == 0:
        raise ValueError("No primary key with the right suffix!")

    desc_primary_key = desc_primary_keys[0]
    if all(
        [
            (desc_primary_key + suffix) in primary_keys
            for suffix in desc_primary_key_suffixes
        ]
    ):
        return desc_primary_key
    else:
        raise ValueError("Primary key does not have all the right suffixes!")


def shorten_json(filename: str, out_filename: str):
    in_file = open(filename, encoding="utf8")
    json_object = json.load(in_file)
    in_file.close()

    desc_primary_key = get_description_primary_key(json_object["rules"]["primaryKeys"])

    for item in json_object["data"]:
        for description in item[desc_primary_key]:
            strip_defaults(description)
        item_descriptions = item.pop(desc_primary_key)
        descriptionIds = [get_id(desc_item) for desc_item in item_descriptions]
        item[desc_primary_key + "Ids"] = descriptionIds

    out_file = open(out_filename, "w", encoding="utf8")
    json.dump(json_object, out_file, ensure_ascii=False, indent=2)
    out_file.close()


def print_descriptions(out_filename: str):
    sorted_descriptions = dict(sorted(descriptions.items()))
    out_file = open(out_filename, "w", encoding="utf8")
    json.dump(sorted_descriptions, out_file, ensure_ascii=False, indent=2)
    out_file.close()
