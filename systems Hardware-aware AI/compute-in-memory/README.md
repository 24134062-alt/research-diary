# ⚡ Compute-In-Memory (CIM) - Research Hub

> **Hướng nghiên cứu chuyên sâu về Compute-In-Memory**  
> **Cập nhật**: 12/2024

---

## 📁 Cấu Trúc Thư Mục

```
compute-in-memory/
├── README.md (file này)
├── fundamentals/          # Kiến thức nền tảng
├── papers/               # Notes về papers quan trọng
├── projects/             # Projects thực hành
├── simulations/          # Code simulation
└── resources/            # Tài liệu tham khảo
```

---

## 🎯 Mục Tiêu Học Tập

### Phase 1: Memory Technologies (4 tuần)
- [ ] SRAM, DRAM basics
- [ ] ReRAM (Resistive RAM) physics
- [ ] PCM, MRAM, Flash basics
- [ ] Device non-idealities

### Phase 2: CIM Architectures (4 tuần)
- [ ] Crossbar array basics
- [ ] Matrix-vector multiplication in crossbar
- [ ] ADC/DAC design concepts
- [ ] CIM architecture designs

### Phase 3: Simulation & Projects (4 tuần)
- [ ] NeuroSim simulator
- [ ] DNN mapping to crossbar
- [ ] Accuracy under non-idealities
- [ ] Energy/latency analysis

---

## 📚 Key Topics

| Topic | File | Status |
|-------|------|--------|
| Memory Wall Problem | `fundamentals/memory-wall.md` | 🔲 Todo |
| ReRAM Basics | `fundamentals/reram-basics.md` | 🔲 Todo |
| Crossbar Arrays | `fundamentals/crossbar.md` | 🔲 Todo |
| CIM Architectures | `fundamentals/cim-arch.md` | 🔲 Todo |
| Device Variations | `fundamentals/variations.md` | 🔲 Todo |

---

## 🔗 Quick Links

### Simulators
- [NeuroSim](https://github.com/neurosim) - Georgia Tech
- [DNN+NeuroSim](https://github.com/neurosim/DNN_NeuroSim_V1.4)
- [CrossSim](https://github.com/sandialabs/cross-sim) - Sandia Labs

### Key Labs
- Georgia Tech (Prof. Shimeng Yu)
- Stanford (Prof. Wong)
- MIT (Prof. Chandrakasan)
- Tsinghua University

### Conferences
- ISCA, MICRO (Architecture)
- ISSCC (Circuits)
- DAC, ICCAD (Design)
- IEDM (Devices)

---

## 🔬 Core Concepts

### The Memory Wall

```
       Traditional Computing           Goal of CIM
       
┌─────────┐   ←Data→   ┌─────────┐    ┌─────────────────┐
│ Compute │◄─────────►│ Memory  │    │ Memory+Compute  │
└─────────┘           └─────────┘    │   (Integrated)  │
     ↑                                └─────────────────┘
 Bottleneck!                         No data movement!
```

### Crossbar Computing

```
     V₁  V₂  V₃  (Inputs)
      │   │   │
  ────●───●───●──── I₁ = V₁G₁₁ + V₂G₁₂ + V₃G₁₃
      │   │   │
  ────●───●───●──── I₂ = V₁G₂₁ + V₂G₂₂ + V₃G₂₃
      │   │   │
  ────●───●───●──── I₃ = V₁G₃₁ + V₂G₃₂ + V₃G₃₃

  ● = Memory cell (conductance G = weight)
  → Matrix-vector multiply in O(1)!
```

---

## 🚀 Getting Started

### Prerequisites
- Basic electronics knowledge
- Python programming
- Neural network basics

### Setup NeuroSim (Simulation)

```bash
# Clone NeuroSim
git clone https://github.com/neurosim/DNN_NeuroSim_V1.4.git
cd DNN_NeuroSim_V1.4

# Follow installation guide in repository
# Requires C++ compiler
```

### Simple Crossbar Simulation (Python)

```python
import numpy as np

def crossbar_matmul(V_input, G_weights, noise_sigma=0.01):
    """
    Simulate crossbar matrix-vector multiplication
    
    V_input: Input voltages (vector)
    G_weights: Conductance matrix (weights)
    noise_sigma: Device variation noise
    """
    # Add device variation (Gaussian noise)
    G_noisy = G_weights + np.random.normal(0, noise_sigma, G_weights.shape)
    
    # Crossbar computation: I = V * G (Ohm's law)
    I_output = np.dot(G_noisy.T, V_input)
    
    return I_output

# Example
weights = np.random.randn(4, 8)  # 4 inputs, 8 outputs
inputs = np.random.rand(4)

# Ideal computation
ideal_output = np.dot(weights.T, inputs)

# CIM computation (with noise)
cim_output = crossbar_matmul(inputs, weights, noise_sigma=0.05)

# Compare
error = np.mean(np.abs(ideal_output - cim_output))
print(f"Mean absolute error: {error:.4f}")
```

---

## 📊 Key Challenges

| Challenge | Difficulty | Research Opportunity |
|-----------|------------|---------------------|
| Device variations | High | Robust training methods |
| Limited precision | Medium | Quantization-aware training |
| ADC/DAC overhead | Medium | ADC-free designs |
| Write endurance | High | Write reduction strategies |
| Mapping algorithms | Medium | Compiler optimization |

---

## 📝 Notes

*Thêm ghi chú của bạn tại đây...*
