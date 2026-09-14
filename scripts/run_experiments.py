from pathlib import Path

import json
import os
import re
import statistics
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "generated"
OUTPUT_FILE = REPO_ROOT / "results.jsonl"
NUM_RUNS = 10

cycle_re = re.compile(r"Cycles\s*=\s*(\d+)")
program_re = re.compile(r"n(\d+)")


with OUTPUT_FILE.open("w") as f:

    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Make traversal deterministic between directories
        dirnames.sort()

        # Find benchmark programs in this directory
        programs = [
            name
            for name in filenames
            if program_re.fullmatch(name)
        ]

        if not programs:
            continue

        # n1, n2, n4, n8, n16, ...
        programs.sort(key=lambda name: int(name[1:]))

        directory = Path(dirpath)

        print(f"\nProcessing {directory}")

        # Records belonging to this particular experiment/instruction.
        # You can analyze this list after the directory is complete.
        directory_records = []

        for program in programs:
            path = directory / program

            relative = path.relative_to(ROOT)
            parts = relative.parts

            # Expected structure:
            #
            # vop2/
            #   latency/
            #     vdst_to_src0/
            #       v_add_co_ci_u32/
            #         n64
            #
            if len(parts) != 5:
                print(f"Skipping unexpected path: {relative}")
                continue

            encoding, benchmark_type, experiment, instruction, program_name, = parts
            n = int(program_name[1:])
            cycles = []
            for _ in range(NUM_RUNS):
                result = subprocess.run(
                    [str(path)],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                match = cycle_re.search(result.stdout)
                if not match:
                    raise RuntimeError(
                        f"Could not parse output from {path}: "
                        f"{result.stdout!r}"
                    )

                cycles.append(int(match.group(1)))

            record = {
                "encoding": encoding,
                "benchmark_type": benchmark_type,
                "experiment": experiment,
                "instruction": instruction,
                "n": n,
                "min_cycles": min(cycles),
                "median_cycles": statistics.median(cycles),
                "max_cycles": max(cycles),
                "runs": cycles,
            }

            directory_records.append(record)

            f.write(json.dumps(record) + "\n")
            f.flush()

            print(
                f"  n={n:<4} "
                f"min={record['min_cycles']:<6} "
                f"median={record['median_cycles']:<6} "
                f"max={record['max_cycles']:<6}"
            )

        # ------------------------------------------------------------
        # At this point, ALL n values for one experiment/instruction
        # have been collected.
        #
        # This is where we can calculate latency.
        # ------------------------------------------------------------

        if directory_records:
            print(
                f"Completed: "
                f"{directory_records[0]['instruction']} / "
                f"{directory_records[0]['experiment']}"
            )
