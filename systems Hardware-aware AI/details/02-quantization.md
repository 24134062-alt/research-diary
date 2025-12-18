# Category II: Quantization

> **Tổng quan**: Quantization là kỹ thuật giảm độ chính xác số học của weights và activations từ floating-point (FP32) xuống lower precision (INT8, INT4, binary) để tăng tốc inference và giảm memory.

---

## 16. Mixed-Precision Quantization with Hardware Constraints

### Mô tả
Sử dụng các bit-widths khác nhau cho các layers khác nhau trong network, tối ưu cho hardware cụ thể.

### Ý tưởng
```
Layer 1: 8-bit  ←  Sensitive layer, cần precision cao
Layer 2: 4-bit  ←  Less sensitive, có thể compress
Layer 3: 8-bit  ←  Critical for accuracy
Layer 4: 2-bit  ←  Highly compressible
```

### Hardware Considerations
- **Supported precisions**: Không phải hardware nào cũng hỗ trợ mọi bit-width
- **Precision switching cost**: Overhead khi chuyển đổi giữa precisions
- **Memory alignment**: Certain bit-widths align better in memory

### Optimization Problem
```
minimize    Latency(quantized_model)
subject to  Accuracy_drop ≤ threshold
            Bit-widths ∈ {2, 4, 8, 16, 32}
```

### Đọc thêm
- HAQ: Hardware-Aware Automated Quantization (MIT, 2019)
- Mixed Precision Quantization of DNNs (2018)

---

## 17. Quantization-aware Training for Ultra-Low Precision (Binary, Ternary)

### Mô tả
Train networks với ultra-low precision (1-2 bits), simulate quantization effects during training.

### Precision Levels
| Bits | Values | Memory Reduction |
|------|--------|------------------|
| Binary (1-bit) | {-1, +1} | 32x |
| Ternary (2-bit) | {-1, 0, +1} | 16x |
| 4-bit | 16 levels | 8x |
| 8-bit | 256 levels | 4x |

### Training Challenges
```
Forward Pass:  Use quantized weights → discrete
Backward Pass: Need gradients → continuous

Solution: Straight-Through Estimator (STE)
          ∂L/∂w ≈ ∂L/∂w_quantized
```

### Binary Networks
```python
# Binary weight
w_binary = sign(w_real)  # +1 or -1

# Binary convolution: very efficient
# XNOR + popcount instead of multiply-accumulate
output = popcount(XNOR(input_binary, weight_binary))
```

### Đọc thêm
- BinaryConnect (2015)
- XNOR-Net (2016)
- ReActNet (2020)

---

## 18. Hardware-aware Post-Training Quantization

### Mô tả
Quantize model đã train xong mà không cần retrain, với awareness về target hardware.

### Process
```
Trained FP32 Model → Calibration → Quantization → Optimized INT8 Model
                         ↓
                   (Small dataset
                    to determine
                    scale/zero-point)
```

### Calibration Methods
| Method | Description | Accuracy |
|--------|-------------|----------|
| **Min-Max** | Use min/max values | Low |
| **Percentile** | Use percentile values | Medium |
| **MSE** | Minimize quantization error | High |
| **Cross-entropy** | Minimize output difference | Highest |

### Hardware-aware Aspects
- Choose quantization scheme supported by hardware
- Per-tensor vs per-channel quantization
- Symmetric vs asymmetric quantization

### Đọc thêm
- Post-training Quantization (Google, 2018)
- NVIDIA TensorRT Quantization

---

## 19. Dynamic Quantization for Adaptive Inference

### Mô tả
Điều chỉnh quantization dynamically based on input data hoặc runtime conditions.

### Approaches
1. **Input-dependent**: Adjust precision based on input complexity
2. **Layer-adaptive**: Different precision for different inputs per layer
3. **Runtime-adaptive**: Change precision based on battery/thermal state

### Benefits
```
Easy Input → Lower Precision → Faster, Less Energy
Hard Input → Higher Precision → More Accuracy
```

### Implementation
```python
def dynamic_forward(x):
    complexity = estimate_complexity(x)
    if complexity < threshold:
        return quantized_forward(x, bits=4)
    else:
        return quantized_forward(x, bits=8)
```

### Đọc thêm
- Dynamic Network Quantization (2019)
- Input-adaptive Quantization (2020)

---

## 20. Quantization for Transformer Models on Edge Devices

### Mô tả
Áp dụng quantization cho Transformers (BERT, GPT, ViT) để deploy trên edge devices.

### Transformer Challenges
- **Attention mechanism**: Softmax requires higher precision
- **Layer Norm**: Sensitive to quantization
- **Large models**: BERT-base = 110M params

### Key Observations
```
Transformer Layers:
├── Self-Attention  → Most sensitive, need 8-bit
├── FFN Linear      → Less sensitive, can use 4-bit
├── LayerNorm       → Keep FP32 or use approximation
└── Embeddings      → Can be heavily quantized
```

### Special Techniques
- **Outlier-aware quantization**: Handle outliers in activations
- **I-BERT**: Integer-only BERT inference
- **Q8BERT**: 8-bit quantized BERT

### Đọc thêm
- Q-BERT (2019)
- I-BERT (2021)
- TernaryBERT (2020)

---

## 21. Layer-wise Optimal Bit-width Allocation

### Mô tả
Xác định bit-width tối ưu cho từng layer để maximize accuracy dưới constraint về model size hoặc latency.

### Problem Formulation
```
maximize    Accuracy(model)
subject to  Σ(bits_i × params_i) ≤ Budget
            bits_i ∈ {2, 4, 8}
```

### Sensitivity Analysis
```
Sensitivity Score per Layer:
Layer 1: 0.85  ← High sensitivity, need more bits
Layer 2: 0.23  ← Low sensitivity, can compress
Layer 3: 0.67  ← Medium sensitivity
...
```

### Methods
1. **Heuristic**: Assign bits based on sensitivity ranking
2. **Optimization**: Use integer programming
3. **Learning-based**: Use RL or gradient-based methods

### Đọc thêm
- Mixed Precision DNNs (2018)
- HAWQ (2019)

---

## 22. Quantization Error Compensation Techniques

### Mô tả
Các kỹ thuật bù đắp cho accuracy loss do quantization.

### Error Sources
```
Quantization Error = Round(x × scale) / scale - x
                   = Rounding error + Clipping error
```

### Compensation Techniques

| Technique | Description |
|-----------|-------------|
| **Bias Correction** | Adjust biases to correct mean shift |
| **AdaRound** | Learned rounding instead of nearest |
| **BRECQ** | Block-wise reconstruction |
| **QDrop** | Randomly drop quantization during training |

### Bias Correction Example
```python
# Original output: E[Wx]
# Quantized output: E[Q(W)x] ≠ E[Wx]
# Correction: bias_new = bias + E[Wx] - E[Q(W)x]
```

### Đọc thêm
- Data-Free Quantization (2019)
- AdaRound (2020)
- BRECQ (2021)

---

## 23. Integer-only Inference Optimization

### Mô tả
Thiết kế inference pipeline hoàn toàn bằng integer arithmetic, không cần floating-point.

### Why Integer-only?
- Faster: Integer ops 2-4x faster than FP32
- Lower power: Integer units consume less energy
- Simpler hardware: No FPU needed

### Challenges
```
Typical Neural Network:
Conv → BatchNorm → ReLU → ... → Softmax
  │        │                        │
  └── Needs FP for normalization ───┘

Solution: Fuse BN into Conv, approximate Softmax
```

### Integer Operations
```
Affine quantization: x_int = round(x * scale) + zero_point
Computation: y_int = x_int * w_int
Requantization: Adjust scale for next layer
```

### Đọc thêm
- Quantization and Training of DNNs (Google, 2018)
- TFLite Quantization

---

## 24. Quantization-friendly Neural Network Design

### Mô tả
Thiết kế network architectures từ đầu để chúng dễ quantize hơn.

### Design Principles
1. **Avoid large dynamic range**: Easier to quantize
2. **Use ReLU over other activations**: Better clipping behavior
3. **Uniform layer widths**: Consistent quantization
4. **Avoid skip connections with different precisions**: Matching issues

### Quantization-friendly vs Unfriendly
```
Unfriendly:                    Friendly:
├── Swish activation           ├── ReLU activation
├── Squeeze-and-Excitation     ├── Simple residual
├── Deep narrow layers         ├── Balanced layers
└── Large softmax              └── Temperature-scaled softmax
```

### Đọc thêm
- Searching for Quantization-friendly Architectures (2020)

---

## 25. On-chip Quantization Calibration

### Mô tả
Perform calibration và fine-tuning của quantization parameters directly trên deployed device.

### Motivation
- Lab calibration data ≠ deployment data distribution
- Device-specific characteristics affect optimal quantization
- Enable continuous adaptation

### On-chip Process
```
Deployed Device:
1. Collect small calibration buffer
2. Compute optimal scales/zero-points
3. Update quantization parameters
4. Continue inference with new params
```

### Challenges
- Limited compute for calibration
- Limited memory for storing calibration data
- Need to maintain service during calibration

### Đọc thêm
- On-chip Hardware-aware Quantization (2023)

---

## 26. Gradient Quantization for Distributed Training

### Mô tả
Quantize gradients trong distributed training để reduce communication overhead.

### Communication Bottleneck
```
Worker 1 ──┐
Worker 2 ──┼──→ Parameter Server ──→ Updated Weights
Worker 3 ──┘         │
    ↑                │
    └── Gradients (large!) ──┘
```

### Gradient Compression
| Method | Compression | Accuracy Impact |
|--------|-------------|-----------------|
| 1-bit SGD | 32x | Low (with error feedback) |
| TernGrad | ~16x | Low |
| Top-K | Variable | Low with large K |
| Random-K | Variable | Medium |

### Error Feedback
```python
# Accumulate quantization error
error_buffer += gradient - quantize(gradient)
# Apply error to next gradient
next_gradient += error_buffer
```

### Đọc thêm
- 1-bit SGD (Microsoft, 2014)
- Deep Gradient Compression (2018)

---

## 27. Activation Quantization vs Weight Quantization Trade-offs

### Mô tả
Phân tích và tối ưu trade-offs giữa quantizing weights vs activations.

### Comparison
| Aspect | Weight Quantization | Activation Quantization |
|--------|--------------------|-----------------------|
| Memory saving | Model size | Runtime memory |
| Computation | Weight-stationary speedup | Both inputs quantized |
| Sensitivity | Usually less sensitive | More sensitive |
| Range | Static | Dynamic (input-dependent) |

### Mixed Strategy
```
Conservative:  W8A8  (8-bit weights, 8-bit activations)
Moderate:      W4A8  (more weight compression)
Aggressive:    W4A4  (maximum compression)
Ultra:         W2A8  (extreme weight compression)
```

### Hardware Implications
- Weight quantization: Reduce model loading time
- Activation quantization: Reduce memory bandwidth during compute
- Joint: Maximum efficiency but careful tuning needed

### Đọc thêm
- Trained Ternary Quantization (2017)
- PACT: Parameterized Clipping Activation (2018)

---

## 📚 Quantization Toolbox

### Frameworks
| Framework | Features |
|-----------|----------|
| **PyTorch Quantization** | Dynamic, static, QAT |
| **TensorFlow Lite** | Post-training, QAT |
| **NVIDIA TensorRT** | INT8 calibration |
| **ONNX Runtime** | Cross-platform quantization |

### Common Workflow
```
1. Train FP32 model
2. Analyze sensitivity
3. Choose quantization strategy
4. Calibrate or QAT
5. Validate accuracy
6. Deploy
```
