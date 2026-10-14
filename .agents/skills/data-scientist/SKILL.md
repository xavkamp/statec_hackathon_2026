---
name: data-scientist
description: >
  Expert data science workflows covering the full analytical pipeline: exploratory data analysis (EDA),
  data cleaning and transformation, statistical modeling, machine learning, and result communication.
  Use this skill whenever the user mentions datasets, CSVs, dataframes, model training, feature engineering,
  statistical tests, data visualization, or asks to "analyze", "predict", "cluster", "classify", or
  "find patterns" in data — even if they don't use the phrase "data science". Also trigger for tasks
  involving pandas, numpy, scikit-learn, matplotlib, seaborn, plotly, or similar libraries.
  When someone uploads a data file and wants insight from it, always use this skill.
---

# Data Scientist Skill

A skill for end-to-end data science work: from raw data to insight to production-ready output.

---

## Workflow Overview

Follow this pipeline, skipping stages that don't apply:

1. **Understand the Goal** — clarify the business or research question
2. **Load & Inspect** — read data, check shape, types, sample rows
3. **EDA** — distributions, correlations, outliers, class balance
4. **Clean & Transform** — missing values, encoding, scaling, feature engineering
5. **Model / Analyze** — choose the right method; fit, evaluate, iterate
6. **Communicate** — clear charts, tables, and plain-language interpretation
7. **Deliver** — notebook, script, or report as appropriate

---

## Stage 1 — Understand the Goal

Before touching data, pin down:
- **Task type**: prediction, classification, clustering, anomaly detection, statistical test, EDA only?
- **Target variable** (if supervised): what are we predicting?
- **Success metric**: accuracy, RMSE, AUC, p-value, business KPI?
- **Constraints**: interpretability required? Real-time inference? Specific libraries?

If the user hasn't specified, ask one focused question — don't interrogate them.

---

## Stage 2 — Load & Inspect

```python
import pandas as pd
import numpy as np

df = pd.read_csv("data.csv")          # adjust for .xlsx, .parquet, .json, etc.

# Always run these first
print(df.shape)
print(df.dtypes)
print(df.head())
print(df.describe(include="all"))
print(df.isnull().sum())
print(df.duplicated().sum())
```

Report findings concisely: rows × columns, numeric vs. categorical cols, % missing per column, obvious anomalies.

---

## Stage 3 — Exploratory Data Analysis (EDA)

### Univariate
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Numeric distributions
df.hist(figsize=(12, 8), bins=30)
plt.tight_layout(); plt.show()

# Categorical frequencies
for col in df.select_dtypes("object").columns:
    print(df[col].value_counts().head(10))
```

### Bivariate / Multivariate
```python
# Correlation heatmap
sns.heatmap(df.corr(numeric_only=True), annot=True, fmt=".2f", cmap="coolwarm")

# Pairplot (use sparingly on large datasets)
sns.pairplot(df, hue="target_col")   # replace target_col

# Target vs features (classification)
for col in numeric_cols:
    sns.boxplot(x="target_col", y=col, data=df)
    plt.show()
```

### Key things to flag
- Skewed distributions → consider log transform
- High-cardinality categoricals → consider target encoding or grouping rare levels
- Multicollinearity (|r| > 0.85) → consider dropping one
- Class imbalance → flag for modeling stage

---

## Stage 4 — Clean & Transform

### Missing values
```python
# Drop columns > 50% missing
threshold = 0.5
df = df.loc[:, df.isnull().mean() < threshold]

# Impute numeric with median (robust to outliers)
from sklearn.impute import SimpleImputer
num_imputer = SimpleImputer(strategy="median")

# Impute categorical with mode
cat_imputer = SimpleImputer(strategy="most_frequent")
```

### Encoding
```python
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

# Low cardinality (< 10 levels): one-hot
pd.get_dummies(df, columns=["col_name"], drop_first=True)

# High cardinality or ordinal: label encode or target encode
```

### Scaling
```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# StandardScaler for most ML algorithms
# MinMaxScaler for neural nets or distance-based methods
```

### Feature engineering hints
- Date columns → extract year, month, day_of_week, is_weekend
- Text columns → TF-IDF, embeddings, or basic length/word-count features
- Interaction terms for domain-specific combos
- Binning continuous vars when business buckets are meaningful

### Train/test split — always do this before fitting
```python
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y  # drop stratify for regression
)
```

---

## Stage 5 — Model / Analyze

### Supervised Learning

#### Quick-start model selection
| Task | First try | If you need more |
|------|-----------|-----------------|
| Binary classification | `LogisticRegression` | `RandomForestClassifier`, `XGBClassifier` |
| Multiclass | `RandomForestClassifier` | `GradientBoostingClassifier` |
| Regression | `Ridge` | `RandomForestRegressor`, `XGBRegressor` |
| Time series | Holt-Winters / statsmodels ARIMA | Prophet, LSTM |

#### Evaluation
```python
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,  # classification
    mean_absolute_error, mean_squared_error, r2_score         # regression
)

# Always evaluate on held-out test set, not training set
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))  # or regression metrics
```

#### Cross-validation
```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5, scoring="roc_auc")
print(f"CV AUC: {scores.mean():.3f} ± {scores.std():.3f}")
```

#### Hyperparameter tuning
```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

# RandomizedSearchCV is faster for large grids
search = RandomizedSearchCV(model, param_distributions, n_iter=50,
                             cv=5, scoring="roc_auc", n_jobs=-1)
search.fit(X_train, y_train)
print(search.best_params_)
```

### Unsupervised Learning

#### Clustering
```python
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score

# Elbow method to pick k
inertias = [KMeans(n_clusters=k, random_state=42).fit(X_scaled).inertia_
            for k in range(2, 11)]
plt.plot(range(2, 11), inertias, "bo-")

# Evaluate cluster quality
labels = KMeans(n_clusters=k_optimal).fit_predict(X_scaled)
print(silhouette_score(X_scaled, labels))
```

#### Dimensionality reduction
```python
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

pca = PCA(n_components=0.95)  # keep 95% variance
X_reduced = pca.fit_transform(X_scaled)
```

### Statistical Tests

| Question | Test |
|----------|------|
| Two group means different? | `scipy.stats.ttest_ind` |
| Multiple groups? | `scipy.stats.f_oneway` (ANOVA) |
| Relationship between categoricals? | `scipy.stats.chi2_contingency` |
| Data normal? | `scipy.stats.shapiro` (n<5000) |
| Non-parametric two groups? | `scipy.stats.mannwhitneyu` |

Always check assumptions before applying a test. Report effect size alongside p-value.

---

## Stage 6 — Communicate Results

### Guiding principles
- Lead with the answer to the business question, then support with numbers
- One chart = one idea; label axes, include units, add a title
- Report uncertainty: confidence intervals, std dev, or CV score spread
- Avoid jargon; explain what "AUC = 0.87" means in plain language

### Standard result template
```
## Key Findings
1. [Most important finding — business language]
2. [Second finding]
3. [Third finding]

## Model Performance
- Metric: value (benchmark / baseline: value)
- Interpretation: [what this means in context]

## Caveats & Next Steps
- [Data limitations]
- [Recommended follow-up analysis]
```

### Visualization best practices
```python
# Use a clean style
plt.style.use("seaborn-v0_8-whitegrid")
COLORS = ["#2563EB", "#DC2626", "#16A34A", "#CA8A04"]  # accessible palette

# Always save figures at high resolution for reports
fig.savefig("output.png", dpi=150, bbox_inches="tight")
```

---

## Stage 7 — Deliver

| Deliverable | Format |
|-------------|--------|
| Exploratory analysis | Markdown summary + saved figures |
| Reproducible analysis | `.py` script or Jupyter-style code blocks |
| Report for stakeholders | `.docx` (use docx skill) or `.pdf` (use pdf skill) |
| Dashboard | React artifact (use frontend-design skill) |
| Trained model | `joblib.dump(model, "model.pkl")` |

---

## Common Pitfalls — Always Avoid

- **Data leakage**: never fit scalers/encoders on the full dataset before splitting
- **Ignoring class imbalance**: check `y.value_counts()` early; use `class_weight="balanced"` or oversample
- **Reporting train set metrics**: always evaluate on held-out test data
- **Overfitting**: use cross-validation; compare train vs. test performance
- **p-hacking**: pre-register your hypothesis; apply multiple-testing correction (Bonferroni, BH)
- **Unlabeled axes**: every chart must have labeled axes, a title, and units

---

## Quick-Reference: Useful Libraries

| Library | Use |
|---------|-----|
| `pandas` | data manipulation |
| `numpy` | numerical ops |
| `matplotlib` / `seaborn` | static charts |
| `plotly` | interactive charts |
| `scikit-learn` | ML models, preprocessing, metrics |
| `xgboost` / `lightgbm` | gradient boosting |
| `scipy.stats` | statistical tests |
| `statsmodels` | regression with statistics output |
| `imbalanced-learn` | handling class imbalance |
| `shap` | model explainability |
| `joblib` | model serialization |
