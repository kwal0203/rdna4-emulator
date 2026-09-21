#ifndef RDNA4_CLOCK_DOMAIN_HH
#define RDNA4_CLOCK_DOMIAN_HH

#include <cstdint>

namespace rdna4 {

/**
 * The ClockDomain provides clock to a group of clocked objects bundled under
 * the same clock domain. The clock domains provide support for a hierarchical
 * structure with source and derived domains.
 */

using Tick = uint64_t;

class ClockDomain {
  public:
    ClockDomain(uint64_t period) : period_(period) {}

    uint64_t period() const { return period_; }

    uint64_t cycles(uint64_t n) const { return n * period_; }

    Tick cyclesToTicks(uint64_t cycles) const { return cycles * period(); }

  private:
    Tick period_;
};

} // namespace rdna4

#endif RDNA4_CLOCK_DOMAIN_HH