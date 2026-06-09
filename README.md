# 📄 Custom Vietnamese OCR Engine for IBM Docling

> **Project Description:** A high-performance, self-trained OCR pipeline customized for IBM's Docling library. Specifically engineered to accurately parse structurally complex, scanned Vietnamese legal documents, and highly optimized for CPU-only environments.

## ✨ Key Features & Technical Highlights

* **🛠️ Core Library Customization**
  Engineered a custom **OCR Adapter layer** to successfully override Docling's default extraction engine. This seamlessly embeds a specialized recognition workflow directly into the native document parsing pipeline.

* **👁️ Dual-Stage Computer Vision Pipeline**
  Combined **YOLOv8** for precise document layout analysis (text & table zone detection) with an ultra-lightweight **CRNN** model. Fine-tuned specifically for Vietnamese typography, achieving **98% accuracy** in diacritic-heavy character recognition.

* **⚡ Hardware & Inference Optimization**
  Optimized model topology to run smoothly on non-GPU and hardware-constrained CPU environments. This architecture yields a **40% reduction in RAM/CPU overhead** compared to standard engines like EasyOCR or Tesseract.

* **📑 Structure & Topology Preservation**
  Secured pristine **Markdown outputs** by preventing alignment drift and table cellular fragmentation in high-density scanned PDFs. This establishes a solid, high-fidelity data foundation for downstream **Advanced RAG and Graph RAG systems**.
* ## ⚙️ Prerequisites

- **OS:** Ubuntu / Windows
- **Python:** 3.9 or higher
- **Hardware:** CPU-only environments are fully supported and optimized.

## 🚀 Installation
**1. Clone the repository**
```bash
git clone [https://github.com/duongmanh27/CUSTOM-VIETNAMESE-OCR-ENGINE-FOR-IBM-DOCLING.git](https://github.com/duongmanh27/CUSTOM-VIETNAMESE-OCR-ENGINE-FOR-IBM-DOCLING.git)
cd CUSTOM-VIETNAMESE-OCR-ENGINE-FOR-IBM-DOCLING
```

**2. Set up a virtual environment (Recommended)**
```bash
python -m venv venv
source venv/bin/activate
```
**3. Install dependencies:**
Install the required Python packages (including PyTorch for CPU, Ultralytics, and IBM Docling):
```bash
pip install -r requirements.txt
```
**4. Download and Extract Model Weights:**
The custom OCR pipeline relies on fine-tuned YOLOv8 and CRNN models. Due to GitHub's file size limit, the compressed weights are hosted on Google Drive.

Access this [Google Drive Folder](https://drive.google.com/drive/folders/1Qozy22D0TJZuSCSskoRQo-gU0sssL7ri?usp=sharing) to download the `weight.zip` file.

Place the downloaded `weight.zip` file directly into the root directory of this project.

Extract the archive using the following commands:
```bash
unzip weight.zip
```
## 📬 Contact & Weights Password

The pre-trained model weights (`weight.zip`) are password-protected to prevent unauthorized distribution. 

To obtain the **FREE** extraction password, or if you have any questions regarding this project, please feel free to reach out to me:
* **📧 Email:** [duongmanh608@gmail.com](mailto:duongmanh608@gmail.com)
* 