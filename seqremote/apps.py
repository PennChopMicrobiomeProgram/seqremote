import json
import os
import time

import onecodex.cli
import requests


class OneCodexApp(object):
    def __init__(self):
        self.api_key = os.getenv("ONE_CODEX_API_KEY")
        if self.api_key is None:
            raise RuntimeError(
                "Could not load API key from environment variable "
                "ONE_CODEX_API_KEY.\n")

    def assign_sample(self, sample_fp, output_dir, summary_fp, wait=120, timeout=86400):
        """Assign a single sample file, start to finish."""
        sample_id = self.upload_sample(sample_fp)
        sample_fn = os.path.basename(sample_fp)
        starting_time = time.clock()
        time.sleep(wait)        
        while True:
            analyses = self._get_analyses([sample_fn])
            if self._analyses_are_finished(analyses):
                break
            total_time = time.clock() - starting_time
            if (total_time > timeout):
                raise RuntimeError("Timed out. {}".format(analyses))
            time.sleep(wait)
        summaries = self._download_analysis_files(
            analyses, output_dir, skip_raw=False)
        return summaries

    def upload_sample(self, sample_fp, wait=10):
        """Upload a sample file and return uuid."""
        self._cli(["upload", sample_fp])
        time.sleep(wait)
        samples_json = self._api("samples")
        sample_fn = os.path.basename(sample_fp)
        sample_id = self._get_sample_id(sample_fn, samples_json)
        return sample_id

    def get_sample_ids(self, sample_fps):
        samples_json = self._api("samples")
        all_sample_ids = dict(
            (r["filename"], r["id"]) for r in samples_json)
        sample_fns = map(os.path.basename, sample_fps)
        return [all_sample_ids.get(fn) for fn in sample_fns]

    def _get_analyses(self, sample_fns):
        """Get analyses associated with a set of samples."""
        analyses = self._api("analyses")
        return [
            a for a in analyses if a["sample_filename"] in sample_fns]

    @staticmethod
    def _analyses_are_finished(analyses):
        def is_finished(analysis):
            return analysis["analysis_status"] != "Pending"
        finished = map(is_finished, analyses)
        return all(finished)

    def download_analyses(sample_fns, output_dir, skip_raw):
        analyses = self._get_analyses(sample_fns)
        self._retrieve_analysis_files(analyses, output_dir, skip_raw)

    def _download_analysis_files(self, analyses, output_dir, skip_raw):
        """Download all analysis results, return summary."""
        if not self._analyses_are_finished(analyses):
            raise RuntimeError("Not finished: {}".format(analyses))
        for a in analyses:
            self._download_analysis_summary(a, output_dir)
            self._download_analysis_table(a, output_dir)
            if not skip_raw:
                self._download_analysis_raw_output(a, output_dir)

    def _download_analysis_summary(self, analysis, output_dir):
        """Get analysis summary."""
        analysis_id = analysis["id"]
        summary = self._api("analyses", analysis_id)
        fp = self._analysis_summary_filename(analysis)
        if output_dir is not None:
            fp = os.path.join(output_dir, fp)
        with open(fp, "w") as f:
            json.dump(summary, f)
        return fp

    def _download_analysis_table(self, analysis, output_dir):
        """Download table output, return filepath."""
        if analysis["analysis_status"] != "Success":
            return None
        analysis_id = analysis["id"]
        analysis_json = self._api("analyses", analysis_id, "table")
        fp = self._analysis_table_filename(analysis)
        if output_dir is not None:
            fp = os.path.join(output_dir, fp)
        with open(fp, "w") as f:
            json.dump(analysis_json, f)
        return fp

    def _download_analysis_raw_output(self, analysis, output_dir):
        """Download raw outout, return filepath."""
        if analysis["analysis_status"] != "Success":
            return None
        analysis_id = analysis["id"]
        fp = self._analysis_raw_output_filename(analysis)
        if output_dir is not None:
            fp = os.path.join(output_dir, fp)
        self._cli(["analyses", analysis_id, "--raw", fp])
        return fp

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
    def _analysis_summary_filename(cls, analysis):
        return cls._analysis_output_base(analysis) + "_summary.json"

    @classmethod
    def _analysis_table_filename(cls, analysis):
        return cls._analysis_output_base(analysis) + ".json"

    @classmethod
    def _analysis_raw_output_filename(cls, analysis):
        return cls._analysis_output_base(analysis) + ".tsv.gz"
