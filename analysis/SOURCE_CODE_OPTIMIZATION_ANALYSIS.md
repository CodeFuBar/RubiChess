# RubiChess Source Code Optimization Analysis

**Date:** November 24, 2025  
**Purpose:** Identify potential performance improvements in the source code

---

## Executive Summary

After reviewing the RubiChess source code, the engine is **already well-optimized**. The codebase follows modern chess engine best practices with:
- Efficient bitboard operations
- SIMD-optimized NNUE evaluation
- Proper use of inline functions
- Hardware intrinsics for bit manipulation

However, there are some **minor optimization opportunities** that could provide small improvements.

---

## Current Optimizations (Already Implemented)

### 1. Bitboard Operations - EXCELLENT
```cpp
// Uses hardware intrinsics for bit manipulation
#define GETLSB(i,x) (i =(int) _tzcnt_u64(x))
#define POPCOUNT(x) (int)(__popcnt64(x))
inline int pullLsb(U64* x) {
    int i = (int)_tzcnt_u64(*x);
    *x = _blsr_u64(*x);  // Uses BMI1 instruction
    return i;
}
```

### 2. NNUE Evaluation - EXCELLENT
- Uses SIMD (SSE2/AVX2/AVX-512) for neural network inference
- Incremental accumulator updates
- Proper memory alignment (`alignas(64)`)

### 3. Transposition Table - GOOD
- Uses bucket system (TTBUCKETNUM entries per cluster)
- Age-based replacement scheme
- Huge page support on Linux

### 4. Move Generation - GOOD
- Uses magic bitboards for sliding pieces
- Efficient move encoding in 32-bit integers

---

## Potential Optimization Opportunities

### 1. **Prefetching for Transposition Table** - MEDIUM IMPACT

**Current:** No explicit prefetching
**Suggestion:** Add prefetch hints before TT probe

```cpp
// In search.cpp, before TT lookup
inline void prefetchTT(U64 hash) {
    _mm_prefetch((char*)&tp.table[hash & tp.sizemask], _MM_HINT_T0);
}

// Usage: Call prefetchTT() early in alphabeta()
```

**Expected improvement:** 1-3% in positions with high TT hit rate

---

### 2. **Branch Prediction Hints** - LOW IMPACT

**Current:** No explicit branch hints
**Suggestion:** Add `[[likely]]` and `[[unlikely]]` attributes (C++20)

```cpp
// In search.cpp
if (tpHit) [[likely]] {
    // TT hit path - most common
}

if (en.stopLevel == ENGINESTOPIMMEDIATELY) [[unlikely]] {
    return beta;
}
```

**Note:** Requires C++20 or compiler-specific attributes

---

### 3. **Move List Optimization** - LOW IMPACT

**Current:** Linear search for best move
```cpp
chessmove* chessmovelist::getNextMove(int minval) {
    int current = -1;
    for (int i = 0; i < length; i++) {
        if (move[i].value > minval) {
            minval = move[i].value;
            current = i;
        }
    }
    // ...
}
```

**Suggestion:** Consider partial sorting or heap for large move lists

**Note:** Current implementation is fine for typical move list sizes (< 50 moves)

---

### 4. **Evaluation Cache** - MEDIUM IMPACT

**Current:** Pawn hash table exists
**Suggestion:** Consider adding a small evaluation cache for repeated positions

```cpp
// Small cache for recently evaluated positions
struct EvalCache {
    U64 hash;
    int16_t eval;
};
alignas(64) EvalCache evalCache[1024];
```

**Note:** May not help much since NNUE is already fast

---

### 5. **Memory Layout Optimization** - LOW IMPACT

**Current:** Good use of `alignas(64)` for critical structures
**Suggestion:** Ensure hot data is cache-line aligned

```cpp
// In chessposition class, group frequently accessed members
alignas(64) struct {
    U64 piece00[16];
    U64 occupied00[2];
    int state;
    // ... other hot data
} hotData;
```

---

### 6. **Loop Unrolling in NNUE** - ALREADY DONE

The NNUE code already uses SIMD with proper loop structures:
```cpp
#ifdef USE_SIMD
constexpr unsigned int numRegs = ...;
constexpr unsigned int tileHeight = numRegs * SIMD_WIDTH / 16;
ft_vec_t acc[numRegs];
// Vectorized operations
#endif
```

---

### 7. **String Operations in UCI** - NEGLIGIBLE IMPACT

**Current:** Uses `std::string` operations
**Note:** UCI parsing is not performance-critical

---

## Recommendations

### Priority 1: Prefetching (Easy to implement)
Add TT prefetch before probe. This is a simple change with measurable benefit.

### Priority 2: Compiler Flags (Already addressed)
The build_optimal.bat script already handles this with:
- `/O2 /Oi /Ot /GL` (MSVC)
- AVX-512 support when available

### Priority 3: Profile-Guided Optimization (PGO)
The Makefile supports PGO builds which can provide 5-15% improvement:
```bash
make profile-build ARCH=x86-64-avx512
```

---

## Code Quality Observations

### Strengths
1. Clean, well-organized code structure
2. Proper use of namespaces
3. Good separation of concerns
4. Efficient data structures

### Minor Issues (Non-Performance)
1. Some magic numbers could be named constants
2. A few long functions could be split
3. Some comments could be more detailed

---

## Conclusion

RubiChess is a **well-optimized chess engine**. The major performance gains have already been achieved through:
- SIMD-optimized NNUE
- Hardware intrinsics for bit operations
- Efficient data structures

The remaining optimization opportunities are **minor** (1-5% potential improvement):
1. TT prefetching
2. PGO builds
3. Branch hints (C++20)

**Recommendation:** Focus on algorithmic improvements (search, evaluation) rather than micro-optimizations. The build optimization (AVX-512) we already implemented provides more benefit than most source code changes.

---

## Files Reviewed

- `search.cpp` - Main search algorithm
- `move.cpp` - Move generation and handling
- `nnue.cpp` - Neural network evaluation
- `transposition.cpp` - Hash table implementation
- `board.cpp` - Board representation
- `eval.cpp` - Classical evaluation
- `RubiChess.h` - Core definitions and macros
