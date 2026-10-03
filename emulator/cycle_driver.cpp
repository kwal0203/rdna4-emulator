#include <array>
#include <cstdint>
#include <iostream>
#include <vector>

using Cycle = std::uint64_t;

enum class Opcode { Add };

class SimulationClock {
  public:
    Cycle now() const { return cycle_; }
    void advance() { ++cycle_; }

  private:
    Cycle cycle_ = 1;
};

struct PendingResult {
    int destination;
    std::uint32_t value;
    Cycle available_at;
};

struct Instruction {
    Opcode opcode;
    int source0;
    int source1;
    int destination;
    Cycle latency;
};

class Core {
  public:
    void complete(Cycle now) {
        auto it = pending_.begin();
        while (it != pending_.end()) {
            if (it->available_at <= now) {
                // Publish the value only when its simulated latency has elapsed.
                registers_[it->destination] = it->value;
                ready_[it->destination] = true;

                std::cout << "cycle " << now << ": r" << it->destination << " = " << it->value
                          << " becomes ready.\n";

                it = pending_.erase(it);
            } else {
                ++it;
            }
        }
    }

    void issue(Cycle now) {
        if (next_instruction_ == instructions_.size())
            return;

        const auto &next = instructions_[next_instruction_];
        // Both inputs must be ready. Also wait for any earlier writer to
        // the destination, so this simple model has only one pending writer
        // per register.
        if (!ready_[next.source0] || !ready_[next.source1] || !ready_[next.destination]) {
            std::cout << "cycle " << now << ": instruction " << next_instruction_
                      << " waits for registers.\n";
            return;
        }

        // Capture operands at issue. Computing on the host is immediate;
        // making the result visible in the simulated machine happens later.
        const auto source0 = registers_[next.source0];
        const auto source1 = registers_[next.source1];
        std::uint32_t result = 0;
        switch (next.opcode) {
        case Opcode::Add:
            result = source0 + source1;
            break;
        }

        ready_[next.destination] = false;

        pending_.push_back({next.destination, result, now + next.latency});

        std::cout << "cycle " << now << ": issue instruction " << next_instruction_
                  << ": r" << next.destination << " = r" << next.source0 << " + r" << next.source1
                  << " (" << source0 << " + " << source1 << "), result available at cycle "
                  << now + next.latency << "\n";

        ++next_instruction_;
    }

    bool done() const { return next_instruction_ == instructions_.size() && pending_.empty(); }

    void print_registers() const {
        for (std::size_t i = 0; i < registers_.size(); ++i)
            std::cout << "r" << i << " = " << registers_[i] << '\n';
    }

  private:
    std::array<bool, 4> ready_ = {true, true, true, true};
    std::array<std::uint32_t, 4> registers_ = {10, 20, 0, 0};
    std::vector<PendingResult> pending_;
    std::size_t next_instruction_ = 0;
    const std::array<Instruction, 2> instructions_ = {{
        {Opcode::Add, 0, 1, 2, 5}, // r2 = r0 + r1
        {Opcode::Add, 2, 1, 3, 5}  // r3 = r2 + r1
    }};
};

int main() {
    SimulationClock clock;
    Core core;

    while (!core.done()) {
        // Completions precede issue: a result arriving at cycle 6 can be
        // consumed by an instruction issuing at cycle 6.
        core.complete(clock.now());
        core.issue(clock.now());
        clock.advance();
    }

    std::cout << "Final registers:\n";
    core.print_registers();
}
