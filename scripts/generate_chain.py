from .validator import load_vop2_instructions
from pathlib import Path

import subprocess
import argparse
import shutil


REPO_ROOT = Path(__file__).resolve().parents[1]


parser = argparse.ArgumentParser()
parser.add_argument("--encoding", required=True, help="VOP2, VOP3 etc")
parser.add_argument("--benchmark-type", required=True, help="Latency, throughput etc")
parser.add_argument("--hipcc", default="hipcc", help="HIP compiler executable or path (default: hipcc on PATH)")
args = parser.parse_args()

hipcc = shutil.which(args.hipcc)
if hipcc is None:
    parser.error("HIP compiler not found. Add hipcc to PATH or provide --hipcc /path/to/hipcc.")
hipcc = str(Path(hipcc).resolve())

instructions = load_vop2_instructions(str(REPO_ROOT / "metadata" / "isa" / "vop2.yaml"))
for instruction_name, instruction in instructions.root.items():
    for experiment in instruction.latency_paths:
        print(f"Instruction:      {instruction_name}, experiment: {experiment}")

        for count in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]:
            instructions_text = "\n".join(
                f'        "{experiment.instruction_format}\\n\\t"'
                for _ in range(count)
            )

            source = experiment.template_str.format(
                instruction_name=instruction_name,
                instructions=instructions_text)

            out = (
                REPO_ROOT / "generated"
                / args.encoding
                / args.benchmark_type
                / experiment.name
                / instruction_name
                / f"n{count}.hip"
            )
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(source)

            exe = str(out.with_suffix(""))
            print(f"    Compiling {exe.split('/')[-1]}")
            subprocess.run(
                [hipcc, str(out), "-o", exe],
                check=True
            )
