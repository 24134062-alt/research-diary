# 🌿 Bio-inspired & Dendritic Computing

> **Cập nhật**: 12/2024  
> **Mức độ nghiên cứu**: Very Emerging (30-50 papers/năm)  
> **Cơ hội**: Rất cao - Underexplored, interdisciplinary

---

## 📌 Tổng Quan

Bio-inspired computing mở rộng beyond simple artificial neurons, học hỏi từ các cơ chế phức tạp của não bộ như **dendritic computation**, **neuromodulation**, và **adaptive plasticity**.

### Beyond Point Neurons

```
Traditional ANN Neuron:        Biological Neuron:
                               
y = σ(Σwᵢxᵢ + b)              ┌─────────────────────┐
                               │     DENDRITES       │
  Simple weighted sum          │  ┌───┐ ┌───┐ ┌───┐ │
  + nonlinearity               │  └─┬─┘ └─┬─┘ └─┬─┘ │
                               │    │     │     │   │◄──Local computation
                               │    └──┬──┘     │   │
                               │       └────────┤   │
                               │         SOMA   │   │
                               │         ┌──────┤   │
                               │         │      │   │
                               │      AXON      │   │
                               └─────────────────────┘
                               Multiple sites of computation!
```

---

## 🔥 Developments 2024

### Dendritic Computing Highlights

| Development | Source | Significance |
|-------------|--------|--------------|
| **Dendristor** | Tsinghua University | Neuromorphic dendritic network model |
| **Graphene artificial dendrites** | NSF Research | GrADs for analog neuromorphic |
| **Active dendrites for SNNs** | arXiv | Continual learning, reduce catastrophic forgetting |
| **Quadratic neurons** | NeurIPS 2024 | Dendritic-inspired ANNs |

### Bio-inspired AI Trends 2024
- Integration with **neuromorphic computing**
- **Quantum-bio hybrid** exploration
- Applications in **robotics** (RoboBee, RoboRay)
- Healthcare: Drug discovery, personalized medicine

---

## 🧠 Dendritic Computing Deep Dive

### Why Dendrites Matter

```
Point neuron assumption:
Inputs → Sum → Activation → Output
             ↑
        Single computation

Reality (biological neurons):
Inputs → Dendrite 1 → Local computation ─┐
Inputs → Dendrite 2 → Local computation ─┼→ Soma → Integration → Output
Inputs → Dendrite 3 → Local computation ─┘

Multiple stages of nonlinear processing!
Increases computational power significantly
```

### Dendritic Non-linearities

#### Types of Dendritic Computation

| Type | Mechanism | Function |
|------|-----------|----------|
| **Passive** | Cable properties | Spatial filtering |
| **Active** | Voltage-gated channels | Amplification |
| **Plateau potentials** | NMDA spikes | Coincidence detection |
| **Backpropagation** | AP propagation | Learning signals |

### Computational Implications

```
Learning capacity comparison:

Point neuron:
├── Input-output mappings: Limited
└── Learning speed: Baseline

Dendritic neuron:
├── Input-output mappings: Significantly increased
└── Learning speed: Faster (more sites for plasticity)

Research shows: Dendritic complexity → Better learning
```

---

## 🔬 Key Research Areas

### 1. Artificial Dendrites

#### Tsinghua Dendristor (2024)

```
Dendristor architecture:
├── Mimics tree-like dendrite morphology
├── Non-linear integration of synaptic inputs
├── Energy-efficient visual perception
└── Hardware implementation ready
```

#### Graphene Artificial Dendrites (GrADs)

```
GrAD Features:
├── Graphene-based devices
├── Analog computing capabilities
├── Complex dendritic processing
└── Neuromorphic integration potential
```

### 2. Dendritic Neural Networks

#### Architecture

```python
class DendriticNeuron:
    def __init__(self, n_dendrites, inputs_per_dendrite):
        self.dendrites = [
            DendriticBranch(inputs_per_dendrite)
            for _ in range(n_dendrites)
        ]
        self.soma_weights = nn.Parameter(torch.randn(n_dendrites))
    
    def forward(self, x):
        # Dendritic processing (local nonlinearities)
        dendrite_outputs = [
            dendrite(x_subset) 
            for dendrite, x_subset in zip(self.dendrites, x.split())
        ]
        
        # Somatic integration
        soma_input = sum(w * d for w, d in 
                        zip(self.soma_weights, dendrite_outputs))
        
        return activation(soma_input)
```

### 3. Active Dendrites for Continual Learning

#### Catastrophic Forgetting Problem

```
Standard NN:
Task 1 training → Task 2 training → Forget Task 1!

With Active Dendrites (2024):
Task 1 training → Task 2 training → Remember both!

Mechanism:
├── Different dendrites activated for different tasks
├── Context-dependent gating
└── Protects previous task representations
```

---

## 🌳 Bio-inspired Principles

### 1. Sparse Coding

```
Brain: Only ~1-5% neurons active at any time

Bio-inspired sparse networks:
├── Energy efficient
├── Robust to noise
├── Better generalization
└── Memory efficient
```

### 2. Local Learning Rules

| Rule | Mechanism | Advantage |
|------|-----------|-----------|
| **Hebbian** | "Fire together, wire together" | No backprop needed |
| **STDP** | Spike-timing dependent | Temporal learning |
| **BCM** | Sliding threshold | Homeostasis |
| **Oja's rule** | Normalized Hebbian | Stable learning |

### 3. Neuromodulation

```
Global modulators affect local computation:

Dopamine → Reward signals
Acetylcholine → Attention
Norepinephrine → Arousal
Serotonin → Mood/behavior

Bio-inspired AI can incorporate:
├── Attention mechanisms (ACh-inspired)
├── Reward-modulated learning (DA-inspired)
└── Uncertainty estimation (NE-inspired)
```

### 4. Hierarchical Processing

```
Biological vision hierarchy:
V1 → V2 → V4 → IT → PFC
 │     │     │    │     │
Simple → Complex features → Object recognition → Decision

Inspired:
├── CNNs (loosely)
├── Transformers (attention)
└── Cortical models
```

---

## 📊 Research Gaps & Opportunities

### High Opportunity Areas

| Gap | Current State | Potential Impact |
|-----|---------------|------------------|
| **Dendritic ANNs** | Few implementations | High |
| **Local learning at scale** | Limited | Very High |
| **Neuromodulated AI** | Early research | High |
| **Bio-plausible backprop** | Active research | High |
| **Astrocyte-inspired** | Very few papers | Medium-High |
| **Sleep/consolidation** | Emerging | High |

### Open Research Questions

1. **Can dendritic computation improve deep learning?**
   - Early results promising
   - Need systematic evaluation

2. **How to implement local learning at scale?**
   - Backprop not biologically plausible
   - Local rules hard to scale

3. **What can we learn from other brain cell types?**
   - Astrocytes, interneurons
   - Understudied in AI

---

## 🛠️ Implementations

### Frameworks & Libraries

| Tool | Purpose | Source |
|------|---------|--------|
| **Nupic** | HTM (Hierarchical Temporal Memory) | Numenta |
| **BRIAN2** | Biologically realistic simulation | Open source |
| **NEURON** | Detailed neuron models | Yale |
| **BindsNET** | SNN simulation | Open source |

### Example: Simple Dendritic Network

```python
import torch
import torch.nn as nn

class DendriticLayer(nn.Module):
    def __init__(self, n_inputs, n_outputs, n_dendrites=4):
        super().__init__()
        self.n_dendrites = n_dendrites
        inputs_per_dendrite = n_inputs // n_dendrites
        
        # Dendritic branches (local processing)
        self.dendrites = nn.ModuleList([
            nn.Sequential(
                nn.Linear(inputs_per_dendrite, 32),
                nn.Tanh(),  # Local nonlinearity
            )
            for _ in range(n_dendrites)
        ])
        
        # Somatic integration
        self.soma = nn.Linear(32 * n_dendrites, n_outputs)
    
    def forward(self, x):
        # Split input to dendrites
        x_split = x.chunk(self.n_dendrites, dim=-1)
        
        # Local dendritic computation
        dendrite_outputs = [d(x_d) for d, x_d in zip(self.dendrites, x_split)]
        
        # Integrate at soma
        soma_input = torch.cat(dendrite_outputs, dim=-1)
        return self.soma(soma_input)
```

---

## 📚 Key References

### Must-Read Papers
1. "Dendritic Computing: The What, Where, and How" (Neuron, 2020)
2. "Active dendrites enable strong but sparse inputs to determine orientation selectivity" (PNAS, 2021)
3. "How to Build a Brain: From Function to Implementation" (Nature Reviews Neuroscience, 2023)
4. "A dendritic mechanism for decoding traveling waves" (Neuron, 2024)

### Key Research Groups
- **Numenura** (Jeff Hawkins - HTM)
- **Kording Lab** (Penn - Neural computation)
- **Larkum Lab** (Humboldt - Dendritic computation)
- **Blue Brain Project** (EPFL - Detailed simulation)

### Conferences
- **COSYNE** (Computational and Systems Neuroscience)
- **BIC-TA** (Bio-inspired Computing)
- **NeurIPS** (Bio-plausible learning workshops)
- **ICLR** (Neuro-AI workshops)

---

## 💡 Research Ideas

### Beginner Level
1. **Compare point vs dendritic neurons**: Simple classification tasks
2. **Implement STDP**: Local learning in small networks
3. **Survey bio-inspired AI**: Recent advances

### Intermediate Level
4. **Dendritic networks for continual learning**: Reproduce 2024 results
5. **Sparse bio-inspired networks**: Efficiency analysis
6. **Attention as neuromodulation**: Connect to neuroscience

### Advanced Level
7. **Novel dendritic architectures**: Beyond current designs
8. **Local learning at scale**: Biologically plausible deep learning
9. **Astrocyte-inspired modulation**: Understudied area

---

## 📈 Future Outlook

### Trends

```
2024-2025: Dendritic networks gain traction
2025-2027: Integration with neuromorphic hardware
2027-2030: Large-scale bio-plausible learning
2030+:     Brain-like AI systems?
```

### Key Challenges
- **Scalability**: Bio-inspired often slower to train
- **Benchmarks**: Need standardized evaluation
- **Theory**: Why do these principles help?
- **Hardware**: Specialized accelerators needed

### Opportunities
- **Unique approach**: Differentiate from mainstream DL
- **Interdisciplinary**: Neuroscience + CS + Engineering
- **Efficiency**: Potential for extreme efficiency gains
- **Robustness**: Brain-like fault tolerance
