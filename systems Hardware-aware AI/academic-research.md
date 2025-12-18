# Nghiên Cứu Học Thuật: Hardware-aware AI

> **Ngày cập nhật**: 2025-12-18  
> **Phạm vi**: Tổng hợp các bài báo và nghiên cứu học thuật 2023-2024

---

## 📑 Mục Lục

1. [Survey Papers quan trọng](#1-survey-papers-quan-trọng)
2. [Neural Architecture Search (NAS)](#2-neural-architecture-search-nas)
3. [Quantization-aware Training](#3-quantization-aware-training)
4. [TinyML & Edge AI](#4-tinyml--edge-ai)
5. [Hardware Accelerators](#5-hardware-accelerators)
6. [Các hướng nghiên cứu mới](#6-các-hướng-nghiên-cứu-mới)

---

## 1. Survey Papers Quan Trọng

### 1.1 Hardware-Aware Neural Architecture Search: Survey and Taxonomy
- **Venue**: IJCAI (International Joint Conference on Artificial Intelligence)
- **Nội dung chính**:
  - Phân loại taxonomy của HW-NAS
  - Đánh giá các chiến lược ước tính chi phí phần cứng
  - Xây dựng mô hình DL hiệu quả đáp ứng ràng buộc latency và năng lượng
  - Trade-off giữa accuracy và deployability trên các platform khác nhau

### 1.2 A Survey on Deep Learning Hardware Accelerators for Heterogeneous HPC Platforms
- **Timeline**: Submitted 06/2023, Major Revision 07/2024, Accepted for 03/2025
- **Nội dung chính**:
  - Tổng hợp các accelerator cho HPC applications
  - Các loại accelerator: GPU-based, TPU, FPGA-based, ASIC-based
  - Neural Processing Units và co-processors trên RISC-V
  - Công nghệ mới: 3D-stacked Processor-In-Memory, RRAM, PCM, Neuromorphic

### 1.3 Empowering Edge Intelligence: A Comprehensive Survey on On-Device AI Models
- **Source**: arXiv, 03/2025
- **Nội dung chính**:
  - Tình trạng hiện tại, thách thức và xu hướng của on-device AI
  - NAS research tập trung vào hardware-aware optimization
  - Điều chỉnh neural architectures theo ràng buộc của edge devices

---

## 2. Neural Architecture Search (NAS)

### 2.1 NASH: Neural Architecture Search for Hardware-Optimized ML Models
- **Source**: arXiv, 03/2024
- **Đóng góp**:
  - Hardware-based architecture search algorithm
  - Sử dụng FINN open-source hardware compiler
  - Tối ưu cho FPGA với quantized neural networks
  - Tích hợp quantization vào training algorithm
  - Cải thiện accuracy và hardware resource utilization cho ResNet

### 2.2 QA-BWNAS: Scaling Up Quantization-Aware NAS for Efficient Deep Learning on Edge
- **Source**: arXiv, 01/2024
- **Đóng góp**:
  - Quantization-aware NAS cho large-scale tasks
  - Block-wise formulation để tìm kiếm architectures tối ưu
  - Kết quả cho semantic segmentation trên Cityscapes dataset
  - Models nhỏ hơn và nhanh hơn, không giảm performance

### 2.3 QuantNAS: Quantization-aware NAS for Efficient Mobile Deployment
- **Venue**: CVPR 2024 Workshops
- **Đóng góp**:
  - Two-stage one-shot approach
  - Tìm kiếm architecture từ fully quantized supernet
  - Cải thiện accuracy và giảm latency trên mobile CPUs

### 2.4 JAQ: Joint Efficient Architecture Design and Low-Bit Quantization
- **Source**: Tsinghua University
- **Đóng góp**:
  - JAQ Framework - đồng tối ưu neural network architectures, quantization precisions, và hardware accelerators
  - Giải quyết memory overhead và time-consuming hardware search
  - Higher accuracy và reduced hardware search time

### 2.5 An Affordable Hardware-Aware NAS for Ultra-Low-Power Computing Platforms
- **Timeline**: Expected 05/2024
- **Đóng góp**:
  - HW-NAS cho ultra-low-power microcontrollers
  - Tạo tiny CNNs với state-of-the-art classification accuracy
  - Quy trình tìm kiếm nhẹ có thể chạy trên embedded devices

---

## 3. Quantization-aware Training

### 3.1 On-Chip Hardware-Aware Quantization (OHQ)
- **Source**: arXiv, 09/2023
- **Đóng góp**:
  - Mixed-precision quantization trực tiếp trên deployed edge devices
  - Nhận biết actual hardware efficiency
  - Ước tính accuracy impact on-chip
  - Tối ưu bit-width configurations

### 3.2 Hardware-Aware Automated Quantization (HAQ) Framework
- **Timeline**: Prospective publication 06/2025
- **Đóng góp**:
  - Reinforcement learning để tự động xác định quantization policies
  - Tích hợp direct hardware feedback (latency và energy)
  - Hardware simulator trong design loop

### 3.3 HW-NAS for Quantized Neural Networks on FPGAs
- **Source**: Polytechnique Montréal Thesis, 12/2023
- **Đóng góp**:
  - Sửa đổi DARTS framework cho gradient-based NAS
  - Tìm kiếm accurate và low-latency QNNs
  - FPGA implementation sử dụng FINN environment
  - Tích hợp latency như optimization criterion
  - Giảm latency đáng kể với minimal accuracy drops

---

## 4. TinyML & Edge AI

### 4.1 Kỹ Thuật Tối Ưu Model

| Kỹ thuật | Mô tả | Mức độ nén |
|----------|-------|------------|
| **Pruning** | Loại bỏ connections/neurons ít quan trọng | 2-10x |
| **Quantization** | FP32 → INT8/INT4 | 2-8x memory |
| **Knowledge Distillation** | Student model học từ teacher | Variable |
| **NAS** | Tự động thiết kế lightweight models | Task-specific |
| **Operator Fusion** | Gộp nhiều phép tính thành kernel đơn | Reduce latency |

### 4.2 Hardware Platforms cho TinyML

| Platform | Đặc điểm | Use Cases |
|----------|----------|-----------|
| **ARM Cortex-M** | Low-power MCUs, KB RAM | Wearables, sensors |
| **ESP32-S3** | WiFi/BLE, AI acceleration | IoT applications |
| **Arduino** | Beginner-friendly | Prototyping |
| **STM32** | Industrial-grade | Edge computing |
| **GAP-8** | Parallel processing, CNN accelerator | Vision AI |

### 4.3 Frameworks & Tools

| Tool | Chức năng |
|------|-----------|
| **TensorFlow Lite Micro** | Lightweight TF cho embedded |
| **Edge Impulse** | End-to-end TinyML platform |
| **CMSIS-NN** | ARM optimized NN functions |
| **MCUNet** | Pre-trained super-networks |
| **Apache TVM** | Cross-platform compiler |
| **STM32Cube.AI** | STM32 optimization |

### 4.4 Ràng Buộc Tài Nguyên TinyML

```
┌──────────────────────────────────────────────────────────┐
│                   TINYML CONSTRAINTS                      │
├──────────────────────────────────────────────────────────┤
│  Memory:        < 1MB (typically 64KB - 256KB)           │
│  Clock Speed:   40 - 400 MHz                             │
│  Power:         Milliwatts or less                       │
│  Model Size:    < 100KB (target)                         │
│  Latency:       Real-time (< 100ms)                      │
└──────────────────────────────────────────────────────────┘
```

---

## 5. Hardware Accelerators

### 5.1 Phân Loại Accelerators

```
Hardware Accelerators
├── GPU-based
│   ├── NVIDIA CUDA cores
│   └── Tensor Cores (mixed precision)
├── TPU (Tensor Processing Unit)
│   ├── Google Cloud TPU
│   └── Edge TPU (Coral)
├── FPGA-based
│   ├── Xilinx (AMD)
│   └── Intel (Altera)
├── ASIC-based
│   ├── Neural Processing Units (NPU)
│   └── Custom accelerators
└── Emerging Technologies
    ├── 3D-stacked Processor-In-Memory
    ├── Non-volatile Memory (RRAM, PCM)
    ├── Neuromorphic Processors
    └── Multi-Chip Modules
```

### 5.2 Compute-in-Memory (CIM)

- **Vấn đề**: "Memory wall" - bottleneck giữa compute và memory
- **Giải pháp**: Tích hợp computing trực tiếp trong memory systems
- **Lợi ích**: 
  - Giảm data movement
  - Tăng energy efficiency
  - Phù hợp cho neural network operations (matrix multiplications)

### 5.3 Neuromorphic Computing

- **Ý tưởng**: Hardware mô phỏng cấu trúc và hoạt động của não bộ
- **Đặc điểm**:
  - Event-driven processing
  - Spiking neural networks (SNNs)
  - Ultra-low power consumption
- **Ví dụ**: Intel Loihi, IBM TrueNorth

---

## 6. Các Hướng Nghiên Cứu Mới

### 6.1 Hardware-Software Co-design

```
┌─────────────────────────────────────────────────────────────┐
│                    CO-DESIGN PARADIGM                        │
│                                                             │
│   ┌─────────────┐         ┌─────────────────┐               │
│   │   Software  │◄───────►│    Hardware     │               │
│   │   (Models)  │         │ (Accelerators)  │               │
│   └──────┬──────┘         └────────┬────────┘               │
│          │                         │                         │
│          ▼                         ▼                         │
│   ┌──────────────────────────────────────────┐              │
│   │           Compiler/Runtime               │              │
│   │    (Hardware-aware optimizations)        │              │
│   └──────────────────────────────────────────┘              │
│                         │                                    │
│                         ▼                                    │
│   ┌──────────────────────────────────────────┐              │
│   │      Performance/Energy/Accuracy         │              │
│   │           Feedback Loop                  │              │
│   └──────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Federated Learning on Edge

- **Mục tiêu**: Private on-device training
- **Thách thức**: 
  - Limited compute resources
  - Communication efficiency
  - Data heterogeneity
- **Giải pháp**: Hardware-aware federated optimization

### 6.3 Emerging Research Topics

| Topic | Mô tả | Potential Impact |
|-------|-------|------------------|
| **Tiny Deep Learning (TinyDL)** | Compressed DL models cho resource-constrained hardware | Democratize AI |
| **Photonic AI** | Light-based computing | Ultra-high speed, low energy |
| **DNA-based Computing** | Molecular computing | Massive parallelism |
| **Quantum ML** | Quantum speedup cho ML | Exponential speedup (theoretical) |

---

## 📊 Thống Kê Research Trends

### Papers theo năm (ước tính)

| Năm | HW-NAS | Quantization | TinyML | Total |
|-----|--------|--------------|--------|-------|
| 2021 | ~50 | ~80 | ~30 | ~160 |
| 2022 | ~80 | ~120 | ~60 | ~260 |
| 2023 | ~120 | ~180 | ~100 | ~400 |
| 2024 | ~180 | ~250 | ~150 | ~580 |

### Top Venues

- **Conferences**: NeurIPS, ICML, CVPR, ICCV, ICLR, DAC, HPCA
- **Journals**: TPAMI, TCAD, JSSC, Nature Electronics
- **Workshops**: MLSys, TinyML Summit, EfficientDL

---

## 🔗 Danh Sách Papers Tham Khảo

### Survey Papers
1. "Hardware-Aware Neural Architecture Search: Survey and Taxonomy" - IJCAI
2. "A Survey on Deep Learning Hardware Accelerators for HPC Platforms" - arXiv 2024
3. "Empowering Edge Intelligence: Survey on On-Device AI Models" - arXiv 2025

### NAS Papers
4. "NASH: Neural Architecture Search for Hardware-Optimized ML Models" - arXiv 2024
5. "QA-BWNAS: Scaling Up Quantization-Aware NAS" - arXiv 2024
6. "QuantNAS: Quantization-aware NAS for Mobile" - CVPR 2024 Workshops
7. "JAQ: Joint Architecture and Quantization" - Tsinghua University

### Quantization Papers
8. "On-Chip Hardware-Aware Quantization (OHQ)" - arXiv 2023
9. "HAQ: Hardware-Aware Automated Quantization" - ResearchGate

### TinyML Papers
10. "TinyML: Machine Learning with TensorFlow Lite" - O'Reilly
11. "MCUNet: Tiny Deep Learning on IoT Devices" - NeurIPS 2020
12. "Once-for-All: Train One Network for All" - ICLR 2020

---

## 📝 Ghi Chú Nghiên Cứu

### Câu hỏi nghiên cứu mở

1. Làm thế nào để tự động hóa hoàn toàn quá trình co-design?
2. Trade-off tối ưu giữa accuracy và efficiency là gì?
3. Generalization của HW-aware models qua các platforms?
4. Cách tích hợp emerging hardware (neuromorphic, CIM) vào ML frameworks?

### Potential research directions

- [ ] Hardware-aware training from scratch
- [ ] Cross-platform model optimization
- [ ] Energy-aware neural architecture search
- [ ] On-device learning with privacy guarantees

---

*Cập nhật lần cuối: 2025-12-18*
