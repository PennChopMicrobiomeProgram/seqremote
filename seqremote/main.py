#!/usr/bin/env python
import argparse
import json

from seqremote.apps import OneCodexApp


def retrieve_analyses(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("input_file")
    p.add_argument("output_dir")
    p.add_argument("summary_fp")
    args = p.parse_args(argv)

    app = OneCodexApp()
    summary_data = app.retrieve_analyses(
        args.input_file, args.output_dir, args.summary_fp,
    )


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
        args.input_file, args.output_dir, args.summary_fp
        args.sleep, args.timeout)

if __name__ == "__main__":
    main()
