# Category VI: Hardware Accelerators

> **Tổng quan**: Hardware Accelerators là các phần cứng chuyên dụng được thiết kế để tăng tốc các workloads của neural networks, từ GPU, TPU đến FPGA và ASIC.

---

## 54. FPGA-based Neural Network Accelerator Design

### Mô tả
Thiết kế accelerators trên FPGA để chạy neural network inference với customizable architecture.

### FPGA Advantages
```
┌─────────────────────────────────────────────┐
│              FPGA Benefits                   │
├─────────────────────────────────────────────┤
│ ✓ Reconfigurable logic                      │
│ ✓ Low latency (no OS overhead)              │
│ ✓ Power efficient                            │
│ ✓ Custom precision (arbitrary bit-widths)   │
│ ✓ Parallel processing                        │
└─────────────────────────────────────────────┘
```

### FPGA Resources
| Resource | Purpose | Typical Use |
|----------|---------|-------------|
| **LUTs** | Logic operations | Control, routing |
| **DSPs** | Multiply-accumulate | Convolutions, FC |
| **BRAMs** | On-chip memory | Weights, activations |
| **I/O** | External communication | Data loading |

### Design Flow
```
Neural Network → HLS/RTL Design → Synthesis → Place & Route → Bitstream
                      ↓
              Optimization:
              - Loop unrolling
              - Pipelining
              - Data reuse
```

### Đọc thêm
- FINN (Xilinx, 2017)
- VTA (TVM, 2018)
- Vitis AI (Xilinx/AMD)

---

## 55. ASIC Design for Deep Learning Inference

### Mô tả
Custom chip design tối ưu cho deep learning inference workloads.

### ASIC vs Other Platforms
| Aspect | ASIC | FPGA | GPU |
|--------|------|------|-----|
| Performance | Best | Good | Good |
| Power | Best | Good | High |
| Flexibility | None | High | Medium |
| Development cost | Very High | Medium | Low |
| Time to market | Long | Medium | Short |

### Famous AI ASICs
```
Google TPU:      Matrix multiply focused
Apple Neural Engine: Mobile AI
Qualcomm NPU:    Mobile AI
Tesla FSD:       Autonomous driving
Cerebras WSE:    Wafer-scale chip
```

### Design Considerations
1. **Dataflow architecture**: How data moves through chip
2. **Memory hierarchy**: On-chip SRAM, HBM
3. **Precision support**: INT8, INT4, FP16
4. **Scalability**: Multi-chip configurations

### Đọc thêm
- In-Datacenter Performance of TPU (Google, 2017)
- Eyeriss (MIT, 2017)

---

## 56. Reconfigurable Computing for Adaptive AI

### Mô tả
Architectures có thể reconfigure để match different workloads và models.

### Reconfigurability Levels
```
┌──────────────────────────────────────┐
│     Reconfigurability Spectrum       │
├──────────────────────────────────────┤
│ ASIC  ← Fixed                        │
│ CGRA  ← Coarse-grained              │
│ FPGA  ← Fine-grained                │
│ GPU   ← Programmable                │
│ CPU   ← General purpose →           │
└──────────────────────────────────────┘
```

### Coarse-Grained Reconfigurable Arrays (CGRA)
- Processing elements với configurable interconnects
- Faster reconfiguration than FPGA
- Higher efficiency than GPU for specific workloads

### Use Cases
- Multi-model deployment
- Dynamic precision switching
- Adaptive computation based on input

### Đọc thêm
- CGRA Survey (2021)
- Plasticine (Stanford, 2017)

---

## 57. Dataflow Architectures for Neural Networks

### Mô tả
Thiết kế data movement patterns tối ưu để maximize reuse và minimize memory access.

### Dataflow Types
| Dataflow | Reuses | Best For |
|----------|--------|----------|
| **Weight stationary** | Weights | Large models |
| **Output stationary** | Partial sums | Deep networks |
| **Input stationary** | Activations | Wide layers |
| **Row stationary** | All types | Balanced |

### Weight Stationary Example
```
Load weights once into PE array
Stream inputs through
Accumulate outputs

PE: Processing Element
┌─────┬─────┬─────┐
│ PE  │ PE  │ PE  │◄─ Same weights loaded
├─────┼─────┼─────┤
│ PE  │ PE  │ PE  │◄─ Different inputs stream
├─────┼─────┼─────┤
│ PE  │ PE  │ PE  │◄─ Outputs accumulated
└─────┴─────┴─────┘
```

### Energy Breakdown
```
Energy per operation:
DRAM access:     200× MAC energy
SRAM access:     6× MAC energy
Register access: 1× MAC energy
MAC operation:   1× (baseline)

→ Maximize reuse at lower memory levels!
```

### Đọc thêm
- Eyeriss (MIT, 2017) - Row stationary
- TPU (Google) - Weight stationary
- NVDLA (NVIDIA) - Design framework

---

## 58. Memory Hierarchy Optimization for DNN Accelerators

### Mô tả
Thiết kế và tối ưu memory hierarchy để reduce bottlenecks.

### Memory Hierarchy
```
            ┌─────────────┐
            │    DRAM     │  Size: GB, BW: 100GB/s
            └──────┬──────┘
                   │
            ┌──────▼──────┐
            │  Global     │  Size: MBs, BW: 1TB/s
            │  Buffer     │
            └──────┬──────┘
                   │
            ┌──────▼──────┐
            │  PE Local   │  Size: KBs, BW: 10TB/s
            │  Memory     │
            └──────┬──────┘
                   │
            ┌──────▼──────┐
            │  Registers  │  Size: Bytes
            └─────────────┘
```

### Optimization Techniques
1. **Tiling**: Break large tensors into tiles that fit
2. **Double buffering**: Overlap compute and load
3. **Prefetching**: Load data before needed
4. **Compression**: Reduce data movement

### Đọc thêm
- Memory-Centric DNN Accelerators (2019)
- Timeloop (NVIDIA, 2019)

---

## 59. Systolic Array Design for Matrix Operations

### Mô tả
Thiết kế systolic arrays - regular PE arrays với rhythmic data flow cho matrix operations.

### Systolic Array Concept
```
Data flows like "blood through heart" (systolic)

Input A →  ┌────┐  ┌────┐  ┌────┐
           │ PE │→ │ PE │→ │ PE │→ Output C
           └─┬──┘  └─┬──┘  └─┬──┘
Input B ↓   │       │       │
           ┌▼───┐  ┌▼───┐  ┌▼───┐
           │ PE │→ │ PE │→ │ PE │→
           └─┬──┘  └─┬──┘  └─┬──┘
             │       │       │
           ┌▼───┐  ┌▼───┐  ┌▼───┐
           │ PE │→ │ PE │→ │ PE │→
           └────┘  └────┘  └────┘
```

### Each PE Operation
```python
# Per PE per cycle
c += a * b  # MAC operation
# Pass a to right, b down
```

### TPU Systolic Array
- Google TPU v1: 256×256 systolic array
- 65,536 MACs per cycle
- INT8/INT16 precision

### Đọc thêm
- TPU Architecture (Google)
- Systolic Array Primer

---

## 60. Multi-chip Module Design for Large Models

### Mô tả
Thiết kế systems với multiple chips để handle models quá lớn cho single chip.

### Why Multi-chip?
```
Large Models (GPT-3: 175B params):
- Single chip: ~1-10B params max
- Need: 20+ chips for full model

Also: Higher throughput via parallelism
```

### Parallelism Strategies
| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Data parallel** | Same model, different data | Training |
| **Model parallel** | Split model across chips | Large models |
| **Pipeline parallel** | Different layers on chips | Deep models |
| **Tensor parallel** | Split tensors | Large layers |

### Interconnect Design
```
Chip-to-chip communication:
├── NVLink (NVIDIA): 900 GB/s
├── Infinity Fabric (AMD): 512 GB/s  
├── TPU Interconnect (Google): 4.5 TB/s per chip
└── Custom PCIe: 32 GB/s per link
```

### Đọc thêm
- Megatron-LM (NVIDIA, 2019)
- GPipe (Google, 2019)

---

## 61. 3D-stacked Memory Integration for AI Accelerators

### Mô tả
Tích hợp 3D-stacked memory (HBM) với compute để reduce memory bottleneck.

### HBM (High Bandwidth Memory)
```
Traditional:        3D Stacked (HBM):
┌─────────┐        ┌─────────────────┐
│  CPU    │        │   Memory Dies   │
└────┬────┘        │   ┌───┬───┬───┐ │
     │             │   │   │   │   │ │
┌────▼────┐        │   └───┴───┴───┘ │
│  DRAM   │        │   ┌───────────┐ │
└─────────┘        │   │   Logic   │ │
Wide bus needed    └───┴───────────┴─┘
                   Short vertical connections
```

### HBM Specifications
| Gen | Bandwidth | Capacity | Power |
|-----|-----------|----------|-------|
| HBM1 | 128 GB/s | 4GB | 1W/GB |
| HBM2 | 256 GB/s | 8GB | 0.8W/GB |
| HBM2e | 460 GB/s | 16GB | 0.7W/GB |
| HBM3 | 819 GB/s | 24GB | 0.6W/GB |

### Benefits for AI
- Reduce memory-bound bottlenecks
- Support larger batch sizes
- Enable bigger on-chip models

### Đọc thêm
- HBM in AI Accelerators (2020)
- NVIDIA A100/H100 Architecture

---

## 62. Accelerator Virtualization for Multi-tenant Deployment

### Mô tả
Chia sẻ AI accelerators giữa multiple users/models một cách efficient.

### Virtualization Approaches
```
┌─────────────────────────────────────────┐
│              Physical GPU                │
├─────────┬─────────┬─────────┬───────────┤
│ VM 1    │ VM 2    │ VM 3    │ VM 4      │
│ Model A │ Model B │ Model A │ Model C   │
└─────────┴─────────┴─────────┴───────────┘
```

### Technologies
- **NVIDIA MIG**: Multi-Instance GPU
- **NVIDIA vGPU**: Virtual GPU
- **AMD MxGPU**: SR-IOV based
- **Intel GVT-g**: Graphics virtualization

### Challenges
- Resource isolation
- Performance interference
- Memory partitioning
- Scheduling fairness

### Đọc thêm
- NVIDIA MIG Documentation
- GPU Virtualization Survey (2021)

---

## 63. Power Management for AI Accelerators

### Mô tả
Quản lý power consumption để balance performance và energy efficiency.

### Power Components
```
Total Power = Dynamic + Static + I/O

Dynamic: Computation, data movement (∝ activity)
Static:  Leakage (∝ chip area, always on)
I/O:     External communication
```

### Power Management Techniques
| Technique | Description | Savings |
|-----------|-------------|---------|
| **DVFS** | Dynamic voltage/frequency | 20-50% |
| **Clock gating** | Stop unused blocks | 10-30% |
| **Power gating** | Cut power to blocks | 50-90% |
| **Precision switching** | Lower precision | 30-50% |

### TDP Management
```
Thermal Design Power (TDP):
├── Sustained power limit
├── Burst above TDP short-term
├── Throttle when overheating
└── Balance thermal vs performance
```

### Đọc thêm
- Energy-efficient DNN Accelerators (2019)
- GPU Power Management

---

## 64. Thermal-aware Accelerator Design

### Mô tả
Thiết kế accelerators với awareness về thermal constraints.

### Thermal Challenges
```
Heat generation → Temperature rise → Issues:
├── Performance throttling
├── Reliability degradation  
├── Shorter lifespan
└── Higher cooling costs
```

### Thermal Management
1. **Design-time**: Floorplanning, power distribution
2. **Run-time**: DVFS, task migration, workload scheduling
3. **Cooling**: Heatsinks, fans, liquid cooling

### Dark Silicon Problem
```
Not all transistors can be active simultaneously
due to power/thermal limits.

Solution: Heterogeneous design
- Some cores high-performance
- Some cores energy-efficient
- Dynamic switching based on thermal state
```

### Đọc thêm
- Thermal-aware DNN Accelerators (2020)

---

## 65. Security Considerations in AI Hardware

### Mô tả
Bảo mật hardware AI khỏi các attacks và data leakage.

### Threat Model
```
Threats:
├── Model extraction (steal model)
├── Input inference (reveal inputs)
├── Side-channel attacks (timing, power)
└── Adversarial attacks via hardware
```

### Security Measures
| Measure | Protects Against |
|---------|-----------------|
| **Encryption** | Data in transit/rest |
| **TEE** | Privileged access |
| **Memory encryption** | Physical access |
| **Constant-time ops** | Timing attacks |
| **Power noise** | Power analysis |

### Trusted Execution Environment (TEE)
```
┌─────────────────────────────────────┐
│           Normal World               │
├─────────────────────────────────────┤
│           Secure World (TEE)         │
│  ┌─────────────────────────────┐    │
│  │   AI Model (Protected)       │    │
│  │   Input/Output (Encrypted)   │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

### Đọc thêm
- ML Hardware Security Survey (2021)
- NVIDIA Confidential Computing

---

## 📚 Hardware Accelerator Ecosystem

### Major Players
| Company | Products | Focus |
|---------|----------|-------|
| NVIDIA | GPU, Tensor Cores | General AI |
| Google | TPU | Cloud AI |
| Apple | Neural Engine | Mobile AI |
| Intel | Habana, IPU | Datacenter |
| AMD | MI series | HPC/AI |
| Cerebras | WSE | Large models |
| Graphcore | IPU | Training |
