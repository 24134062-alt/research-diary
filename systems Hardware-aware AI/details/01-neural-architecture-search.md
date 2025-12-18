# Category I: Neural Architecture Search (NAS)

> **Tổng quan**: Neural Architecture Search là phương pháp tự động hóa việc thiết kế kiến trúc mạng neural thay vì thiết kế thủ công bởi chuyên gia.

---

## 1. Hardware-aware Neural Architecture Search for Edge Devices

### Mô tả
Thiết kế tự động các kiến trúc mạng neural được tối ưu hóa cho các thiết bị edge như smartphone, IoT sensors, microcontrollers.

### Vấn đề giải quyết
- Thiết bị edge có giới hạn về memory, compute, và năng lượng
- Cần models đạt accuracy cao nhưng vẫn chạy được trên hardware hạn chế
- Trade-off giữa performance và deployability

### Phương pháp chính
```
Search Space → Search Strategy → Hardware Constraints → Optimal Architecture
     ↓              ↓                    ↓
  (Ops, Layers)   (RL, Evolution,    (Latency,
                   Gradient-based)    Energy, Memory)
```

### Đọc thêm
- MnasNet (Google, 2019)
- ProxylessNAS (MIT, 2019)
- FBNet (Facebook, 2019)

---

## 2. Differentiable NAS with Hardware Constraints

### Mô tả
Sử dụng gradient descent để tìm kiếm kiến trúc tối ưu, tích hợp các ràng buộc phần cứng như differentiable loss terms.

### Vấn đề giải quyết
- NAS truyền thống rất tốn tài nguyên (hàng nghìn GPU hours)
- Cần phương pháp nhanh hơn để tìm kiếm
- Khó tối ưu đồng thời accuracy và hardware metrics

### Ý tưởng cốt lõi
```python
# Pseudo-code
Loss = CrossEntropy(output, target) + λ * HardwareCost(architecture)
# HardwareCost có thể là latency, energy, hoặc memory
# Cần HardwareCost phải differentiable
```

### Kỹ thuật
- **Gumbel-Softmax**: Làm cho discrete choices trở nên differentiable
- **Latency lookup tables**: Precompute latency cho từng operation
- **Differentiable latency predictors**: Train neural network để predict latency

### Đọc thêm
- DARTS (CMU, 2019)
- SNAS (SenseTime, 2019)
- FBNetV2 (Facebook, 2020)

---

## 3. Multi-Objective NAS: Balancing Accuracy, Latency, and Energy

### Mô tả
Tìm kiếm kiến trúc tối ưu cho nhiều mục tiêu đồng thời, không chỉ accuracy mà còn latency, energy consumption, memory footprint.

### Vấn đề giải quyết
- Single-objective optimization không đủ cho real-world deployment
- Cần Pareto-optimal solutions cho các trade-offs khác nhau
- User có thể chọn model phù hợp với constraints cụ thể

### Pareto Front Concept
```
Accuracy ↑
    │      ●  ●  ● ← Pareto Front (best trade-offs)
    │   ●
    │ ●
    │●
    └──────────────→ Latency ↑
```

### Phương pháp
- **Weighted Sum**: Combine objectives với weights
- **NSGA-II/III**: Evolutionary multi-objective optimization
- **Scalarization**: Transform multi-objective thành single objective

### Đọc thêm
- LEMONADE (Bosch, 2019)
- NSGANetV2 (2020)
- DONNA (MIT, 2021)

---

## 4. Zero-shot NAS for Resource-Constrained Devices

### Mô tả
Đánh giá và xếp hạng các kiến trúc mà không cần training, sử dụng các proxy metrics có thể compute nhanh.

### Vấn đề giải quyết
- Training mỗi architecture candidate rất tốn thời gian
- Resource-constrained scenarios không thể afford nhiều training runs
- Cần cách nhanh để filter out bad architectures

### Proxy Metrics phổ biến
| Metric | Ý nghĩa | Compute Cost |
|--------|---------|--------------|
| **#Parameters** | Model size | O(1) |
| **#MACs/FLOPs** | Computation | O(1) |
| **Gradient norm** | Trainability | O(1 forward-backward) |
| **Synflow** | Signal propagation | O(1 forward) |
| **NASWOT** | Architecture expressivity | O(mini-batch) |

### Đọc thêm
- Zero-Cost Proxies (2021)
- Training-free NAS (2021)
- ZenNAS (2021)

---

## 5. Transferable NAS across Heterogeneous Hardware Platforms

### Mô tả
Thiết kế methods để transfer NAS results từ một hardware platform sang platform khác mà không cần search lại từ đầu.

### Vấn đề giải quyết
- Mỗi hardware platform có characteristics khác nhau
- Search riêng cho từng platform rất tốn kém
- Cần generalization across platforms

### Approaches
1. **Meta-learning**: Learn to adapt quickly to new hardware
2. **Hardware embedding**: Encode hardware characteristics as vectors
3. **Predictor adaptation**: Fine-tune latency predictors for new hardware

### Đọc thêm
- HAT (MIT, 2020)
- OFA (Once-for-All, MIT, 2020)
- APQ (2020)

---

## 6. Reinforcement Learning-based Hardware-aware NAS

### Mô tả
Sử dụng RL agents để explore search space và maximize reward function bao gồm cả accuracy và hardware efficiency.

### Framework
```
Controller (RNN) → Generate Architecture → Train & Evaluate → Reward
      ↑                                                          │
      └──────────────────────────────────────────────────────────┘
      
Reward = Accuracy - λ * (Latency / Target_Latency)
```

### Challenges
- **Sample inefficiency**: RL cần nhiều samples
- **Reward shaping**: Cách design reward function
- **Exploration-exploitation**: Balance giữa explore new architectures và exploit good ones

### Algorithms sử dụng
- Policy Gradient (REINFORCE)
- Proximal Policy Optimization (PPO)
- Q-learning variants

### Đọc thêm
- NASNet (Google, 2018)
- MnasNet (Google, 2019)
- HAQ (MIT, 2019)

---

## 7. Evolutionary Algorithms for Hardware-efficient Architecture Search

### Mô tả
Sử dụng evolutionary algorithms (EA) như genetic algorithms để evolve neural network architectures với hardware constraints.

### Process
```
Population → Selection → Crossover → Mutation → New Population
    ↓            ↓           ↓           ↓            ↓
 [Arch1,     (Fittest    (Combine    (Random      [Arch1',
  Arch2,      survive)    parents)    changes)     Arch2',
  ...]                                             ...]
```

### Fitness Function
```python
fitness = accuracy * (target_latency / actual_latency) ^ β
# β controls importance of latency constraint
```

### Advantages
- Naturally handles multi-objective optimization
- No gradient computation required
- Good for discrete, complex search spaces

### Đọc thêm
- AmoebaNet (Google, 2019)
- CARS (2020)
- Regularized Evolution (2019)

---

## 8. Once-for-All Networks: Train Once, Deploy Anywhere

### Mô tả
Train một "super-network" duy nhất có thể extract ra nhiều sub-networks phù hợp với các hardware constraints khác nhau.

### Concept
```
┌─────────────────────────────────────────┐
│           Once-for-All Network          │
│  ┌─────────────────────────────────┐    │
│  │ Contains all possible sub-nets  │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
            │
            ▼
  ┌─────────────────────────────────────────────────┐
  │  Mobile  │  Tablet  │   PC   │  Server  │  Cloud │
  │  subnet  │  subnet  │ subnet │  subnet  │ subnet │
  └─────────────────────────────────────────────────┘
```

### Searchable Dimensions
- Depth (số layers)
- Width (số channels per layer)
- Kernel size
- Resolution (input size)

### Benefits
- Train once, reduce cost significantly
- Instant deployment to new hardware
- No separate search needed

### Đọc thêm
- Once-for-All (MIT Han Lab, 2020)
- BigNAS (Google, 2020)
- AttentiveNAS (Facebook, 2021)

---

## 9. Supernet Training for Hardware-aware Model Selection

### Mô tả
Techniques để train weight-sharing supernets hiệu quả, enabling fair comparison giữa các architectures.

### Weight Sharing Concept
```
Supernet: All architectures share weights
          │
          ├── Subnet A: Uses subset of weights
          ├── Subnet B: Uses different subset  
          └── Subnet C: Another subset
```

### Challenges
- **Interference**: Different subnets competing for same weights
- **Fairness**: Ensuring all subnets get adequate training
- **Ranking consistency**: Supernet ranking ≠ standalone ranking

### Solutions
- Progressive shrinking
- Sandwich rule training
- Knowledge distillation from full network

### Đọc thêm
- Single-Path NAS (2019)
- FairNAS (2019)
- SPOS (2020)

---

## 10. Latency Predictor Design for NAS

### Mô tả
Thiết kế các predictors có thể estimate latency của một architecture trên target hardware mà không cần actually run.

### Approaches
| Approach | Input | Accuracy | Speed |
|----------|-------|----------|-------|
| **Lookup Table** | Operation type | Medium | Very Fast |
| **Linear Model** | Op counts | Low | Very Fast |
| **MLP Predictor** | Architecture encoding | High | Fast |
| **GNN Predictor** | Computation graph | Very High | Medium |

### Latency Breakdown
```
Total Latency = Σ(Op latency) + Memory transfer + Overhead

Op latency = f(op_type, input_size, hardware_config)
```

### Đọc thêm
- nn-Meter (Microsoft, 2021)
- BRP-NAS (2020)
- HELP (2021)

---

## 11. Memory-aware Neural Architecture Search

### Mô tả
NAS với focus đặc biệt vào memory constraints - peak memory usage, memory bandwidth, activation memory.

### Memory Components
```
Total Memory = Weight Memory + Activation Memory + Workspace
    │              │                │                │
    │         (Parameters)    (Intermediate)    (Temp buffers)
    │
    └── Must fit in device RAM/SRAM
```

### Optimization Targets
- Peak memory reduction
- Memory access patterns
- Buffer reuse optimization

### Techniques
- In-place operations
- Activation checkpointing-aware search
- Memory-efficient operators

### Đọc thêm
- MemNAS (2020)
- MCUNet (MIT, 2020)

---

## 12. Energy-aware NAS for Battery-powered Devices

### Mô tả
Tối ưu hóa energy consumption thay vì chỉ latency, quan trọng cho wearables, IoT, mobile devices.

### Energy Model
```
Energy = Dynamic Energy + Static Energy
       = Σ(Op energy) + Leakage * Time

Op energy ∝ #Memory accesses + #Computations
```

### Considerations
- Memory access energy >> Computation energy
- Battery capacity constraints
- Thermal throttling effects

### Đọc thêm
- EfficientNet (Google, 2019)
- GreenAI (2019)

---

## 13. NAS for Specialized Hardware Accelerators (TPU, NPU, FPGA)

### Mô tả
Thiết kế NAS methods đặc biệt cho các accelerators với characteristics độc đáo.

### Hardware Characteristics

| Accelerator | Strengths | NAS Considerations |
|-------------|-----------|-------------------|
| **TPU** | Matrix multiply, high throughput | Batch size, tensor shapes |
| **NPU** | Low power, fixed ops | Supported ops, precision |
| **FPGA** | Reconfigurable, customizable | Resource utilization, routing |

### FPGA-specific
- Look for parallelizable architectures
- Consider resource types (LUTs, DSPs, BRAMs)
- Pipeline-friendly designs

### Đọc thêm
- Co-Exploration (2019)
- FPGA-aware NAS (2020)

---

## 14. Automated Search Space Design for Hardware-aware NAS

### Mô tả
Tự động thiết kế search space thay vì manually define, adapting to target hardware.

### Problem
- Manual search space design requires expertise
- Suboptimal search space leads to suboptimal results
- Different hardware may need different search spaces

### Approaches
1. **Search space shrinking**: Start large, prune irrelevant parts
2. **Search space growing**: Start small, expand promising regions
3. **Meta-learning**: Learn good search spaces from previous searches

### Đọc thêm
- Neural Predictor for NAS (2019)
- AutoSpace (2021)

---

## 15. Proxy Tasks for Efficient Hardware-aware NAS

### Mô tả
Sử dụng smaller/simpler tasks làm proxy để đánh giá architectures nhanh hơn.

### Proxy Types
| Proxy | Description | Speedup |
|-------|-------------|---------|
| **Reduced epochs** | Train fewer epochs | 10-100x |
| **Reduced dataset** | Use subset of data | 10-50x |
| **Reduced resolution** | Lower input size | 2-5x |
| **Smaller model** | Scale down architecture | 5-20x |

### Correlation Challenge
```
Proxy performance ←?→ Full training performance
                   │
        Need high rank correlation
```

### Đọc thêm
- NASBENCH (Google, 2019)
- Proxy validation studies (2020)

---

## 📚 Tài Liệu Tổng Hợp

### Must-read Papers
1. "Neural Architecture Search: A Survey" (2019)
2. "A Survey on Hardware-aware Neural Architecture Search" (2021)
3. "Efficient Deep Learning: A Survey" (2020)

### Influential Works
- NASNet → đặt nền tảng cho NAS
- DARTS → differentiable approach
- Once-for-All → practical deployment
- MnasNet → hardware-aware pioneer

### Conferences
- NeurIPS, ICML, ICLR (top ML venues)
- CVPR, ICCV, ECCV (computer vision)
- DAC, ICCAD (hardware design)
- MLSys (systems for ML)
