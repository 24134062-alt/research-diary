# Category VII: Memory & Compute Optimization

> **Tổng quan**: Memory và compute optimization tập trung vào giải quyết "memory wall" - bottleneck giữa compute speed và memory bandwidth trong AI workloads.

---

## 66. Compute-in-Memory (CIM) for Neural Networks

### Mô tả
Thực hiện computation trực tiếp trong memory arrays, tránh data movement tốn kém.

### The Memory Wall
```
Problem:
Compute speed improving faster than memory bandwidth
→ Memory becomes bottleneck

Traditional:
Memory ──load──> Compute ──store──> Memory
        ↑____________↓
        Lots of data movement!

CIM:
Memory + Compute integrated
        ↑
        No data movement!
```

### CIM Approaches
| Technology | Principle | Precision |
|------------|-----------|-----------|
| **SRAM CIM** | Analog/digital in SRAM | 4-8 bit |
| **ReRAM CIM** | Resistance-based | 1-4 bit |
| **Flash CIM** | Charge-based | 4-8 bit |
| **DRAM CIM** | In-DRAM processing | Digital |

### Matrix-Vector Multiplication in ReRAM
```
V₁ ──┐   ┌─ R₁₁ ─ R₁₂ ─ R₁₃ ─┐
V₂ ──┤   │  R₂₁ ─ R₂₂ ─ R₂₃ ─┤
V₃ ──┘   └─ R₃₁ ─ R₃₂ ─ R₃₃ ─┘
                   │
                   ▼
         I = V × R (Ohm's law!)
         
Weights encoded as resistance values
Input as voltage
Output as current (sum)
```

### Challenges
- Analog noise
- Limited precision
- Write endurance
- Programming overhead

### Đọc thêm
- ISAAC (2016)
- PRIME (2016)
- Compute-in-Memory Survey (2020)

---

## 67. Processing-in-Memory Architectures

### Mô tả
Đặt processing elements gần hoặc trong memory để reduce data movement.

### PIM Levels
```
Near-memory computing:
Memory ← Short distance → Processing

In-memory computing:
Memory + Processing = Same unit
```

### HBM-PIM
```
Traditional HBM:           HBM-PIM:
┌─────────────┐           ┌─────────────┐
│   DRAM      │           │ DRAM + PIM  │
│   Dies      │           │   Logic     │
├─────────────┤           ├─────────────┤
│   Logic     │           │   Logic     │
└─────────────┘           └─────────────┘
    │                         │
    ▼                         ▼
Limited IO bandwidth     Compute at memory
```

### Samsung HBM-PIM
- Processing near HBM memory stacks
- 2.9x faster than GPU for specific workloads
- 62% less energy

### Đọc thêm
- Samsung HBM-PIM (2021)
- UPMEM PIM-DRAM
- Processing-in-Memory Survey (2022)

---

## 68. Memory-efficient Training Algorithms

### Mô tả
Algorithms giảm memory footprint trong training, cho phép train larger models.

### Memory during Training
```
Memory = Weights + Gradients + Optimizer states + Activations

For AdamW:
Weights:     N params (FP16: 2N bytes)
Gradients:   N params (FP16: 2N bytes)  
Optimizer:   2N params (FP32: 8N bytes) - momentum + variance
Activations: O(batch × layers × hidden)

Total ≈ 12-16 bytes per parameter + activations
```

### Techniques
| Technique | Memory Reduction | Tradeoff |
|-----------|-----------------|----------|
| Mixed precision | 2x | Minimal |
| Gradient checkpointing | 3-5x | 1.3x compute |
| ZeRO Stage 1-3 | 4-8x | Communication |
| LoRA | 10-100x | Fine-tuning only |

### Gradient Checkpointing
```
Forward: Compute all, save only checkpoints
Backward: Recompute from checkpoints

Trade: Compute ↑ 33%, Memory ↓ √n
```

### Đọc thêm
- ZeRO (Microsoft, 2020)
- Gradient Checkpointing (2016)
- FSDP (PyTorch)

---

## 69. Activation Checkpointing Strategies

### Mô tả
Chiến lược lưu và tái tính toán activations để giảm memory.

### Problem
```
Deep networks: Save all activations for backward pass
Memory ∝ depth × batch × hidden size

GPT-3 (175B): Activations can exceed 1TB!
```

### Checkpointing Strategies
| Strategy | Memory | Recompute |
|----------|--------|-----------|
| **None** | O(n) | 0 |
| **Full** | O(1) | O(n²) |
| **Selective** | O(√n) | O(n) |
| **Adaptive** | Budget-based | Varies |

### Implementation
```python
# Without checkpointing
def forward(x):
    x1 = layer1(x)    # Save
    x2 = layer2(x1)   # Save  
    x3 = layer3(x2)   # Save
    return x3

# With checkpointing
@torch.utils.checkpoint
def forward(x):
    x1 = layer1(x)    # Not saved
    x2 = layer2(x1)   # Not saved (recompute in backward)
    x3 = layer3(x2)
    return x3
```

### Đọc thêm
- Sublinear Memory Cost (2016)
- Activation Compression (2021)

---

## 70. Memory Bandwidth Optimization

### Mô tả
Tối ưu sử dụng memory bandwidth - often the true bottleneck.

### Bandwidth vs Compute
```
Arithmetic Intensity = FLOPs / Bytes moved

If low arithmetic intensity → Memory-bound
If high arithmetic intensity → Compute-bound

Goal: Increase arithmetic intensity via reuse
```

### Optimization Techniques
1. **Data layout optimization**: Align with memory access patterns
2. **Tiling**: Process data in cache-friendly blocks
3. **Prefetching**: Load data before needed
4. **Compression**: Reduce bytes transferred

### Memory Access Patterns
```
Good (Coalesced):         Bad (Strided):
Thread 0 → addr 0         Thread 0 → addr 0
Thread 1 → addr 1         Thread 1 → addr 128
Thread 2 → addr 2         Thread 2 → addr 256
...                       ...
One memory transaction    Many memory transactions
```

### Đọc thêm
- Roofline Model (2009)
- Memory Optimization Survey (2021)

---

## 71. Cache-aware Neural Network Design

### Mô tả
Thiết kế networks để maximize cache hit rate.

### Cache Hierarchy Impact
```
Access latency:
L1 cache:  ~4 cycles
L2 cache:  ~12 cycles
L3 cache:  ~40 cycles
DRAM:      ~200 cycles

50x difference between L1 and DRAM!
```

### Cache-friendly Design
| Design Choice | Cache Impact |
|---------------|--------------|
| Smaller layers | Fit in cache |
| Depthwise conv | Higher reuse |
| Channel-last layout | Better locality |
| Power-of-2 dims | Avoid conflicts |

### Tiling for Cache
```python
# Naive: Poor cache usage
for i in range(H):
    for j in range(W):
        compute(A[i,j], B[i,j])

# Tiled: Better cache usage
for ti in range(0, H, TILE):
    for tj in range(0, W, TILE):
        for i in range(ti, min(ti+TILE, H)):
            for j in range(tj, min(tj+TILE, W)):
                compute(A[i,j], B[i,j])
```

---

## 72. DRAM/SRAM Trade-offs for Edge AI

### Mô tả
Cân bằng giữa SRAM (fast, expensive, limited) và DRAM (slow, cheap, larger).

### Comparison
| Aspect | SRAM | DRAM |
|--------|------|------|
| Speed | Fast (~1ns) | Slow (~50ns) |
| Energy | Low (10fJ/bit) | High (100fJ/bit) |
| Density | Low | High |
| Cost | High | Low |
| Refresh | Not needed | Needed |

### Strategy for Edge
```
Model weights: Store in Flash/DRAM (accessed less)
Activations: Buffer in SRAM (accessed frequently)
Hot weights: Cache in SRAM

Small models: All in SRAM
Large models: Layer-wise loading from DRAM
```

### Memory Planning
```python
def memory_plan(model, sram_size, dram_size):
    for layer in model.layers:
        if layer.activation_size < sram_size:
            # Keep activations in SRAM
            layer.activation_memory = SRAM
        else:
            # Tile and stream from DRAM
            layer.activation_memory = DRAM
```

---

## 73. Non-volatile Memory for Neural Network Storage

### Mô tả
Sử dụng NVM (Flash, ReRAM, PCM) để store models với low power retention.

### NVM Technologies
| Type | Write | Read | Endurance | Use Case |
|------|-------|------|-----------|----------|
| **Flash** | Slow | Fast | 10⁵ | Model storage |
| **ReRAM** | Fast | Fast | 10⁶-10⁹ | CIM |
| **PCM** | Medium | Fast | 10⁸ | General |
| **MRAM** | Fast | Fast | 10¹⁵ | Cache |

### Benefits for Edge AI
- No power needed to retain model
- Instant-on capability
- Reduce DRAM power

### Challenges
- Write endurance
- Write energy
- Reliability

---

## 74. ReRAM-based Neural Network Accelerators

### Mô tả
Sử dụng Resistive RAM để implement neural network weights và compute.

### ReRAM Basics
```
Resistive RAM cell:
High Resistance State (HRS) = "0"
Low Resistance State (LRS)  = "1"

Multiple levels possible → store analog weights
```

### ReRAM Crossbar Array
```
       V₁  V₂  V₃  (Input voltages)
        │   │   │
    ────●───●───●──── I₁ (Output current)
        │   │   │
    ────●───●───●──── I₂
        │   │   │
    ────●───●───●──── I₃
        
    ● = ReRAM cell (resistance = weight)
    
    I = V × G (conductance)
    → Parallel MAC operations!
```

### Advantages
- Massively parallel MAC
- In-memory computing
- Low power

### Đọc thêm
- ISAAC (2016)
- PipeLayer (2017)
- PUMA (2019)

---

## 75. Memory Compression for Inference

### Mô tả
Compress data in memory để reduce storage và bandwidth.

### What to Compress
```
Weights: Static, high compression possible
Activations: Dynamic, need fast compression
Gradients: Training only, can be lossy
```

### Compression Techniques
| Technique | Compression | Overhead |
|-----------|-------------|----------|
| **Zero compression** | 2-5x | Very low |
| **Sparse encoding** | 2-10x | Low |
| **Entropy coding** | 1.5-3x | Medium |
| **Delta encoding** | 1.5-2x | Low |

### Zero-value Compression
```
Dense: [0, 0, 3, 0, 0, 2, 0, 1]
Compressed: values=[3, 2, 1], indices=[2, 5, 7]
Or run-length: [2, 3, 2, 2, 1, 1] (count, value pairs)
```

### Đọc thêm
- Deep Compression (2016)
- SparCE (2018)
- Memory-side Compression (2019)

---

## 📚 Memory Optimization Summary

### Key Metrics
```
Memory Efficiency = Useful data / Total data moved
Compute Efficiency = Achieved FLOPs / Peak FLOPs
Energy Efficiency = Operations / Joule
```

### Design Guidelines
1. Minimize data movement
2. Maximize data reuse
3. Match precision to task
4. Exploit sparsity
5. Use appropriate memory hierarchy
