# 📚 Learning Roadmap - Hardware-aware AI

> **Personalized cho bạn**  
> **Cập nhật**: 12/2024

---

## ✅ Kiến Thức Đã Có

| Môn | Status | Ứng dụng |
|-----|--------|----------|
| Ma trận (Linear Algebra) | ✅ Đã học | Neural networks, quantization |
| Giải tích, Vi tích phân | ✅ Đã học | Backpropagation, optimization |
| Xác suất thống kê | ✅ Đã học | ML foundations |
| C++ | ✅ Đã học | Embedded, hardware interface |
| Python | ✅ Đã học | ML frameworks |
| Cấu trúc dữ liệu | ✅ Đã học | Algorithms |

**→ Nền tảng tốt! Có thể bắt đầu ngay với ML.**

---

## 🎯 Hướng Đi Phù Hợp Nhất

| Hướng | Độ phù hợp | Cần học thêm |
|-------|-----------|--------------|
| **TinyML/Edge AI** | ⭐⭐⭐⭐⭐ | ML + Embedded |
| **Model Compression** | ⭐⭐⭐⭐⭐ | ML only |
| **Neuromorphic** | ⭐⭐⭐⭐ | + Neuroscience basics |
| **Bio-inspired** | ⭐⭐⭐⭐ | + Neuroscience |
| **CIM/ReRAM** | ⭐⭐⭐ | + Electronics/Circuits |
| **Quantum ML** | ⭐⭐⭐ | + Quantum Mechanics |
| **Photonic** | ⭐⭐ | + Physics (Optics) |

---

## 🗺️ Lộ Trình 6 Tháng

### Phase 1: Machine Learning (Tháng 1-2)

```
Tuần 1-2: PyTorch Fundamentals
├── Tensors, autograd, nn.Module
├── Dataset, DataLoader
└── 🔗 pytorch.org/tutorials

Tuần 3-4: Neural Networks
├── MLP → MNIST classification
├── CNN → CIFAR-10 classification
├── Loss functions, optimizers
└── 🔗 Course: Fast.ai (practical)

Tuần 5-6: Training Techniques
├── Regularization (dropout, batch norm)
├── Learning rate scheduling
├── Data augmentation
└── 🎯 Goal: Train ResNet-18 on CIFAR-10

Tuần 7-8: Modern Architectures
├── Transformers, Attention mechanism
├── Vision Transformer (ViT) basics
└── 🔗 Course: Karpathy "Let's build GPT"
```

**📚 Resources:**
- [Fast.ai](https://course.fast.ai/) - FREE, practical
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [Andrej Karpathy YouTube](https://www.youtube.com/@AndrejKarpathy)

---

### Phase 2: Hardware & Optimization (Tháng 3-4)

```
Tuần 9-10: Computer Architecture
├── Memory hierarchy (Cache, DRAM)
├── Latency vs bandwidth
├── GPU architecture basics
└── 🔗 Book: Patterson & Hennessy Ch.1-5

Tuần 11-12: Model Compression Basics
├── Quantization (FP32 → INT8)
├── Pruning (structured, unstructured)
├── Knowledge distillation
└── 🔗 PyTorch quantization tutorial

Tuần 13-14: Hands-on Compression
├── Quantize your ResNet-18
├── Prune 50% weights
├── Measure speedup
└── 🎯 Goal: 2-4x smaller model, <2% accuracy loss

Tuần 15-16: Profiling & Analysis
├── torch.profiler
├── Memory usage analysis
├── Latency breakdown
└── Compare FP32 vs INT8 performance
```

**📚 Resources:**
- [PyTorch Quantization](https://pytorch.org/docs/stable/quantization.html)
- [Neural Network Distiller](https://nervanasystems.github.io/distiller/)
- Book: "Computer Organization and Design" (Patterson)

---

### Phase 3: Specialization (Tháng 5-6)

**Chọn 1 trong 2 track:**

#### Track A: TinyML/Edge AI 📱

```
Tuần 17-18: TensorFlow Lite
├── Convert PyTorch → TFLite
├── INT8 quantization for mobile
└── 🔗 tensorflow.org/lite

Tuần 19-20: Edge Deployment
├── Deploy on Raspberry Pi
├── hoặc ESP32/Arduino
├── Real-time inference
└── 🔗 Edge Impulse tutorials

Tuần 21-22: Optimization
├── Profile on device
├── Memory optimization
├── Latency optimization
└── 🎯 Goal: <100ms inference on edge

Tuần 23-24: Project
├── Build complete edge AI application
├── Object detection hoặc voice recognition
└── Document & share on GitHub
```

#### Track B: Neuromorphic Computing 🧠

```
Tuần 17-18: Spiking Neural Networks
├── LIF neuron model
├── snnTorch framework
└── 🔗 snntorch.readthedocs.io

Tuần 19-20: SNN Training
├── Surrogate gradient method
├── Train SNN on MNIST
├── Compare with ANN
└── 🔗 Tutorials on snnTorch

Tuần 21-22: Neuromorphic Concepts
├── Event-driven processing
├── STDP learning rule
├── Neuromorphic datasets (N-MNIST)
└── 🔗 Intel Lava framework

Tuần 23-24: Project
├── SNN for gesture recognition / keyword spotting
├── Compare energy vs ANN
└── Document & share
```

---

## 📅 Weekly Schedule Template

```
Mỗi tuần (10-15 giờ):

Thứ 2-3: Theory (2-3h)
├── Đọc papers/tutorials
└── Watch lectures

Thứ 4-5: Coding (4-5h)
├── Implement concepts
└── Run experiments

Thứ 6-7: Project (3-4h)
├── Apply to personal project
└── Debug, iterate

Chủ nhật: Review (1-2h)
├── Summarize learnings
└── Plan next week
```

---

## 🛠️ Tools Setup

### Environment Setup (Do This First!)

```bash
# 1. Install Miniconda
# Download from: https://docs.conda.io/en/latest/miniconda.html

# 2. Create environment
conda create -n hwai python=3.10
conda activate hwai

# 3. Install PyTorch
pip install torch torchvision torchaudio

# 4. Install tools
pip install numpy matplotlib jupyter
pip install tensorboard wandb  # logging

# 5. (Optional) TinyML tools
pip install tensorflow tflite-runtime

# 6. (Optional) Neuromorphic
pip install snntorch
```

---

## 📊 Progress Tracker

### Phase 1: Machine Learning
- [ ] PyTorch basics completed
- [ ] MLP on MNIST (>98% acc)
- [ ] CNN on CIFAR-10 (>85% acc)
- [ ] Understand Transformers
- [ ] ResNet-18 trained from scratch

### Phase 2: Hardware & Optimization
- [ ] Understand memory hierarchy
- [ ] INT8 quantization implemented
- [ ] Pruning implemented
- [ ] Model size reduced 2-4x
- [ ] Profiling completed

### Phase 3: Specialization
- [ ] Track chosen: ____________
- [ ] Framework learned
- [ ] First project completed
- [ ] GitHub repo published
- [ ] (Optional) Blog post written

---

## 📚 Essential Resources

### Courses (Free)

| Course | Platform | Focus |
|--------|----------|-------|
| Fast.ai | fast.ai | Practical DL |
| CS231n | YouTube | CNNs |
| Let's build GPT | YouTube | Transformers |
| TinyML | edX | Edge AI |

### Books

| Book | Focus | Priority |
|------|-------|----------|
| "Deep Learning" (Goodfellow) | Theory | Medium |
| "Dive into DL" (d2l.ai) | Practical | High |
| "TinyML" (O'Reilly) | Edge AI | High (if Track A) |

### Communities

- **Discord**: ML Collective
- **Reddit**: r/MachineLearning, r/learnmachinelearning
- **Twitter/X**: Follow researchers

---

## 🎯 6-Month Milestones

| Month | Milestone | Deliverable |
|-------|-----------|-------------|
| 1 | PyTorch proficiency | CIFAR-10 CNN |
| 2 | Modern architectures | Transformer implementation |
| 3 | Compression basics | Quantized model |
| 4 | Optimization skills | 4x compressed model |
| 5 | Specialization | Track-specific project |
| 6 | Complete project | GitHub + Documentation |

---

**Bắt đầu ngay với Phase 1, Tuần 1: PyTorch Fundamentals! 🚀**

*Tip: Đặt reminder học mỗi ngày, consistency > intensity*
