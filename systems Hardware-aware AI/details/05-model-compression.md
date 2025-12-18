# Category V: Model Compression

> **Tổng quan**: Model Compression bao gồm các kỹ thuật ngoài pruning và quantization để giảm kích thước và computation của neural networks.

---

## 46. Low-rank Factorization for Efficient Inference

### Mô tả
Phân tích ma trận weights thành tích của các ma trận có rank thấp hơn để giảm computation.

### Concept
```
Original Weight Matrix W (m × n):
- Parameters: m × n
- Computation: O(mn)

Low-rank Factorization W ≈ U × V:
- U: m × k
- V: k × n
- Parameters: k(m + n)  [if k << min(m,n)]
- Computation: O(k(m + n))
```

### Decomposition Methods
| Method | Description | Use Case |
|--------|-------------|----------|
| **SVD** | Singular Value Decomposition | General |
| **Tucker** | Multi-dimensional decomposition | Conv layers |
| **CP** | CANDECOMP/PARAFAC | 4D tensors |
| **TT** | Tensor Train | Very large layers |

### Example: Conv Layer Decomposition
```
Original: (C_out, C_in, K, K) → C_out × C_in × K² params

CP decomposition:
(C_out, R) × (C_in, R) × (K, R) × (K, R)
Parameters: R × (C_out + C_in + 2K)
```

### Đọc thêm
- Speeding up CNNs with Low-rank Expansions (2014)
- Tucker Decomposition for CNNs (2016)

---

## 47. Weight Sharing Strategies for Hardware Efficiency

### Mô tả
Multiple weights share same value, reducing unique parameters và enabling efficient codebook lookup.

### Concept
```
Original weights: [1.2, 0.8, 1.3, 0.9, 1.1, 0.7, 1.2, 0.8]
After clustering: [A,   B,   A,   B,   A,   B,   A,   B]
Codebook: A=1.2, B=0.8 (only 2 values to store)
```

### K-means Clustering
1. Cluster weights into K centroids
2. Replace each weight with nearest centroid
3. Store: index array + centroid codebook
4. Fine-tune centroids

### Compression Ratio
```
Original: 32 bits per weight
Clustered: log2(K) bits per index + K × 32 bits for codebook

Example with K=16, 1M weights:
Original: 32M bits
Clustered: 4M bits + 512 bits ≈ 4M bits (8x compression)
```

### Đọc thêm
- Deep Compression (Han et al., 2016)
- Hashed Nets (2015)

---

## 48. Neural Network Compression for Real-time Applications

### Mô tả
Compression techniques đặc biệt cho latency-critical applications.

### Real-time Requirements
| Application | Latency Budget | FPS Requirement |
|-------------|---------------|-----------------|
| Autonomous driving | <100ms | 10-30 FPS |
| Video conferencing | <50ms | 30 FPS |
| Gaming | <16ms | 60 FPS |
| VR/AR | <7ms | 90+ FPS |

### Compression for Latency
```
Focus areas:
├── Reduce memory bottlenecks (activation compression)
├── Reduce computation (pruning, quantization)
├── Reduce model loading (smaller size)
└── Reduce I/O overhead (operator fusion)
```

### Latency Profiling
```python
# Profile each component
breakdown = {
    'conv_layers': 45%,
    'fc_layers': 30%,
    'memory_ops': 15%,
    'other': 10%
}
# Focus compression on largest contributors
```

### Đọc thêm
- Real-time Neural Networks (2020)
- Latency-aware Compression (2019)

---

## 49. Joint Compression: Pruning + Quantization + Distillation

### Mô tả
Kết hợp nhiều techniques compression để đạt maximum efficiency.

### Compression Pipeline
```
Original Model
    │
    ▼
Knowledge Distillation (smaller architecture)
    │
    ▼
Pruning (remove unimportant weights)
    │
    ▼
Quantization (reduce precision)
    │
    ▼
Highly Compressed Model
```

### Joint Training
```python
Loss = TaskLoss + 
       α * SparsityRegularization +  # Pruning
       β * QuantizationLoss +         # Quantization  
       γ * DistillationLoss           # Distillation
```

### Multiplicative Compression
```
Distillation: 4x smaller architecture
Pruning: 5x fewer weights
Quantization: 4x smaller (INT8)
─────────────────────────────
Total: 80x compression!
```

### Đọc thêm
- Deep Compression (2016)
- Joint Quantization and Pruning (2019)

---

## 50. Compression-aware Training from Scratch

### Mô tả
Train networks từ đầu với awareness về compression sẽ được applied.

### Approach
```
Traditional: Train → Compress → Fine-tune
Compression-aware: Train with compression simulation → Deploy
```

### Training Modifications
1. **Simulated quantization**: Fake quantize during forward pass
2. **Soft pruning**: Learnable pruning masks
3. **Progressive regularization**: Gradually increase sparsity

### Benefits
- Better final accuracy
- No fine-tuning needed
- Model "learns to be compressed"

### Đọc thêm
- Training Quantized Networks from Scratch (2019)
- Gradual Pruning (2018)

---

## 51. Dynamic Model Compression based on Input Complexity

### Mô tả
Adjust compression level dynamically based on input difficulty.

### Concept
```
Easy Input:  Use highly compressed model → Fast
Hard Input:  Use less compressed model  → Accurate

Complexity Estimator → Route to appropriate model path
```

### Multi-exit Architecture
```
Input → Block1 → [Exit1: very compressed] 
              ↓
        Block2 → [Exit2: moderately compressed]
              ↓
        Block3 → [Exit3: full model]
```

### Complexity Estimation
- **Confidence-based**: Exit if confidence > threshold
- **Entropy-based**: Exit if entropy < threshold
- **Learned**: Train classifier for input difficulty

### Đọc thêm
- Adaptive Neural Networks (2017)
- SkipNet (2018)

---

## 52. Compressing Vision Transformers for Edge Devices

### Mô tả
Áp dụng compression cho Vision Transformers (ViT) để deploy trên edge.

### ViT Challenges
```
ViT-Base: 86M params, 17.5 GFLOPs
DeiT-Base: 86M params, 17.5 GFLOPs

Compare to:
MobileNetV3: 5M params, 0.2 GFLOPs
```

### Compression Strategies
| Strategy | Description | Reduction |
|----------|-------------|-----------|
| **Patch pruning** | Remove uninformative patches | 30-50% |
| **Head pruning** | Remove attention heads | 20-40% |
| **Token reduction** | Merge similar tokens | 30-60% |
| **Layer dropping** | Skip layers | 20-40% |
| **Quantization** | INT8 attention | 4x |

### Efficient ViT Designs
- **DeiT**: Distillation-trained ViT
- **MobileViT**: Mobile-friendly ViT
- **EfficientViT**: Hardware-efficient design

### Đọc thêm
- DeiT (2021)
- MobileViT (Apple, 2021)
- EfficientViT (2023)

---

## 53. LLM Compression for On-device Inference

### Mô tả
Compress Large Language Models (GPT, LLaMA) để chạy trên devices.

### LLM Sizes
| Model | Parameters | FP16 Size |
|-------|------------|-----------|
| GPT-2 | 1.5B | 3GB |
| LLaMA-7B | 7B | 14GB |
| LLaMA-13B | 13B | 26GB |
| LLaMA-70B | 70B | 140GB |

### Compression Techniques for LLMs
```
1. Quantization: FP16 → INT4 (4x reduction)
2. Pruning: Remove 50% weights (2x)
3. Distillation: 7B → 1B student (7x)
4. Combined: 50-200x reduction possible
```

### Key Papers
- **GPTQ**: Post-training quantization for GPT
- **QLoRA**: Quantized Low-Rank Adaptation
- **AWQ**: Activation-aware Weight Quantization
- **SqueezeLLM**: Sensitivity-based quantization

### On-device LLMs
```
Target: Run 7B model on smartphone
Memory: 4-8GB available
Approach: 4-bit quantization → 3.5GB
Add: KV cache optimization, speculative decoding
```

### Đọc thêm
- GPTQ (2023)
- llama.cpp (open source)
- MLC-LLM (2023)

---

## 📚 Compression Summary

### Technique Comparison
| Technique | Model Size | Latency | Accuracy | Complexity |
|-----------|------------|---------|----------|------------|
| Quantization | 4x | 2x faster | -1-2% | Low |
| Pruning | 2-10x | 1.5-3x | -1-5% | Medium |
| Distillation | 4-10x | 4-10x | -2-5% | High |
| Low-rank | 2-4x | 1.5-2x | -1-3% | Medium |
| Combined | 20-100x | 10-50x | -3-10% | High |
