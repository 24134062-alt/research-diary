# Category III: Pruning & Sparsity

> **Tổng quan**: Pruning là kỹ thuật loại bỏ các connections hoặc neurons ít quan trọng trong neural network để giảm computation và memory requirements.

---

## 28. Structured Pruning for Hardware Acceleration

### Mô tả
Pruning theo cấu trúc (channels, filters, layers) thay vì individual weights, dễ tận dụng hardware acceleration.

### Unstructured vs Structured
```
Unstructured (Fine-grained):     Structured (Coarse-grained):
┌──────────────┐                 ┌──────────────┐
│ 0 1 0 0 1 0  │                 │ 1 1 1 1 1 1  │
│ 1 0 0 1 0 0  │  →  Sparse      │ 0 0 0 0 0 0  │  →  Remove entire
│ 0 0 1 0 0 1  │     matrix      │ 1 1 1 1 1 1  │     row/column
└──────────────┘                 └──────────────┘
Hard to accelerate               Easy to accelerate
```

### Types of Structured Pruning
| Type | Granularity | Speedup | Accuracy |
|------|-------------|---------|----------|
| Filter pruning | Remove entire filters | High | Lower |
| Channel pruning | Remove channels | High | Medium |
| Layer pruning | Remove layers | Very High | Lowest |
| Block pruning | Remove blocks | Medium | Higher |

### Hardware Benefits
- No sparse tensor operations needed
- Direct model size reduction
- Standard dense operations work

### Đọc thêm
- Filter Pruning (2017)
- Channel Pruning for Accelerating CNNs (2017)

---

## 29. Dynamic Pruning during Inference

### Mô tả
Pruning decisions made dynamically based on input data at runtime.

### Concept
```
Easy Input → Skip more computations → Faster
Hard Input → Use more network → Accurate
```

### Approaches
1. **Early exit**: Exit at intermediate layer if confident
2. **Dynamic channel selection**: Choose channels based on input
3. **Adaptive depth**: Variable number of layers per input

### Early Exit Architecture
```
Input → Block1 → [Exit1?] → Block2 → [Exit2?] → Block3 → Output
            │         │
            └→ Output if confident
```

### Gating Mechanism
```python
def dynamic_forward(x, block, gate):
    importance = gate(x)  # Learn which channels to use
    mask = importance > threshold
    return block(x * mask)
```

### Đọc thêm
- Dynamic Neural Networks Survey (2021)
- SkipNet (2018)
- BlockDrop (2018)

---

## 30. Channel Pruning with Hardware Latency Constraints

### Mô tả
Prune channels để meet target latency constraints trên specific hardware.

### Optimization
```
minimize    Σ importance(channel_i) × pruned_i
subject to  Latency(pruned_model) ≤ Target_Latency
            pruned_i ∈ {0, 1}
```

### Channel Importance Criteria
| Criterion | Description | Cost |
|-----------|-------------|------|
| L1-norm | Sum of absolute weights | Low |
| L2-norm | Sum of squared weights | Low |
| Gradient | Gradient-based importance | Medium |
| Fisher | Fisher information | High |
| Taylor | First-order Taylor expansion | Medium |

### Latency-aware Process
```
1. Profile latency of each channel on target hardware
2. Compute importance scores
3. Greedily prune least important channels
4. Stop when latency budget met
5. Fine-tune
```

### Đọc thêm
- NetAdapt (Google, 2018)
- AMC: AutoML for Model Compression (2018)

---

## 31. N:M Sparsity Patterns for GPU/TPU Optimization

### Mô tả
Sparsity pattern trong đó chỉ N values trong mỗi M consecutive values là non-zero, được NVIDIA Ampere GPUs hỗ trợ natively.

### 2:4 Sparsity Example
```
Original:    [1.2, 0.5, 0.8, 0.3, 0.9, 0.2, 0.7, 0.4]
2:4 Sparse:  [1.2, 0.0, 0.8, 0.0, 0.9, 0.0, 0.7, 0.0]
             Keep 2 largest in each group of 4
```

### Hardware Support
```
NVIDIA Ampere (A100):
- Sparse Tensor Cores
- 2:4 structured sparsity
- ~2x speedup with minimal accuracy loss
```

### Training for N:M Sparsity
1. Train dense network
2. Apply N:M mask
3. Fine-tune with mask fixed
4. Optional: repeat pruning + fine-tuning

### Đọc thêm
- Accelerating Sparse Deep Neural Networks (NVIDIA, 2021)
- SR-STE: N:M Sparsity Training (2021)

---

## 32. Lottery Ticket Hypothesis for Efficient Networks

### Mô tả
Hypothesis: Mọi dense network chứa một sparse subnetwork (winning ticket) có thể train đến same accuracy khi isolated.

### The Hypothesis
```
Dense Network (initialized) 
    │
    ├── Contains "winning ticket"
    │   (sparse subnetwork + initialization)
    │
    └── If found and trained from scratch,
        matches dense network performance
```

### Finding Winning Tickets
```python
# Iterative Magnitude Pruning (IMP)
for iteration in range(num_iterations):
    1. Train network to completion
    2. Prune p% smallest magnitude weights
    3. Reset remaining weights to initial values
    4. Repeat
```

### Key Insights
- Initialization matters (must keep original init)
- Winning tickets are transferable across datasets
- Leads to very sparse networks (1-10% remaining)

### Đọc thêm
- The Lottery Ticket Hypothesis (Frankle & Carlin, 2019)
- Stabilizing the Lottery Ticket (2019)

---

## 33. Hardware-aware Filter Importance Scoring

### Mô tả
Thiết kế importance metrics cho filter pruning có tính đến hardware characteristics.

### Traditional Importance Scores
```python
# L1-norm based
importance = torch.sum(torch.abs(filter_weights))

# Activation-based
importance = torch.mean(activations ** 2)

# Gradient-based
importance = torch.abs(weights * gradients)
```

### Hardware-aware Scoring
```python
importance_hw = (
    accuracy_importance * α +
    (1 / latency_contribution) * β +
    (1 / energy_contribution) * γ
)
```

### Layer-specific Hardware Costs
| Layer Position | Latency Impact | Pruning Priority |
|----------------|----------------|------------------|
| Early layers | High (large activations) | Higher priority |
| Middle layers | Medium | Medium |
| Late layers | Low (small activations) | Lower priority |

### Đọc thêm
- Hardware-aware Network Pruning (2020)
- Network Slimming (2017)

---

## 34. Pruning Large Language Models for Edge Deployment

### Mô tả
Áp dụng pruning cho LLMs như GPT, LLaMA để chạy trên edge devices.

### LLM Pruning Challenges
- Huge model sizes (7B - 175B parameters)
- Complex attention mechanisms
- Maintaining coherence sau pruning

### Structured Pruning for LLMs
```
LLM Structure:
├── Embedding layers     → Hard to prune
├── Attention heads      → Can prune some heads
├── FFN layers           → Can prune neurons
└── Output layers        → Keep intact
```

### Techniques
1. **Head pruning**: Remove entire attention heads
2. **Width pruning**: Reduce hidden dimensions
3. **Depth pruning**: Remove entire layers
4. **Vocabulary pruning**: Reduce embedding size

### Đọc thêm
- SparseGPT (2023)
- LLM-Pruner (2023)
- Wanda (2023)

---

## 35. Sparse Tensor Core Utilization

### Mô tả
Tối ưu hóa neural networks để tận dụng Sparse Tensor Cores trong modern GPUs.

### Tensor Core Evolution
```
Volta (V100):  Dense Tensor Cores only
Ampere (A100): Dense + Sparse Tensor Cores (2:4)
Hopper (H100): Enhanced sparse operations
```

### Requirements for Sparse TC
- 2:4 structured sparsity pattern
- Specific matrix dimensions
- Proper data layout

### Optimization Workflow
```
1. Train with sparsity-inducing regularization
2. Convert to 2:4 pattern
3. Fine-tune
4. Use cuSPARSELt library
5. Profile and optimize
```

### Đọc thêm
- NVIDIA cuSPARSELt Documentation
- Structured Pruning for Tensor Cores (2021)

---

## 36. Co-design of Pruning Algorithms and Hardware

### Mô tả
Đồng thiết kế pruning algorithms và hardware architectures để maximize efficiency.

### Co-design Space
```
┌─────────────────────────────────────────┐
│            Co-design Space               │
├──────────────────┬──────────────────────┤
│   Algorithm      │    Hardware          │
├──────────────────┼──────────────────────┤
│ Sparsity pattern │ Sparse accelerator   │
│ Pruning ratio    │ Memory organization  │
│ Granularity      │ Datapath design      │
│ Regularity       │ Index encoding       │
└──────────────────┴──────────────────────┘
```

### Example: Column-balanced Sparsity
- Algorithm: Ensure equal sparsity per column
- Hardware: Simplified load balancing logic

### Research Directions
- Hardware-algorithm matching
- Sparsity format optimization
- Custom pruning for custom accelerators

### Đọc thêm
- EIE: Efficient Inference Engine (2016)
- Sparse Architecture Co-design (2020)

---

## 37. Progressive Pruning with Hardware Feedback

### Mô tả
Pruning iteratively với feedback từ actual hardware measurements.

### Iterative Process
```
Initial Model
    │
    ├──→ Prune small percentage
    │        │
    │        ▼
    │    Deploy on hardware
    │        │
    │        ▼
    │    Measure latency/accuracy
    │        │
    │        ▼
    │    Adjust pruning strategy
    │        │
    └────────┘
    Until target met
```

### Feedback Signals
- Actual latency (not estimated)
- Memory bandwidth utilization
- Energy consumption
- Thermal behavior

### Benefits
- More accurate than analytical models
- Captures complex hardware behaviors
- Adapts to hardware variations

### Đọc thêm
- NetAdapt (2018)
- AMC (2018)

---

## 📚 Pruning Toolbox

### Libraries
| Library | Features |
|---------|----------|
| **PyTorch Pruning** | Basic structured/unstructured |
| **NVIDIA NeMo** | LLM pruning |
| **Neural Magic** | Sparsity training |
| **Intel Neural Compressor** | Hardware-aware pruning |

### Best Practices
1. Start with sensitivity analysis
2. Use gradual pruning schedule
3. Fine-tune after pruning
4. Validate on target hardware
5. Consider sparsity + quantization together
