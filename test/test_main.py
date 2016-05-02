import unittest

from seqremote.main import convert_json_to_table

class FunctionTests(unittest.TestCase):
    def test_convert_json_to_table(self):
        self.assertEqual(list(convert_json_to_table(TWOTAXA_JSON)), TWOTAXA_TABLE)

TWOTAXA_JSON = [
    {
        "readcount": 42546,
        "name": "Eukaryota",
        "rank": "superkingdom",
        "tax_id": 2759,
    }, {
        "readcount": 26079,
        "name": "Anaerococcus",
        "rank": "genus",
        "tax_id": 165779,
    }
]

TWOTAXA_TABLE = [
    ["readcount", "name", "rank", "tax_id"],
    ["42546", "Eukaryota", "superkingdom", "2759"],
    ["26079", "Anaerococcus", "genus", "165779"],
]
