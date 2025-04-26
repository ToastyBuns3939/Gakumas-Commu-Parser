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


def get_index(description):
    try:
        return other_descriptions.index(description)
    except ValueError:
        other_descriptions.append(description)
        index = len(other_descriptions) - 1
        descriptions[f"other:{index}"] = description
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


def get_id(description):
    id = ""

    target_id = description.get("targetId", "")
    if target_id != "":
        id = f"id:{target_id}"
    elif is_plain_string(description):
        id = f"text:{description["text"]}"
    elif is_exam_customize(description):
        custom_type = description["examDescriptionType"][len(exam_customise_head) :]
        id = f"custom:{custom_type}:{description["text"]}"

    if id != "":
        if id not in descriptions:
            descriptions[id] = description
        if descriptions[id] != description:
            return get_index(description)
        return id

    return get_index(description)


def process_json(filename: str, out_filename: str):
    in_file = open(filename, encoding="utf8")
    json_object = json.load(in_file)
    in_file.close()

    for item in json_object["data"]:
        for description in item["produceDescriptions"]:
            strip_defaults(description)
        item_descriptions = item.pop("produceDescriptions")
        descriptionIndexes = [get_id(desc_item) for desc_item in item_descriptions]
        item["produceDescriptionIndexes"] = descriptionIndexes

    json_object["descriptions"] = dict(sorted(descriptions.items()))

    out_file = open(out_filename, "w", encoding="utf8")
    # json.dump(
    #     json_object, out_file, ensure_ascii=False, indent=None, separators=(",", ":")
    # )
    json.dump(json_object, out_file, ensure_ascii=False, indent=2)
    out_file.close()
    pass
