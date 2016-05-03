#!/usr/bin/env python
import argparse
import json
import os
from seqremote.apps import OneCodexApp


def convert_json_to_table(json_records):
    fields = ["readcount", "name", "rank", "tax_id"]
    yield fields
    for rec in json_records:
        yield [str(rec[f]) for f in fields]


def convert_json(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("input_file", type=argparse.FileType("r"))
    p.add_argument("output_file", type=argparse.FileType("w"))
    args = p.parse_args(argv)
    json_input = json.load(args.input_file)
    tabular_output = convert_json_to_table(json_input)
    for line in tabular_output:
        args.output_file.write("\t".join(line))
        args.output_file.write("\n")


def check_upload(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("file_of_filepaths")
    args = p.parse_args(argv)

    app = OneCodexApp()
    fps = []
    with open(args.file_of_filepaths) as f:
        for line in f:
            line = line.strip()
            if line:
                fps.append(line)
    sample_ids = app.get_sample_ids(fps)
    for fp, sample_id in zip(fps, sample_ids):
        print "{}\t{}".format(fp, sample_id)


def upload_file(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("input_file")
    args = p.parse_args(argv)

    app = OneCodexApp()
    summary_data = app.upload_sample(args.input_file)


def retrieve_analyses(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("input_filename", nargs="+")
    p.add_argument("--output_dir")
    p.add_argument("--skip_raw", action="store_true")
    args = p.parse_args(argv)

    fns = set(os.path.basename(fn) for fn in args.input_filename)
    app = OneCodexApp()
    app.download_analyses(args.input_filename, args.output_dir, args.skip_raw)


def assign_file(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("input_file")
    p.add_argument("output_dir")
    p.add_argument("summary_fp")
    p.add_argument("--sleep", default=100, type=int)
    p.add_argument("--timeout", default=86400, type=int)
    args = p.parse_args(argv)
    app = OneCodexApp()
    app.assign_sample(
        args.input_file, args.output_dir, args.summary_fp,
        args.sleep, args.timeout)

if __name__ == "__main__":
    main()
