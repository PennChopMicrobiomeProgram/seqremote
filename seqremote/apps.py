import json
import os
import subprocess
import sys
import tempfile
import time

import onecodex.cli
import requests


def gzip_if_needed(fp):
    needs_gzip = not fp.endswith(".gz")
    if needs_gzip:
        subprocess.check_call(["gzip", "--keep", fp])
        fp = fp + ".gz"
    return needs_gzip, fp


class OneCodexApp(object):
    def __init__(self):
        self.api_key = os.getenv("ONE_CODEX_API_KEY")
        if self.api_key is None:
            raise RuntimeError(
                "Could not load API key from environment variable "
                "ONE_CODEX_API_KEY.\n")

    def assign_sample(self, sample_fp, output_dir, summary_fp, wait=120, timeout=86400):
        """Assign a single sample file, start to finish."""
        sample_id, sample_fn = self.upload_sample(sample_fp)
        starting_time = time.clock()
        time.sleep(wait)        
        while True:
            analyses = self.get_analyses(sample_fn)
            if self.analyses_are_finished(analyses):
                break
            total_time = time.clock() - starting_time
            if (total_time > timeout):
                raise RuntimeError("Timed out. {}".format(analyses))
            time.sleep(wait)
        summaries = self.retrieve_analyses(
            sample_fn, output_dir, summary_fp, analyses)
        return summaries

    def upload_sample(self, sample_fp, wait=10):
        """Upload a sample file and return uuid."""
        needed_gzip, gzipped_sample_fp = gzip_if_needed(sample_fp)
        print "GZIPPED_SAMPLE_FP:", gzipped_sample_fp
        self._cli(["upload", gzipped_sample_fp])
        time.sleep(wait)
        samples_json = self._api("samples")
        sample_fn = os.path.basename(gzipped_sample_fp)
        sample_id = self._get_sample_id(sample_fn, samples_json)
        if needed_gzip:
            os.remove(gzipped_sample_fp)
        return sample_id, sample_fn

    def get_sample_ids(self, sample_fps):
        samples_json = self._api("samples")
        all_sample_ids = dict(
            (r["filename"], r["id"]) for r in samples_json)
        sample_fns = map(os.path.basename, sample_fps)
        return [all_sample_ids.get(fn) for fn in sample_fns]

    def get_analyses(self, sample_fn):
        """Get analyses associated with a sample."""
        return list(self._get_analyses(sample_fn))

    def _get_analyses(self, sample_fn):
        analyses = self._api("analyses")
        for a in analyses:
            if a["sample_filename"] == sample_fn:
                yield a

    @staticmethod
    def analyses_are_finished(analyses):
        def is_finished(analysis):
            return analysis["analysis_status"] != "Pending"
        finished = map(is_finished, analyses)
        return all(finished)

    def retrieve_analyses(self, sample_fn, output_dir, summary_fp, analyses=None):
        """Download all analysis results, return summary."""
        if analyses is None:
            analyses = self.get_analyses(sample_fn)
        if not self.analyses_are_finished(analyses):
            raise ValueError("Not finished: {}".format(analyses))
        analysis_summaries = []
        for a in analyses:
            summary = self.get_analysis_summary(a["id"])
            summary[u'table_fp'] = self.download_table(a, output_dir)
            summary[u'raw_fp'] = self.download_raw_output(a, output_dir)
            analysis_summaries.append(summary)
        with open(summary_fp, "w") as f:
            json.dump(analysis_summaries, f)
        return analysis_summaries

    def get_analysis_summary(self, analysis_id):
        """Get analysis summary."""
        return self._api("analyses", analysis_id)

    def download_table(self, analysis, output_dir):
        """Download table output, return filepath."""
        if analysis["analysis_status"] != "Success":
            return None
        analysis_id = analysis["id"]
        analysis_json = self._api("analyses", analysis_id, "table")
        table_fp = os.path.join(
            output_dir, self._analysis_table_filename(analysis))
        with open(table_fp, "w") as f:
            json.dump(analysis_json, f)
        return table_fp

    def download_raw_output(self, analysis, output_dir):
        """Download raw outout, return filepath."""
        if analysis["analysis_status"] != "Success":
            return None
        analysis_id = analysis["id"]
        raw_fp = os.path.join(
            output_dir, self._analysis_raw_output_filename(analysis))
        self._cli(["analyses", analysis_id, "--raw", raw_fp])
        return raw_fp

    def _api(self, *parts):
        url = "https://app.onecodex.com/api/v0/" + "/".join(parts)
        r = requests.get(url, auth=(self.api_key, ""))
        return r.json()

    def _cli(self, args):
        args = args + ["--api-key", self.api_key]
        onecodex.cli.main(args)

    @staticmethod
    def _get_sample_id(filename, data):
        for rec in data:
            if rec["filename"] == filename:
                return rec["id"]
        return None

    @staticmethod
    def _analysis_output_base(analysis):
        sample_filename = analysis["sample_filename"]
        sample_base, ext = os.path.splitext(sample_filename)
        if ext == ".gz":
            sample_base, _ = os.path.splitext(sample_base)
        reference_id = analysis["reference_id"]
        return "_".join([sample_base, "ref", reference_id])

    @classmethod
    def _analysis_table_filename(cls, analysis):
        return cls._analysis_output_base(analysis) + ".json"

    @classmethod
    def _analysis_raw_output_filename(cls, analysis):
        return cls._analysis_output_base(analysis) + ".tsv.gz"
