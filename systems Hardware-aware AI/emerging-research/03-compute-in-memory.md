# ⚡ Compute-in-Memory (CIM) & Processing-in-Memory (PIM)

> **Cập nhật**: 12/2024  
> **Mức độ nghiên cứu**: Emerging (50-80 papers/năm)  
> **Cơ hội**: Cao - Cần interdisciplinary expertise

---

## 📌 Tổng Quan

Compute-in-Memory (CIM) phá vỡ kiến trúc von Neumann truyền thống bằng cách **thực hiện tính toán trực tiếp trong memory**, tránh bottleneck data movement.

### The Memory Wall Problem
```
Traditional (von Neumann):
┌─────────┐    ┌─────────┐
│ Compute │◄──►│ Memory  │  ← Data movement = 200x energy vs compute!
└─────────┘    └─────────┘
       ↑
    Bottleneck

Compute-in-Memory:
┌─────────────────────────┐
│   Memory + Compute      │  ← No data movement!
│   (Integrated)          │
└─────────────────────────┘
```

### Energy Breakdown (Typical DNN)
| Component | Energy (Traditional) |
|-----------|---------------------|
| DRAM access | 200 pJ |
| SRAM access | 6 pJ |
| MAC operation | 1 pJ |

**→ 99% energy spent on data movement!**

---

## 🔥 Research 2024 Highlights

### Key Papers 2024

| Paper | Venue | Contribution |
|-------|-------|--------------|
| **CRPIM** | NTHU | Compute-reuse for ReRAM PIM, significant speedup |
| **RACA** | arXiv | ADC-free ReRAM accelerator, improved efficiency |
| **Edge AI with ReRAM** | HKU | ReRAM-aware NAS for edge devices |
| **ReS-CIM** | DAC 2024 | ReRAM-cached SRAM CIM architecture |
| **Reliability in ReRAM CIM** | arXiv | Survey on SNN + ReRAM reliability |

### Emerging Trends
1. **ADC-free designs**: Eliminate expensive converters
2. **Hybrid SRAM-ReRAM**: Combine best of both
3. **CIM for LLMs**: Attention mechanism acceleration
4. **Reliability-aware design**: Handle device variations

---

## 🔬 Technology Deep Dive

### ReRAM (Resistive RAM) Basics

```
ReRAM Cell:
High Resistance State (HRS) = "0" / Low weight
Low  Resistance State (LRS) = "1" / High weight

Multiple levels possible → Analog weight storage
```

### Crossbar Array for Matrix-Vector Multiply

```
     V₁   V₂   V₃   (Input voltages = activations)
      │    │    │
  ────●────●────●──── → I₁ = Σ(Vⱼ × G₁ⱼ)
      │    │    │
  ────●────●────●──── → I₂ = Σ(Vⱼ × G₂ⱼ)
      │    │    │
  ────●────●────●──── → I₃ = Σ(Vⱼ × G₃ⱼ)

  ● = ReRAM cell (G = conductance = weight)

Ohm's law: I = V × G
Kirchhoff: Sum currents per row
→ Matrix-vector multiply in O(1) time!
```

### CIM Technologies Comparison

| Technology | Type | Precision | Endurance | Speed | Energy |
|------------|------|-----------|-----------|-------|--------|
| **SRAM CIM** | Volatile | 4-8 bit | Unlimited | Fast | Medium |
| **ReRAM** | Non-volatile | 2-4 bit | 10⁶-10¹² | Fast | Low |
| **PCM** | Non-volatile | 4-8 bit | 10⁸ | Medium | Medium |
| **Flash** | Non-volatile | 4-8 bit | 10⁵ | Slow | Low |
| **MRAM** | Non-volatile | 1-2 bit | 10¹⁵ | Fast | Medium |

---

## 🏗️ Architecture Designs

### 1. Basic ReRAM CIM Architecture

```
┌─────────────────────────────────────────────────┐
│                 ReRAM CIM Tile                   │
├─────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────┐  │
│  │            ReRAM Crossbar Array            │  │
│  │  (Weights encoded as conductances)         │  │
│  └───────────────────────────────────────────┘  │
│       ↑                               ↓         │
│  ┌────┴────┐                    ┌─────┴─────┐   │
│  │   DAC   │  (Input→Voltage)  │    ADC    │   │
│  └─────────┘                    └───────────┘   │
│       ↑                               ↓         │
│  ┌────┴────┐                    ┌─────┴─────┐   │
│  │ Digital │                    │  Digital  │   │
│  │  Input  │                    │  Output   │   │
│  └─────────┘                    └───────────┘   │
└─────────────────────────────────────────────────┘
```

### 2. ADC-Free Design (RACA, 2024)

```
No ADC/DAC needed:
- Analog computation throughout
- Implicit activation functions
- Significant energy savings

Tradeoff: Lower precision, need careful design
```

### 3. Hybrid SRAM-ReRAM (ReS-CIM, 2024)

```
┌─────────────────────────────────────┐
│           Hybrid Architecture       │
├─────────────────────────────────────┤
│  ReRAM: Long-term weight storage    │
│         (Non-volatile)              │
│              ↓                      │
│  SRAM:  Active computation          │
│         (High speed, reliable)      │
└─────────────────────────────────────┘

Benefits:
- ReRAM: Dense, non-volatile, energy efficient
- SRAM: Fast, reliable, unlimited endurance
```

---

## 📊 Research Gaps & Opportunities

### High Opportunity Areas

| Gap | Difficulty | Impact | Papers 2024 |
|-----|------------|--------|-------------|
| **CIM for LLMs** | Hard | Very High | Few |
| **CIM for Transformers** | Hard | High | ~5-10 |
| **Reliability solutions** | Medium | High | ~10-15 |
| **CIM-aware NAS** | Medium | High | ~5 |
| **Security in CIM** | Medium | High | ~5 |
| **CIM training** | Very Hard | Revolutionary | Very few |

### Open Research Questions

1. **How to handle device variations?**
   - Non-idealities affect accuracy
   - Need robust training/mapping methods

2. **CIM for complex operations beyond MAC?**
   - Attention, softmax, layer norm?
   - Currently limited to dense matrix-vector

3. **CIM training (not just inference)?**
   - Weight updates require high precision
   - Endurance limitations for ReRAM

4. **Large model deployment?**
   - How to map GPT-scale models to CIM?
   - Memory capacity limitations

---

## ⚠️ Challenges & Solutions

### Device-Level Challenges

| Challenge | Description | Solution Approaches |
|-----------|-------------|---------------------|
| **Variation** | Cell-to-cell differences | In-situ training, calibration |
| **Noise** | Read/write noise | Error correction, redundancy |
| **Endurance** | Limited write cycles | Write reduction, wear leveling |
| **Stuck faults** | Cells fail permanently | Remapping, redundancy |
| **Drift** | Resistance changes over time | Refresh, recalibration |

### System-Level Challenges

| Challenge | Description | Solution Approaches |
|-----------|-------------|---------------------|
| **Precision** | Limited analog bits | Mixed-precision, multiple cells |
| **ADC overhead** | Energy/area cost | ADC-free designs, shared ADC |
| **Programming** | Slow write operations | Incremental updates |
| **Mapping** | Fit model to crossbars | CIM-aware compilation |

---

## 🛠️ Tools & Simulation

### Simulation Frameworks

| Tool | Purpose | Source |
|------|---------|--------|
| **NeuroSim** | CIM performance estimation | GitHub (GT) |
| **MNSIM** | Memristor NN simulation | GitHub |
| **DNN+NeuroSim** | End-to-end simulation | Georgia Tech |
| **CrossSim** | Crossbar simulation | Sandia Labs |

### Example Simulation Flow

```python
# Pseudo-code for CIM simulation
def simulate_cim(model, crossbar_config):
    # Map weights to crossbar
    mapped_weights = map_to_crossbar(model.weights, 
                                      crossbar_config)
    
    # Add non-idealities
    noisy_weights = add_device_variation(mapped_weights,
                                         sigma=0.05)
    
    # Simulate inference
    for input in test_data:
        analog_input = dac_convert(input)
        output = crossbar_compute(analog_input, noisy_weights)
        digital_output = adc_convert(output)
    
    # Evaluate accuracy under non-idealities
    return evaluate_accuracy(digital_output)
```

---

## 📚 Key References

### Must-Read Papers
1. "ISAAC: A Convolutional Neural Network Accelerator with In-situ Analog Arithmetic in Crossbars" (ISCA, 2016)
2. "PRIME: A Novel Processing-in-Memory Architecture" (ISCA, 2016)
3. "In-Memory Computing: Advances and Prospects" (IEEE, 2023)
4. "ReRAM-based Accelerators for DNNs: A Survey" (2024)

### Key Research Groups
- **Georgia Tech** (Prof. Shimeng Yu - NeuroSim)
- **Stanford** (Prof. Wong - ReRAM)
- **MIT** (Prof. Chandrakasan)
- **Tsinghua University** (Prof. Qian)
- **KAIST** (Korea)

### Conferences
- **ISCA/MICRO** (Computer Architecture)
- **ISSCC** (Circuits)
- **DAC/ICCAD** (Design Automation)
- **IEDM** (Device)

---

## 💡 Research Ideas

### Beginner Level
1. **Simulation study**: Impact of device variations on accuracy
2. **Benchmark**: Compare CIM vs GPU for specific models
3. **Survey**: Analysis of recent CIM architectures

### Intermediate Level
4. **CIM-aware quantization**: Optimize for crossbar constraints
5. **Fault tolerance**: Redundancy schemes for stuck-at faults
6. **Hybrid architectures**: When to use CIM vs digital

### Advanced Level
7. **CIM for attention mechanisms**: Transformer acceleration
8. **On-chip CIM training**: Handle limited endurance
9. **Large model mapping**: Chip-let based CIM for LLMs

---

## 📈 Industry & Career

### Companies Working on CIM

| Company | Focus | Products |
|---------|-------|----------|
| **Samsung** | HBM-PIM | Commercial (2021+) |
| **SK Hynix** | PIM DRAM | Development |
| **Intel** | Various | Research |
| **Mythic** | Analog CIM | Startup |
| **Syntiant** | Voice AI | Commercial |
| **Tetramem** | ReRAM | Startup |

### Skills Needed
- **Hardware**: Device physics, circuit design
- **Software**: Compiler, mapping algorithms
- **ML**: Model optimization, robustness
- **Interdisciplinary**: Rare combination = high value!
