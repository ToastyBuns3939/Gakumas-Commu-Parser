import openpyxl
from openpyxl.worksheet.formula import ArrayFormula


def get_original_formula(row_index):
    desc_cells = f"OFFSET($F{row_index}, 0, 0, 1, $E{row_index})"
    return ArrayFormula(f"C{row_index}", f'=TEXTJOIN("", FALSE, {desc_cells})')


def get_translation_formula(ref_sheet_name, row_index):
    desc_cells = f"OFFSET($F{row_index}, 0, 0, 1, $E{row_index})"
    search_range = f"{ref_sheet_name}!$A:$B"
    search = f"VLOOKUP({desc_cells}, {search_range}, 2, false)"
    return ArrayFormula(
        f"D{row_index}",
        f'=TEXTJOIN("", FALSE, IFERROR({search}, {desc_cells}))',
    )


def create_preview_worksheet(workbook, sheet_name, data):
    preview_worksheet = workbook.create_sheet(sheet_name + "-preview")
    workbook.create_sheet(sheet_name)
    rows = create_preview_rows(sheet_name, data)
    for row in rows:
        preview_worksheet.append(row)
    format_preview_worksheet(preview_worksheet)


def create_preview_rows(sheet_name, data):
    return [
        [
            "Id",
            "Name",
            "Original",
            "Translation",
            "Number of description parts",
            "Description parts",
        ],
    ] + [
        [
            item["id"],
            item.get("name", ""),
            get_original_formula(index + 2),
            get_translation_formula(sheet_name, index + 2),
            len(item["produceDescriptions"]),
        ]
        + [desc["text"] for desc in item["produceDescriptions"]]
        for index, item in enumerate(data)
    ]


def format_preview_worksheet(worksheet):
    worksheet.column_dimensions["A"].width = 30  # id column
    worksheet.column_dimensions["B"].width = 30  # name column
    worksheet.column_dimensions["C"].width = 60  # original text column
    worksheet.column_dimensions["D"].width = 60  # translation column

    alignment = openpyxl.styles.Alignment(
        horizontal="left",
        vertical="top",
        wrap_text=True,
    )
    for row in worksheet["C:D"]:
        for cell in row:
            cell.alignment = alignment
