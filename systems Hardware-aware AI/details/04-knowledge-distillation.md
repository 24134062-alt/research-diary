# Category IV: Knowledge Distillation

> **Tổng quan**: Knowledge Distillation là kỹ thuật chuyển "kiến thức" từ một model lớn (teacher) sang model nhỏ hơn (student) để student đạt performance tương đương nhưng efficient hơn.

---

## 38. Hardware-aware Knowledge Distillation

### Mô tả
Thiết kế student network và distillation process với awareness về target hardware constraints.

### Traditional vs Hardware-aware
```
Traditional:                     Hardware-aware:
Teacher → Student                Teacher → Student
         (fixed arch)                     (optimized for hardware)
                                          + Latency constraint
                                          + Memory constraint
                                          + Energy constraint
```

### Distillation với Hardware Constraints
```python
Loss = α * TaskLoss(student_output, labels) +
       β * DistillLoss(student_output, teacher_output) +
       γ * max(0, Latency(student) - TargetLatency)
```

### Joint Optimization
- Student architecture search + distillation
- Layer-wise distillation importance based on hardware
- Progressive distillation with hardware feedback

### Đọc thêm
- Hardware-aware Knowledge Distillation (2021)
- Student-Teacher Networks for Edge AI (2020)

---

## 39. Self-distillation for Efficient Networks

### Mô tả
Model tự distill knowledge vào chính nó, không cần separate teacher.

### Concept
```
┌────────────────────────────────────────┐
│              Same Network               │
├──────────────────┬─────────────────────┤
│   Deep Path      │    Shallow Path     │
│   (Teacher)      │    (Student)        │
│        │         │         ▲           │
│        └─────────┼─────────┘           │
│          Distill │                     │
└──────────────────┴─────────────────────┘
```

### Methods
1. **Be Your Own Teacher (BYOT)**: Later layers teach earlier layers
2. **Deep Mutual Learning**: Multiple networks teach each other
3. **Born-Again Networks**: Train new network with same architecture

### Benefits
- No need for separate teacher
- Single training process
- Regularization effect

### Đọc thêm
- Self-Distillation (2019)
- Born-Again Neural Networks (2018)
- Deep Mutual Learning (2018)

---

## 40. Feature-based Distillation for Edge AI

### Mô tả
Distill intermediate feature representations, không chỉ final outputs.

### Feature Points for Distillation
```
Teacher Network:
Input → [F1] → [F2] → [F3] → [F4] → Output
          ↓      ↓      ↓      ↓
Student Network:
Input → [f1] → [f2] → [f3] → [f4] → Output

Distillation: Align F_i with f_i
```

### Alignment Methods
| Method | Operation | Cost |
|--------|-----------|------|
| **Direct matching** | MSE(F, f) | Low |
| **Attention transfer** | Match attention maps | Medium |
| **Gram matrices** | Match style/texture | Medium |
| **Contrastive** | Learn similarities | High |

### Adapter Layers
```python
# When dimensions don't match
class Adapter(nn.Module):
    def __init__(self, student_dim, teacher_dim):
        self.proj = nn.Linear(student_dim, teacher_dim)
    
    def forward(self, student_features):
        return self.proj(student_features)
```

### Đọc thêm
- FitNets (2015)
- Attention Transfer (2017)
- Contrastive Representation Distillation (2020)

---

## 41. Distillation-aware Architecture Design

### Mô tả
Thiết kế student architectures đặc biệt tối ưu cho distillation.

### Design Considerations
```
Good Student for Distillation:
├── Similar structure to teacher (easier mapping)
├── Sufficient capacity to absorb knowledge
├── Efficient computation
└── Hardware-friendly operations
```

### Architecture Matching
| Teacher Component | Student Equivalent |
|------------------|-------------------|
| Large conv | Depthwise-separable conv |
| Attention | Linear attention / Local attention |
| Deep layers | Skip connections |
| Wide layers | Narrow + deeper |

### Capacity Analysis
```
Need: Student Capacity >= Essential Knowledge
But:  Student Capacity << Teacher Capacity

Sweet spot: Just enough capacity for task knowledge
```

### Đọc thêm
- Structured Knowledge Distillation (2019)
- Architecture-aware KD (2020)

---

## 42. Multi-teacher Distillation for Robust Edge Models

### Mô tả
Sử dụng nhiều teacher models để distill knowledge đa dạng vào một student.

### Multi-teacher Setup
```
Teacher 1 (ImageNet expert)  ─┐
Teacher 2 (Detection expert)  ├─→ Student
Teacher 3 (Segmentation)     ─┘
```

### Knowledge Aggregation
1. **Averaging**: Average teacher outputs
2. **Weighted**: Learnable weights per teacher
3. **Selective**: Choose best teacher per sample
4. **Ensemble**: Combine with attention

### Benefits
- More robust knowledge
- Better generalization
- Task-specific expertise

### Đọc thêm
- Multi-teacher Knowledge Distillation (2020)
- Ensemble Knowledge Distillation (2019)

---

## 43. Online Distillation on Resource-constrained Devices

### Mô tả
Perform distillation trực tiếp trên edge devices với limited resources.

### Challenges
```
Edge Device Constraints:
├── Limited memory: Can't load large teacher
├── Limited compute: Can't run teacher inference
├── Limited storage: Can't store teacher
└── Limited power: Battery considerations
```

### Solutions
1. **Cached teacher outputs**: Pre-compute and store
2. **Partial teacher**: Load only necessary layers
3. **Progressive**: Distill incrementally
4. **Federated**: Distill across devices

### On-device Workflow
```
Cloud: Teacher inference → Cache outputs
Edge:  Load cached outputs → Train student locally
```

### Đọc thêm
- On-device Training Survey (2021)
- Federated Knowledge Distillation (2020)

---

## 44. Task-specific Distillation for TinyML

### Mô tả
Customize distillation cho specific TinyML tasks như keyword spotting, wake word, gesture recognition.

### TinyML Task Examples
| Task | Input | Output | Typical Size |
|------|-------|--------|--------------|
| Keyword spotting | Audio | Class | <50KB |
| Wake word | Audio | Binary | <20KB |
| Gesture | IMU data | Class | <30KB |
| Anomaly detection | Sensor | Binary | <10KB |

### Task-specific Considerations
```
Keyword Spotting:
├── Temporal features important
├── Spectral features secondary
├── Distill along time axis
└── Focus on phoneme representations
```

### Đọc thêm
- TinyML KD (2021)
- Efficient Audio Classification (2020)

---

## 45. Progressive Distillation with Hardware Constraints

### Mô tả
Distill theo stages, dần dần reduce model size while respecting hardware limits at each stage.

### Progressive Schedule
```
Stage 1: Teacher → Student-Large (2x compression)
Stage 2: Student-Large → Student-Medium (4x total)
Stage 3: Student-Medium → Student-Small (8x total)
Stage 4: Student-Small → Student-Tiny (16x total)
```

### Benefits of Progressive Approach
- Easier optimization (smaller gap each step)
- Can stop at any stage
- Better final accuracy than direct distillation

### Hardware-aware Staging
```
At each stage, validate:
├── Accuracy acceptable?
├── Latency within budget?
├── Memory fits device?
└── Energy consumption OK?

If all yes → continue to next stage
If accuracy < threshold → stop
```

### Đọc thêm
- Progressive Knowledge Distillation (2019)
- Staged Training (2020)

---

## 📚 Distillation Toolbox

### Key Papers
1. "Distilling Knowledge in Neural Networks" (Hinton, 2015)
2. "FitNets" (2015)
3. "Knowledge Distillation Survey" (2020)

### Temperature Scaling
```python
# Soft targets with temperature
soft_targets = softmax(teacher_logits / temperature)
soft_predictions = softmax(student_logits / temperature)

KD_loss = KL_divergence(soft_predictions, soft_targets) * (temperature ** 2)
```

### Best Practices
- Higher temperature (T=4-20) for more knowledge transfer
- Combine with hard labels (α * hard + (1-α) * soft)
- Match intermediate representations
- Consider layer-wise learning rates
