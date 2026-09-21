#ifndef RDNA4_TYPES_HH
#define RDNA4_TYPES_HH

#include <bit>
#include <cstdint>
#include <ostream>
#include <stdexcept>

namespace rdna4 {

using Counter = std::int64_t;
using Tick = std::uint64_t;

const Tick MaxTick = 0xffffffffffffffffULL;
Counter counter;

class Cycles {
  private:
    std::uint64_t c;

  public:
    explicit constexpr Cycles(std::uint64_t _c) : c(_c) {}
    Cycles() : c(0) {}

    constexpr operator uint64_t() const { return c; }
    constexpr bool operator>(const Cycles &cc) const { return c > cc.c; }
    constexpr Cycles operator+(const Cycles &b) { return Cycles(c + b.c); }
    constexpr Cycles operator<<(const int32_t shift) { return Cycles(c << shift); }
    constexpr Cycles operator>>(const int32_t shift) { return Cycles(c >> shift); }
    Cycles &operator++() {
        ++c;
        return *this;
    }
    Cycles &operator--() {
        --c;
        return *this;
    }
    Cycles &operator+=(const Cycles &cc) {
        c += cc.c;
        return *this;
    }
    constexpr Cycles operator-(const Cycles &b) {
        return c >= b.c ? Cycles(c - b.c)
                        : throw std::invalid_argument("RHS cycle value larger than LHS");
    }
    friend std::ostream &operator<<(std::ostream &out, const Cycles &cycles) {
        out << cycles.c;
        return out;
    }
};

using Addr = uint64_t;
const Addr MaxAddr = (Addr)-1;

using RegVal = uint64_t;
using RegIndex = uint16_t;

static inline uint32_t floatToBits(float val) { return std::bit_cast<uint32_t>(val); }
static inline uint64_t floatToBits(double val) { return std::bit_cast<uint64_t>(val); }
static inline float bitsToFloat(uint32_t bits) { return std::bit_cast<float>(bits); }
static inline float bitsToFloat(uint64_t bits) { return std::bit_cast<double>(bits); }

} // namespace rdna4

#endif