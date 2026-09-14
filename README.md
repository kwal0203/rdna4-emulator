# RDNA4 Emulator

A cycle-accurate AMD RDNA4 GPU emulator in development, grounded in measurements from real hardware.

The goal is to model instruction execution, dependencies, wave scheduling, and memory behavior closely enough to predict kernel performance. Hardware microbenchmarks provide the measurements used to calibrate the model, with validation against independent workloads.

## Current status

The repository is currently focused on **microarchitecture characterization**, the foundation for the emulator. It contains a VOP2 instruction metadata catalog, HIP/AMDGPU assembly benchmark templates, and scripts to generate dependency chains, collect cycle counts, and estimate instruction latency. A runnable cycle-level simulator and end-to-end accuracy validation are planned.

The current workflow supports:

- Validating instruction metadata, operand dependency paths, and template references with Pydantic.
- Generating and compiling a benchmark for each configured instruction dependency path at chain lengths of 1, 2, 4, …, 1024 instructions.
- Running each generated executable 10 times and recording raw, minimum, median, and maximum cycle counts.
- Fitting an integer latency model and reporting fit ranges, residuals, local slopes, and a heuristic confidence level.

## Getting started

### Requirements

- Linux with an RDNA4 GPU and a working HIP/ROCm environment for compiling and running benchmarks.
- Python 3.12 or newer.
- `uv` for installing the Python dependencies from the lockfile.

Run the following commands from the repository root:

```bash
uv sync --locked
```

Before generating benchmarks, adjust the paths currently embedded in the scripts to match your checkout and ROCm installation:

| File | Setting | Current value |
| --- | --- | --- |
| `scripts/generate_chain.py` | Metadata path passed to `load_vop2_instructions` | `/home/kane/Projects/rdna4-emulator/metadata/isa/vop2.yaml` |
| `scripts/generate_chain.py` | `hipcc` | `/opt/rocm/core-10.0/bin/hipcc` |
| `scripts/run_experiments.py` | `ROOT` | `/home/kane/Projects/rdna4-emulator/generated` |

### Generate and compile benchmarks

```bash
uv run python -m scripts.generate_chain --encoding vop2 --benchmark-type latency
```

This reads `metadata/isa/vop2.yaml` and compiles each configured latency path at every chain length. Generated HIP sources and executables are written under:

```text
generated/vop2/latency/<dependency_path>/<instruction>/n<count>.hip
generated/vop2/latency/<dependency_path>/<instruction>/n<count>
```

For example, `vdst_to_src0/v_add_f32/n64` benchmarks a chain of 64 additions in which each result feeds the next instruction's `src0` operand.

The command-line arguments currently label output directories; the generator always loads the VOP2 catalog and generates latency chains. Other encodings and throughput experiments are not implemented by these flags.

### Collect and analyze measurements

```bash
uv run python -m scripts.run_experiments
uv run python -m scripts.analyze_experiments
```

The runner discovers generated executables and writes measurements to `results.jsonl`. The analyzer groups those measurements by encoding, benchmark type, dependency path, and instruction, then writes estimates to `latency_results.jsonl` and prints a report.

Both output files are overwritten on each respective run. Generated benchmarks and JSONL results are ignored by Git; save copies of measurements you want to retain.

## Measurement approach

The HIP templates place a dependent instruction chain between GPU counter reads. Varying the chain length helps separate fixed measurement overhead from the cost of each additional instruction:

```text
measured cycles = overhead + latency × chain length
```

Analysis uses the minimum cycle count from each set of repeated runs. It searches integer latencies from 1 to 256 cycles and accepts the longest prefix of chain lengths with at least five points and a maximum absolute residual of three cycles. Larger chain lengths can be excluded when they no longer fit. An ordinary least-squares slope and adjacent-length slopes provide additional diagnostics.

These estimates describe the tested dependency path under the benchmark conditions. The reported confidence is a fit heuristic, not independent confirmation of hardware behavior or emulator accuracy. Disassembly inspection, SQTT trace analysis, and independent throughput tests are part of the planned validation workflow.

## Repository layout

| Path | Purpose |
| --- | --- |
| `metadata/isa/vop2.yaml` | Instruction descriptions, operands, opcodes, and latency paths |
| `scripts/validator.py` | Metadata schema validation and template lookup |
| `scripts/templates/` | HIP source templates with inline AMDGPU assembly |
| `scripts/generate_chain.py` | Dependency-chain source generation and compilation |
| `scripts/run_experiments.py` | Repeated execution and raw measurement collection |
| `scripts/analyze_experiments.py` | Latency estimation and fit diagnostics |
| `kernels/latency/valu/` | Initial experiment specification; not consumed by the current generator |
| `harness/main.cpp` | Placeholder for a standalone harness |
| `summary.md` | Research direction and longer-term modeling plans |

## Roadmap

- Expand characterization to instruction throughput, scheduling, execution resources, and occupancy.
- Measure LDS, caches, global memory latency and bandwidth, and cross-wave behavior.
- Archive exact assembly, disassembly, raw measurements, and SQTT traces for reproducible experiments.
- Build the cycle-level execution and memory model using measured parameters.
- Quantify prediction error against held-out microbenchmarks and real kernels.
- Explore integration of the validated model into Georgia Tech MacSim.
