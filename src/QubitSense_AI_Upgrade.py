# QubitSense AI: Quantum Kernel Intelligence Lab
# Upgrade for the existing SVC vs QSVC baseline.
# Run in Google Colab. This is a small, reproducible research prototype, not proof of quantum advantage.

%pip -q install "qiskit>=1.2" "qiskit-machine-learning>=0.8" scikit-learn matplotlib pandas

import time
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from qiskit.circuit.library import ZZFeatureMap, ZFeatureMap
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from qiskit_machine_learning.algorithms import QSVC

# ---------------------------
# 1. Experiment configuration
# ---------------------------
SEEDS = [21, 42, 73]        # use at least 3 repeatable splits
SAMPLES_PER_CLASS = 15      # small sample to keep simulation manageable
TEST_SIZE = 0.30
NOISE_STD = 0.10            # controlled Gaussian perturbation in PCA feature space
MAX_QUANTUM_TRAIN_SAMPLES = 32

iris = load_iris()
X_all, y_all = iris.data, iris.target
class_names = iris.target_names

rng = np.random.default_rng(2026)
selected = []
for cls in np.unique(y_all):
    ids = np.where(y_all == cls)[0]
    selected.extend(rng.choice(ids, size=SAMPLES_PER_CLASS, replace=False))
selected = np.array(selected)
X, y = X_all[selected], y_all[selected]
print(f"Dataset: Iris | {len(X)} selected samples | classes: {list(class_names)}")
print("Study design: repeated splits + kernel comparison + noisy-test robustness + circuit resources")

# ---------------------------
# 2. Model and metric helpers
# ---------------------------
def metrics(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision_macro": precision_score(y_true, y_pred, average="macro", zero_division=0),
        "recall_macro": recall_score(y_true, y_pred, average="macro", zero_division=0),
        "f1_macro": f1_score(y_true, y_pred, average="macro", zero_division=0),
    }

def make_quantum_model(map_name):
    if map_name == "ZZ reps=1":
        fmap = ZZFeatureMap(feature_dimension=2, reps=1, entanglement="linear")
    elif map_name == "ZZ reps=2":
        fmap = ZZFeatureMap(feature_dimension=2, reps=2, entanglement="linear")
    elif map_name == "Z reps=1":
        fmap = ZFeatureMap(feature_dimension=2, reps=1)
    else:
        raise ValueError(f"Unknown map: {map_name}")
    kernel = FidelityQuantumKernel(feature_map=fmap)
    return QSVC(quantum_kernel=kernel), fmap

model_specs = ["Classical RBF SVC", "Quantum ZZ reps=1", "Quantum ZZ reps=2"]
records = []
resource_records = []
per_seed_predictions = []

# ---------------------------
# 3. Repeated, matched experiments
# ---------------------------
for seed in SEEDS:
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=seed, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train_raw)
    X_test_s = scaler.transform(X_test_raw)

    pca = PCA(n_components=2, random_state=seed)
    X_train = pca.fit_transform(X_train_s)
    X_test = pca.transform(X_test_s)

    # Keep training set size bounded for quantum kernel cost.
    if len(X_train) > MAX_QUANTUM_TRAIN_SAMPLES:
        # deterministic stratified reduction
        keep_rng = np.random.default_rng(seed + 1000)
        keep = []
        for cls in np.unique(y_train):
            cls_ids = np.where(y_train == cls)[0]
            per_cls = max(1, MAX_QUANTUM_TRAIN_SAMPLES // len(np.unique(y_train)))
            keep.extend(keep_rng.choice(cls_ids, size=min(per_cls, len(cls_ids)), replace=False))
        keep = np.array(keep)
        X_train_q, y_train_q = X_train[keep], y_train[keep]
    else:
        X_train_q, y_train_q = X_train, y_train

    # Classical baseline uses all training samples.
    classical = SVC(kernel="rbf", C=1.0, gamma="scale")
    t0 = time.perf_counter()
    classical.fit(X_train, y_train)
    fit_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    pred = classical.predict(X_test)
    predict_s = time.perf_counter() - t0
    clean = metrics(y_test, pred)
    noisy_X_test = X_test + np.random.default_rng(seed + 500).normal(0, NOISE_STD, X_test.shape)
    noisy_pred = classical.predict(noisy_X_test)
    noisy = metrics(y_test, noisy_pred)
    records.append({"seed": seed, "model": "Classical RBF SVC", **clean,
                    "noisy_accuracy": noisy["accuracy"], "noisy_f1_macro": noisy["f1_macro"],
                    "fit_seconds": fit_s, "predict_seconds": predict_s,
                    "train_n": len(X_train), "quantum_train_n": np.nan})
    per_seed_predictions.append((seed, "Classical RBF SVC", y_test, pred))

    for map_name in ["ZZ reps=1", "ZZ reps=2"]:
        qmodel, fmap = make_quantum_model(map_name)
        t0 = time.perf_counter()
        qmodel.fit(X_train_q, y_train_q)
        q_fit_s = time.perf_counter() - t0
        t0 = time.perf_counter()
        q_pred = qmodel.predict(X_test)
        q_predict_s = time.perf_counter() - t0
        q_clean = metrics(y_test, q_pred)
        q_noisy_pred = qmodel.predict(noisy_X_test)
        q_noisy = metrics(y_test, q_noisy_pred)
        model_label = f"Quantum {map_name}"
        records.append({"seed": seed, "model": model_label, **q_clean,
                        "noisy_accuracy": q_noisy["accuracy"], "noisy_f1_macro": q_noisy["f1_macro"],
                        "fit_seconds": q_fit_s, "predict_seconds": q_predict_s,
                        "train_n": len(X_train), "quantum_train_n": len(X_train_q)})
        per_seed_predictions.append((seed, model_label, y_test, q_pred))

        # Circuit structure is a proxy for circuit complexity, not a performance score.
        decomposed = fmap.decompose(reps=2)
        ops = decomposed.count_ops()
        resource_records.append({
            "feature_map": map_name,
            "qubits": fmap.num_qubits,
            "depth_decomposed": decomposed.depth(),
            "gate_count_decomposed": sum(ops.values()),
            "gate_types": ", ".join(f"{k}:{v}" for k, v in sorted(ops.items()))
        })

# ---------------------------
# 4. Results and uncertainty
# ---------------------------
runs = pd.DataFrame(records)
print("\nPER-RUN RESULTS")
display(runs.round(4))

summary = runs.groupby("model").agg(
    accuracy_mean=("accuracy", "mean"),
    accuracy_std=("accuracy", "std"),
    f1_macro_mean=("f1_macro", "mean"),
    f1_macro_std=("f1_macro", "std"),
    noisy_accuracy_mean=("noisy_accuracy", "mean"),
    noisy_accuracy_std=("noisy_accuracy", "std"),
    fit_seconds_mean=("fit_seconds", "mean"),
    predict_seconds_mean=("predict_seconds", "mean")
).reset_index()

print("\nSUMMARY: mean and standard deviation across splits")
display(summary.round(4))

resources = pd.DataFrame(resource_records).drop_duplicates(subset=["feature_map"])
print("\nQUANTUM CIRCUIT RESOURCE INSPECTOR")
display(resources)

# ---------------------------
# 5. Simple evidence-based advisor
# ---------------------------
# This rule is descriptive, not a scientific proof of superiority.
best_row = summary.sort_values(["f1_macro_mean", "fit_seconds_mean"], ascending=[False, True]).iloc[0]
classical_row = summary[summary["model"] == "Classical RBF SVC"].iloc[0]
quantum_rows = summary[summary["model"].str.startswith("Quantum")]

print("\nQUBITSENSE ADVISOR")
print(f"Highest mean macro-F1 in these runs: {best_row['model']} ({best_row['f1_macro_mean']:.3f}).")
if len(quantum_rows) and quantum_rows["f1_macro_mean"].max() > classical_row["f1_macro_mean"] + 0.03:
    print("A quantum configuration showed a higher mean macro-F1 by more than 0.03 in this small experiment.")
    print("Treat this as a hypothesis to validate, not proof of quantum advantage.")
else:
    print("No quantum configuration exceeded the classical mean macro-F1 by more than 0.03 in this experiment.")
    print("The classical baseline may be the more practical choice for this dataset and setup.")
print("Always consider variability, runtime, sample size and hardware constraints before drawing conclusions.")

# ---------------------------
# 6. Visualizations
# ---------------------------
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
summary.plot(x="model", y=["accuracy_mean", "f1_macro_mean"], kind="bar", ax=axes[0])
axes[0].set_ylim(0, 1)
axes[0].set_title("Mean clean performance across splits")
axes[0].set_ylabel("Score")
axes[0].tick_params(axis="x", rotation=20)

summary.plot(x="model", y=["accuracy_mean", "noisy_accuracy_mean"], kind="bar", ax=axes[1])
axes[1].set_ylim(0, 1)
axes[1].set_title(f"Clean vs noisy-test accuracy (noise std={NOISE_STD})")
axes[1].set_ylabel("Accuracy")
axes[1].tick_params(axis="x", rotation=20)
plt.tight_layout()
plt.show()

plt.figure(figsize=(9, 4))
plt.bar(summary["model"], summary["fit_seconds_mean"])
plt.title("Mean model fit time (environment-specific)")
plt.ylabel("Seconds")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.show()

# ---------------------------
# 7. Save evidence for report/PPT
# ---------------------------
runs.to_csv("qubitsense_repeated_runs.csv", index=False)
summary.to_csv("qubitsense_summary.csv", index=False)
resources.to_csv("qubitsense_circuit_resources.csv", index=False)
print("\nSaved: qubitsense_repeated_runs.csv, qubitsense_summary.csv, qubitsense_circuit_resources.csv")

# Honest-claims checklist:
# - These are small-sample Iris experiments.
# - Noise is simulated by perturbing test features, not hardware noise.
# - Runtime is environment-specific; simulator runtime is not quantum hardware speed.
# - Repeated splits improve reliability but do not establish quantum advantage.
