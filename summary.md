The RDNA4 project will evolve from an exploratory tinygrad-based emulator into a more formal GPU characterization and performance-modeling effort. Tinygrad has been useful for quickly generating kernels, manipulating instructions, and testing ideas, but the next stage is to “graduate” it from being the primary experimental platform. The canonical benchmarking environment will use HIP/ROCm, controlled AMDGPU assembly or code objects, SQTT traces, automated experiment harnesses, and archived disassembly so that every architectural claim can be reproduced and traced back to an exact experiment.

The larger goal is to build an experimentally calibrated RDNA4 execution and performance model. Microbenchmarks will characterize instruction latency and throughput, dependency behavior, scheduling, execution resources, caches, memory latency and bandwidth. These measurements will become explicit parameters in the emulator rather than ad-hoc assumptions. The model will then be tested against held-out microbenchmarks and real kernels, with prediction error reported quantitatively. Eventually the project should resemble the performance models used in industry architecture and pre-silicon simulation teams rather than simply an ISA emulator.

The work can produce three major public artifacts:

1. **RDNA4 Microarchitecture Characterization Suite** — a reproducible collection of dependent/independent instruction tests, pointer chasing, memory experiments, SQTT analysis, raw measurements, methodology, and an RDNA4 latency/throughput/resource database.

2. **Validated RDNA4 Cycle-Level Performance Model** — the expanded emulator, modeling execution pipelines, dependencies, scheduling, memory behavior and other architectural resources, calibrated against real RDNA4 silicon and evaluated using independent validation workloads.

3. **RDNA4 Support for Georgia Tech MacSim + Research Paper** — transfer the experimentally derived model into an established cycle-level architectural simulator, validate MacSim's predictions against real hardware, and package the methodology and results as a publishable architecture research project.

Together these form a coherent progression: **measure the real GPU → infer its microarchitecture → build and validate a predictive model → integrate that model into a research-grade simulator.**

A good top-level decomposition is:

Execution pipelines
Instruction latency
Instruction throughput / issue rate
Dependency behavior
Wave scheduling
LDS/shared memory
Cache hierarchy
Global memory latency/bandwidth
Control flow / branches
Special-function units
Resource limits / occupancy
Cross-wave / cross-CU effects

For latency:

For example, suppose the hardware can forward the result after 5 cycles even though the instruction formally “completes” later. Your dependency chain measures the 5-cycle forwarding latency, which is exactly the useful number for a performance simulator.

Some instructions also need special treatment. Loads, atomics, branches, matrix operations, and variable-latency instructions may not have one fixed latency at all. A global load might be 20 cycles on one cache hit and hundreds on a DRAM access. For those, you characterize a distribution or a latency by memory level rather than putting one number in the table.

For each instruction:

1. Generate dependent chains of N = 32,64,128,256,512
2. Run many repetitions
3. Record total cycles
4. Fit linear regression:
      cycles = intercept + latency * N
5. Inspect SQTT issue spacing
6. Run independent-chain benchmark
7. Save ISA + trace + raw measurements

v_add_f32

dependent-chain slope:       5.01 cycles/op
SQTT producer spacing:       5 cycles
independent issue interval:  1 cycle
R² of chain-length fit:      0.9998

Inferred dependency latency: 5 cycles
Confidence: high
