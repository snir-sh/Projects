example = {
    '_id': 2234436, 
    'mispar_rechev': 28479503, 
    'tozeret_cd': 1450, 
    'sug_degem': 'P', 
    'tozeret_nm': "צ'רי סין", # make, mutag
    'degem_cd': 2, # make code
    'degem_nm': 'DB21B', 
    'ramat_gimur': 'PR NOBEL', 
    'ramat_eivzur_betihuty': 2, 
    'kvutzat_zihum': 15, 
    'shnat_yitzur': 2022, 
    'degem_manoa': 'SQRF4J16', 
    'mivchan_acharon_dt': '2025-10-08', 
    'tokef_dt': '2026-10-25', 
    'baalut': 'פרטי', 
    'misgeret': 'LVTDB21B1ND271543', 
    'tzeva_cd': 11, 
    'tzeva_rechev': 'שחור מטלי', 
    'zmig_kidmi': '235/55R18', 
    'zmig_ahori': '235/55R18', 
    'sug_delek_nm': 'בנזין', 
    'horaat_rishum': 221711, 
    'moed_aliya_lakvish': '2022-10', 
    'kinuy_mishari': 'TIGGO 8 PRO', 
    'rank': 0.057308756
}

FIELD_META = {
    "mispar_rechev": {
        "labels": {"he": "מספר רישוי", "en": "License plate"},
        "type": "string",
    },
    "tozeret_cd": {
        "labels": {"he": "קוד יצרן", "en": "Manufacturer code"},
        "type": "int",
    },
    "tozeret_nm": {
        "labels": {"he": "יצרן", "en": "Manufacturer"},
        "type": "string",
    },
    "degem_cd": {
        "labels": {"he": "קוד דגם", "en": "Model code"},
        "type": "int",
    },
    "degem_nm": {
        "labels": {"he": "דגם", "en": "Model"},
        "type": "string",
    },
    "sug_degem": {
        "labels": {"he": "סוג דגם", "en": "Model type"},
        "type": "string",
    },
    "ramat_gimur": {
        "labels": {"he": "רמת גימור", "en": "Trim level"},
        "type": "string",
    },
    "kinuy_mishari": {
        "labels": {"he": "כינוי מסחרי", "en": "Trim name"},
        "type": "string",
    },
    "degem_manoa": {
        "labels": {"he": "מנוע", "en": "Engine"},
        "type": "string",
    },
    "sug_delek_nm": {
        "labels": {"he": "סוג דלק", "en": "Fuel type"},
        "type": "string",
    },
    "shnat_yitzur": {
        "labels": {"he": "שנת ייצור", "en": "Year"},
        "type": "int",
    },
    "baalut": {
        "labels": {"he": "בעלות", "en": "Ownership"},
        "type": "string",
    },
    "misgeret": {
        "labels": {"he": "מספר שלדה", "en": "VIN"},
        "type": "string",
    },
    "tzeva_cd": {
        "labels": {"he": "קוד צבע", "en": "Color code"},
        "type": "int",
    },
    "tzeva_rechev": {
        "labels": {"he": "צבע", "en": "Color"},
        "type": "string",
    },
    "zmig_kidmi": {
        "labels": {"he": "צמיג קדמי", "en": "Front tire"},
        "type": "string",
    },
    "zmig_ahori": {
        "labels": {"he": "צמיג אחורי", "en": "Rear tire"},
        "type": "string",
    },
    "ramat_eivzur_betihuty": {
        "labels": {"he": "רמת אבזור בטיחותי", "en": "Safety level"},
        "type": "int",
    },
    "kvutzat_zihum": {
        "labels": {"he": "קבוצת זיהום", "en": "Emission group"},
        "type": "int",
    },
    "mivchan_acharon_dt": {
        "labels": {"he": "מבחן רישוי אחרון", "en": "Last inspection"},
        "type": "date",
    },
    "tokef_dt": {
        "labels": {"he": "תוקף רישיון", "en": "License valid until"},
        "type": "date",
    },
    "moed_aliya_lakvish": {
        "labels": {"he": "מועד עליה לכביש", "en": "First on road"},
        "type": "date",
    },
    "horaat_rishum": {
        "labels": {"he": "הערת רישום", "en": "Registration note"},
        "type": "int",
    },
    "rank": {
        "labels": {"he": "דירוג", "en": "Rank"},
        "type": "double",
    },
}

def record_by_language(record: dict, lang: str = "he") -> dict:
    """
    Return all labels + values for a single language.

    Example output:
    {
      "מספר רישוי": "6523031",
      "יצרן": "TOYOTA",
      "דגם": "COROLLA"
    }
    """
    out = {}

    for field, value in record.items():
        meta = FIELD_META.get(field)
        if not meta:
            continue

        label = meta.get("labels", {}).get(lang)
        if not label:
            continue

        out[label] = value

    return out
 