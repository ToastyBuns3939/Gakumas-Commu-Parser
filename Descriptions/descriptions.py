import json


class DescriptionStore:
    id_descriptions: dict[str, dict]
    other_descriptions: list[dict]

    def __init__(self):
        self.id_descriptions = {}
        self.other_descriptions = []

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

    desc_primary_key_suffixes = [
        ".produceDescriptionType",
        ".examDescriptionType",
        ".examEffectType",
        ".produceCardCategory",
        ".produceCardMovePositionType",
        ".produceStepType",
        ".targetId",
    ]

    @classmethod
    def get_primary_key_prefix(cls, primary_keys):
        desc_primary_key_suffix = cls.desc_primary_key_suffixes[0]
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
                for suffix in cls.desc_primary_key_suffixes
            ]
        ):
            return desc_primary_key
        else:
            raise ValueError("Primary key does not have all the right suffixes!")

    @classmethod
    def strip_defaults(cls, description):
        return dict(
            (key, description[key])
            for key, value in cls.description_defaults.items()
            if description[key] != value
        )

    @classmethod
    def fill_defaults(cls, description):
        return dict(
            (key, description.get(key, value))
            for key, value in cls.description_defaults.items()
        )

    @classmethod
    def is_plain_string(cls, description):
        if (
            description.get("produceDescriptionType", "")
            != "ProduceDescriptionType_PlainText"
        ):
            return False
        if "text" not in description:
            description["text"] = ""
        return description.keys() == {"produceDescriptionType", "text"}

    @classmethod
    def is_diff_string(cls, description):
        if (
            description.get("produceDescriptionType", "")
            != "ProduceDescriptionType_DiffText"
        ):
            return False
        if "text" not in description:
            description["text"] = ""
        return description.keys() == {"produceDescriptionType", "text"}

    exam_customise_head = "ExamDescriptionType_Customize"

    @classmethod
    def is_exam_customize(cls, description):
        if (
            description.get("produceDescriptionType", "")
            != "ProduceDescriptionType_Exam"
        ):
            return False
        if not (
            description.get("examDescriptionType", "").startswith(
                cls.exam_customise_head
            )
        ):
            return False
        if "text" not in description:
            description["text"] = ""
        return description.keys() == {
            "produceDescriptionType",
            "examDescriptionType",
            "text",
        }

    @classmethod
    def get_hash(cls, description):
        target_id = description.get("targetId", "")
        if target_id != "":
            return f"id:{target_id}"
        elif cls.is_plain_string(description):
            return f"plaintext:{description["text"]}"
        elif cls.is_diff_string(description):
            return f"difftext:{description["text"]}"
        elif cls.is_exam_customize(description):
            custom_type = description["examDescriptionType"][
                len(cls.exam_customise_head) :
            ]
            return f"custom:{custom_type}:{description["text"]}"
        else:
            return ""

    def get_other_index(self, description):
        try:
            return self.other_descriptions.index(description)
        except ValueError:
            self.other_descriptions.append(description)
            return len(self.other_descriptions) - 1

    def get_id(self, description):
        id = self.get_hash(description)
        if id != "":
            if id not in self.id_descriptions:
                self.id_descriptions[id] = description
            if self.id_descriptions[id] != description:
                return self.get_other_index(description)
            return id
        return self.get_other_index(description)

    def get_description(self, id):
        if isinstance(id, int):
            return self.other_descriptions[id]
        else:
            return self.id_descriptions[id]

    def print_descriptions(self, out_filename: str):
        sorted_descriptions = dict(sorted(self.id_descriptions.items()))
        out_file = open(out_filename, "w", encoding="utf8")
        json.dump(
            {
                "id_descriptions": sorted_descriptions,
                "other_descriptions": self.other_descriptions,
            },
            out_file,
            ensure_ascii=False,
            indent=2,
        )
        out_file.close()

    def load_descriptions(self, in_filename: str):
        in_file = open(in_filename, encoding="utf8")
        json_object = json.load(in_file)
        in_file.close()

        self.id_descriptions = json_object["id_descriptions"]
        self.other_descriptions = json_object["other_descriptions"]

    def shorten_json(self, in_filename: str, out_filename: str):
        in_file = open(in_filename, encoding="utf8")
        json_object = json.load(in_file)
        in_file.close()

        desc_primary_key = self.get_primary_key_prefix(
            json_object["rules"]["primaryKeys"]
        )

        for item in json_object["data"]:
            item[desc_primary_key] = [
                self.get_id(self.strip_defaults(desc_item))
                for desc_item in item[desc_primary_key]
            ]

        out_file = open(out_filename, "w", encoding="utf8")
        json.dump(json_object, out_file, ensure_ascii=False, indent=2)
        out_file.close()

    def lengthen_json(self, in_filename: str, out_filename: str):
        in_file = open(in_filename, encoding="utf8")
        json_object = json.load(in_file)
        in_file.close()

        desc_primary_key = self.get_primary_key_prefix(
            json_object["rules"]["primaryKeys"]
        )

        for item in json_object["data"]:
            item[desc_primary_key] = [
                self.fill_defaults(self.get_description(id))
                for id in item[desc_primary_key]
            ]

        out_file = open(out_filename, "w", encoding="utf8")
        json.dump(json_object, out_file, ensure_ascii=False, indent=2)
        out_file.close()
