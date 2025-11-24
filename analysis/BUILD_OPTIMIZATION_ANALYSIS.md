# RubiChess Build & Code Optimization Analysis

**Date:** November 24, 2025  
**Purpose:** Identify potential performance improvements in build configuration and source code

---

## Current Build Configuration Analysis

### Visual Studio (Release|x64) Settings

```xml
<Optimization>MaxSpeed</Optimization>           ✅ Good
<FunctionLevelLinking>true</FunctionLevelLinking>  ✅ Good
<IntrinsicFunctions>true</IntrinsicFunctions>   ✅ Good
<FavorSizeOrSpeed>Speed</FavorSizeOrSpeed>      ✅ Good
<WholeProgramOptimization>true</WholeProgramOptimization>  ✅ Good (LTO)
```

### Makefile (GCC/Clang) Settings

```makefile
CXXFLAGS += -O3 -flto                           ✅ Good
```

---

## Potential Build Optimizations

### 1. **Profile-Guided Optimization (PGO)** ⭐ HIGH IMPACT

**Current Status:** Supported but not used by default

**What it does:** Compiles the engine, runs it on typical positions, then recompiles using the profile data to optimize hot paths.

**Potential Improvement:** 5-15% speed increase

**How to enable:**
```bash
# Makefile already supports this:
make profile-build ARCH=x86-64-avx2
```

**For Visual Studio:**
- Add `/GL` (Whole Program Optimization) - Already enabled
- Add `/LTCG` (Link Time Code Generation) - Already enabled via WholeProgramOptimization
- Consider adding PGO instrumentation

---

### 2. **AVX-512 Support** ⭐ MEDIUM IMPACT

**Current Status:** Supported in Makefile, but may not be enabled in VS project

**What it does:** Uses wider SIMD registers (512-bit vs 256-bit AVX2)

**Potential Improvement:** 10-20% for NNUE evaluation on supported CPUs

**Current preprocessor defines (Release|x64):**
```
USE_SSE2;USE_SSSE3;USE_POPCNT;USE_BMI1;USE_AVX2
```

**Missing:** `USE_AVX512` (if your CPU supports it)

**Check your CPU:**
```cmd
wmic cpu get name
```

---

### 3. **BMI2 (PEXT/PDEP) Instructions** ⭐ MEDIUM IMPACT

**Current Status:** Not explicitly enabled in VS project

**What it does:** Uses hardware bit manipulation for faster move generation

**Potential Improvement:** 5-10% for move generation

**To enable:** Add `USE_BMI2` to preprocessor definitions

---

### 4. **Link-Time Optimization (LTO)** ✅ Already Enabled

**Current Status:** Enabled via `WholeProgramOptimization` and `-flto`

---

### 5. **Compiler-Specific Optimizations**

#### For MSVC (Visual Studio):
```xml
<!-- Add to Release configuration -->
<AdditionalOptions>/arch:AVX2 /fp:fast %(AdditionalOptions)</AdditionalOptions>
```

#### For Clang/GCC:
```makefile
CXXFLAGS += -march=native -mtune=native -ffast-math
```

---

## Code-Level Optimization Opportunities

### 1. **Hot Path Analysis**

The most performance-critical code paths in a chess engine are:
1. **Move generation** (`move.cpp`)
2. **NNUE evaluation** (`nnue.cpp`)
3. **Search** (`search.cpp`)
4. **Transposition table** (`transposition.cpp`)

### 2. **NNUE Evaluation Optimizations**

**Current SIMD usage:** Good - uses AVX2/SSE2/NEON

```cpp
#define USE_SIMD
#if defined(USE_SSE2)
#include <immintrin.h>
```

**Potential improvements:**
- Ensure accumulator updates are cache-friendly
- Consider prefetching for large networks

### 3. **Memory Alignment**

**Current:** Uses `allocalign64` for NNUE structures ✅ Good

### 4. **Branch Prediction Hints**

**Potential:** Add `[[likely]]` and `[[unlikely]]` attributes (C++20) to hot paths

```cpp
// Example in search.cpp
if (score > alpha) [[likely]] {
    // ...
}
```

### 5. **Inline Functions**

**Current:** 85 inline functions found - appears well-optimized

---

## Recommended Actions

### Priority 1: Enable PGO Build (Highest Impact)

```bash
# For Clang/GCC:
cd RubiChess/src
make profile-build ARCH=x86-64-avx2
```

**Expected improvement:** 5-15% NPS increase

### Priority 2: Check AVX-512 Support

If your CPU supports AVX-512:
```bash
make profile-build ARCH=x86-64-avx512
```

### Priority 3: Enable BMI2 in Visual Studio

Add `USE_BMI2` to preprocessor definitions if your CPU supports it.

### Priority 4: Fast Math

Add `/fp:fast` (MSVC) or `-ffast-math` (GCC/Clang) for faster floating-point operations.

---

## Benchmark Before/After

To measure improvement, use:
```
go depth 20
```

Record:
- **NPS** (nodes per second)
- **Time to depth 20**

---

## Summary

| Optimization | Status | Potential Gain | Effort |
|--------------|--------|----------------|--------|
| PGO Build | Available | 5-15% | Low |
| AVX-512 | Available | 10-20% | Low |
| BMI2 | Partial | 5-10% | Low |
| LTO | ✅ Enabled | - | - |
| SIMD | ✅ Enabled | - | - |
| Alignment | ✅ Good | - | - |

**Total potential improvement: 15-40% NPS increase** (depending on CPU features)
