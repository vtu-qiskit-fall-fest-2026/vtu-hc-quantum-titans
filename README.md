# Quantum Titans

**Team ID:** VTU-QFF-HC-0138 | **Tier:** Online

| Detail | Information |
|---|---|
| Team | Quantum Titans |
| Team ID | VTU-QFF-HC-0138 |
| Tier | Online |
| Repository | [vtu-hc-quantum-titans](https://github.com/vtu-qiskit-fall-fest-2026/vtu-hc-quantum-titans) |
| Organisation | [vtu-qiskit-fall-fest-2026](https://github.com/vtu-qiskit-fall-fest-2026) |
| Event | VTU-QFF Hackathon – VTU Qiskit Fall Fest 2026 |

## Team Members (GitHub IDs)

| Name | GitHub Username | Role |
|---|---|---|
| Abinaya S | [@Abinaya959](https://github.com/Abinaya959) | Team Lead |
| Afrin U | [@Afrin25007](https://github.com/Afrin25007) | Developer |

---

# QubitSense AI: Quantum Kernel Intelligence Lab

**Track:** Track 4 – Quantum + AI & ML  
**Team:** Quantum Titans  
**Team ID:** VTU-QFF-HC-0138

## 1. Problem Statement

Quantum machine-learning models are often evaluated using classification accuracy alone, which does not fully establish their reliability or practical usefulness. Developers need a reproducible way to compare quantum and classical models across predictive performance, stability, robustness to controlled input perturbations, and computational cost.

## 2. Proposed Solution

QubitSense AI is a Qiskit-based benchmarking framework that compares a classical Support Vector Classifier (SVC) with quantum-kernel Support Vector Classifiers (QSVC). It evaluates model performance across repeated data splits, tests sensitivity to controlled input perturbations, and examines quantum circuit resources.

The framework presents experimental evidence to help users understand the trade-offs between classical and quantum machine learning.

## 3. Key Features

- Classical RBF-kernel SVC versus quantum-kernel QSVC comparison
- Repeated experiments using multiple random seeds
- Accuracy, macro precision, macro recall, and macro F1-score
- Robustness evaluation using controlled test-input perturbations
- Quantum circuit resource analysis, including qubit count, circuit depth, and gate count
- Runtime measurements and evidence-based model comparison

## 4. Methodology

1. Load and preprocess the Iris dataset.
2. Scale the features and reduce the feature space to two principal components.
3. Train a classical RBF-kernel SVC.
4. Train quantum-kernel QSVC models using Qiskit feature maps.
5. Evaluate predictive performance across repeated train/test splits.
6. Compare performance on clean and perturbed test inputs.
7. Summarize measured performance and computational trade-offs.

## 5. Technology Stack

- Python
- Qiskit
- Qiskit Machine Learning
- scikit-learn
- NumPy and pandas
- Matplotlib
- Jupyter Notebook

## 6. Experimental Results

The results section will report the metrics obtained from the experiments actually executed by the team. Performance claims and conclusions should be supported by the generated result files.

## 7. Project Files

- `notebooks/QubitSense_AI_Upgrade.ipynb` – experimental notebook
- `src/QubitSense_AI_Upgrade.py` – Python implementation
- `results/` – experimental CSV files
- `docs/QubitSense_AI_Hackathon_PPT.pptx` – project presentation
- `requirements.txt` – Python dependencies

*Ensure these paths match the files uploaded to the repository.*

## 8. Presentation and Demo

**Project Presentation:** `docs/QubitSense_AI_Hackathon_PPT.pptx`

**YouTube Demo:** [Watch the QubitSense AI demonstration](https://youtu.be/_tjXQqSoTt4)

## 9. Reproducibility

Install the dependencies listed in `requirements.txt`, then run the notebook or Python script. Quantum simulation runtime depends on the execution environment.

## 10. Limitations

This project uses a small Iris dataset and simulated quantum kernels. Controlled input perturbations are not equivalent to physical quantum hardware noise. The project does not claim quantum advantage; it reports measured results and practical trade-offs.

## 11. Acknowledgements

This project uses open-source quantum computing and machine-learning libraries. AI assistance, if used, will be disclosed according to the hackathon rules.
