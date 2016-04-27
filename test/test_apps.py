import json
import os.path
import shutil
import tempfile
import unittest

from seqremote.apps import (
    OneCodexApp, capture_json_output, gzip_if_needed,
)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def copy_to_temp(fp):
    with open(fp) as f:
        data = f.read()
    temp_file = tempfile.NamedTemporaryFile(
        prefix="PCMP_test_", suffix=".fastq")
    temp_file.write(data)
    temp_file.seek(0)
    return temp_file


class UtilityFunctionTests(unittest.TestCase):
    def test_capture_json_output(self):
        def function_that_prints_json(x, y):
            print '{{"x": "{}",'.format(x)
            print '"y": "{}"}}'.format(y)
        observed = capture_json_output(
            function_that_prints_json, "hello", "world")
        expected = {"x": "hello", "y": "world"}
        self.assertEqual(observed, expected)

    def test_gzip_if_needed(self):
        temp_dir = tempfile.mkdtemp()
        fp = os.path.join(temp_dir, "test.fasta")
        with open(fp, "w") as f:
            f.write("abcdefg\n1234567890\n")
        self.assertEqual(gzip_if_needed(fp), (True, fp + ".gz"))
        # Original file should still be there
        self.assertTrue(os.path.exists(fp))
        shutil.rmtree(temp_dir)


class OneCodexAppTests(unittest.TestCase):
    def test_analysis_output_base(self):
        self.assertEqual(
            OneCodexApp._analysis_output_base(ANALYSES[0]),
            "decontam_PCMP_sample_5001-03_R1_ref_79e49bd0f3d2424d")

    def test_analyses_are_finished(self):
        self.assertTrue(OneCodexApp.analyses_are_finished(ANALYSES))
        
    def test_get_sample_id(self):
        sample_id = OneCodexApp._get_sample_id(
            "PCMP_test_8wz9Nj.fastq", SAMPLES)
        self.assertEqual(sample_id, "31bc5173fd934832")
        
    @unittest.skipUnless(os.getenv("TEST_ONE_CODEX"), "Generates junk datasets")
    def test_assign_file(self):
        sample_data_fp = os.path.join(THIS_DIR, "chop_5015_02.fastq")
        sample_file = copy_to_temp(sample_data_fp)
        print sample_file.name
        output_dir = tempfile.mkdtemp()
        app = OneCodexApp()
        summary = app.assign_sample(sample_file.name, output_dir, 10, 100)
        print os.listdir(output_dir)
        self.assertEqual(len(summary), 2)


ANALYSES = json.loads("""\
[
    {
        "analysis_status": "Success",
        "id": "582a4d7356174c67",
        "reference_id": "79e49bd0f3d2424d",
        "reference_name": "RefSeq Complete Genomes",
        "sample_filename": "decontam_PCMP_sample_5001-03_R1.fastq",
        "sample_id": "7bfbd8d5c63e4e71"
    },
    {
        "analysis_status": "Success",
        "id": "ce9b63e410dd4dc6",
        "reference_id": "d1bff177777e4ac7",
        "reference_name": "One Codex Database (July 2015)",
        "sample_filename": "decontam_PCMP_sample_5001-03_R1.fastq",
        "sample_id": "7bfbd8d5c63e4e71"
    },
    {
        "analysis_status": "Success",
        "id": "c9406e83f7c24ca6",
        "reference_id": "79e49bd0f3d2424d",
        "reference_name": "RefSeq Complete Genomes",
        "sample_filename": "illqc_PCMP_sample_5001-03_R1.fastq",
        "sample_id": "68186c8b4a654246"
    },
    {
        "analysis_status": "Success",
        "id": "f7c5eca0092242a0",
        "reference_id": "d1bff177777e4ac7",
        "reference_name": "One Codex Database (July 2015)",
        "sample_filename": "illqc_PCMP_sample_5001-03_R1.fastq",
        "sample_id": "68186c8b4a654246"
    },
    {
        "analysis_status": "Success",
        "id": "9bd1f43f083c4bfb",
        "reference_id": "79e49bd0f3d2424d",
        "reference_name": "RefSeq Complete Genomes",
        "sample_filename": "PCMP_sample_7001-01_R1.fastq",
        "sample_id": "47db5725c76943ae"
    },
    {
        "analysis_status": "Success",
        "id": "5dc2421eac594027",
        "reference_id": "d1bff177777e4ac7",
        "reference_name": "One Codex Database (July 2015)",
        "sample_filename": "PCMP_sample_7001-01_R1.fastq",
        "sample_id": "47db5725c76943ae"
    },
    {
        "analysis_status": "Success",
        "id": "cab60ce1d32243dc",
        "reference_id": "79e49bd0f3d2424d",
        "reference_name": "RefSeq Complete Genomes",
        "sample_filename": "PCMP_sample_7001-01_R2.fastq",
        "sample_id": "44a4d0139f1b4d8f"
    },
    {
        "analysis_status": "Success",
        "id": "d9e71bc406244214",
        "reference_id": "d1bff177777e4ac7",
        "reference_name": "One Codex Database (July 2015)",
        "sample_filename": "PCMP_sample_7001-01_R2.fastq",
        "sample_id": "44a4d0139f1b4d8f"
    },
    {
        "analysis_status": "Success",
        "id": "1f51160ee1de4af2",
        "reference_id": "79e49bd0f3d2424d",
        "reference_name": "RefSeq Complete Genomes",
        "sample_filename": "PCMP_sample_5001-03_R2.fastq",
        "sample_id": "0b0efb8a555f4a7e"
    },
    {
        "analysis_status": "Success",
        "id": "6d6778032b8c44bb",
        "reference_id": "d1bff177777e4ac7",
        "reference_name": "One Codex Database (July 2015)",
        "sample_filename": "PCMP_sample_5001-03_R2.fastq",
        "sample_id": "0b0efb8a555f4a7e"
    },
    {
        "analysis_status": "Success",
        "id": "4573e2a530d441a9",
        "reference_id": "bf35962aced64e66",
        "reference_name": "One Codex Database",
        "sample_filename": "decontam_PCMP_sample_5001-03_R1.fastq",
        "sample_id": "7bfbd8d5c63e4e71"
    },
    {
        "analysis_status": "Success",
        "id": "c0db6e0430564940",
        "reference_id": "bf35962aced64e66",
        "reference_name": "One Codex Database",
        "sample_filename": "illqc_PCMP_sample_5001-03_R1.fastq",
        "sample_id": "68186c8b4a654246"
    },
    {
        "analysis_status": "Success",
        "id": "586ed917e6f64a89",
        "reference_id": "bf35962aced64e66",
        "reference_name": "One Codex Database",
        "sample_filename": "PCMP_sample_5001-03_R2.fastq",
        "sample_id": "0b0efb8a555f4a7e"
    },
    {
        "analysis_status": "Success",
        "id": "e533b559c9bc44c1",
        "reference_id": "bf35962aced64e66",
        "reference_name": "One Codex Database",
        "sample_filename": "PCMP_sample_7001-01_R2.fastq",
        "sample_id": "44a4d0139f1b4d8f"
    },
    {
        "analysis_status": "Success",
        "id": "b76afc1182694f01",
        "reference_id": "bf35962aced64e66",
        "reference_name": "One Codex Database",
        "sample_filename": "PCMP_sample_7001-01_R1.fastq",
        "sample_id": "47db5725c76943ae"
    }
]
""")
        
SAMPLES = json.loads("""\
[
    {
        "filename": "PCMP_cryptococcus.1.L1_R1_unpaired.fastq",
        "id": "513c963513ad426e",
        "upload_status": "Successfully uploaded."
    
},
    {
        "filename": "PCMP_vibriolambda.2.L1_R1_unpaired.fastq",
        "id": "7a1cfa2434d34599",
        "upload_status": "Successfully uploaded."
    
},
    {
        "filename": "lambda.fasta",
        "id": "579db690db3a4cdb",
        "upload_status": "Successfully uploaded."
    
},
    {
        "filename": "PCMP_s98_R1.fastq.gz",
        "id": "dc648b2e632d40b1",
        "upload_status": "Successfully uploaded."
    
},
    {
        "filename": "PCMP_test_8wz9Nj.fastq",
        "id": "31bc5173fd934832",
        "upload_status": "Successfully uploaded."
    
}

]
""")
