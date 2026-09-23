# Module 2 — Titanic Analytics

## Dataset

The classic Titanic dataset is loaded using Seaborn and saved as `titanic.csv` for offline use.

Initial shape:

- 891 rows
- 15 columns

After cleaning:

- 889 rows
- 14 columns

### Missing Values

| Column | Missing % | Treatment |
|---|---:|---|
| deck | 77.22% | Dropped |
| age | 19.87% | Median imputation |
| embarked | 0.22% | Rows dropped |
| embark_town | 0.22% | Rows dropped |

The `deck` column was dropped because most of its values were missing. `age` was median-imputed because it had a moderate amount of missing data. The two rows missing embarkation information were removed because they represented only a very small portion of the dataset.

---

## Exploratory Data Analysis

### Age

IQR analysis:

- Q1 = 22.0
- Q3 = 35.0
- IQR = 13.0
- Outliers = 65

The age boxplot shows several IQR-based outliers. These values were retained because they can represent valid passenger ages.

### Fare

- Mean = 32.0967
- Median = 14.4542
- Mode = 8.05
- Outliers = 114

Fare is right-skewed because the mean is considerably higher than the median. High fare values were retained because they can represent legitimate passenger fares.

---

## Survival Analysis

### Survival by Sex

- Female = 74.04%
- Male = 18.89%

Female passengers had a substantially higher observed survival rate than male passengers.

### Survival by Passenger Class

- 1st class = 62.62%
- 2nd class = 47.28%
- 3rd class = 24.24%

Observed survival decreased from first class to third class.

### Survival by Sex and Passenger Class

| Sex | Class | Survival Rate |
|---|---:|---:|
| Female | 1 | 96.74% |
| Female | 2 | 92.11% |
| Female | 3 | 50.00% |
| Male | 1 | 36.89% |
| Male | 2 | 15.74% |
| Male | 3 | 13.54% |

Combining sex and passenger class reveals stronger differences in survival than considering either variable separately.

Boolean masking using `&` and `|` was also demonstrated for specific passenger groups.

---

## Correlation Analysis

The correlation matrix uses exactly:

- `survived`
- `pclass`
- `age`
- `sibsp`
- `parch`
- `fare`

Strongest absolute correlations:

- `pclass` and `fare` = -0.5482
- `sibsp` and `parch` = 0.4145

A correlation heatmap was generated to visualize these relationships.

---

## Standardization Check

Age and fare were standardized as an exploratory check.

Before standardization:

- Age mean = 29.3152
- Age std = 12.9849
- Fare mean = 32.0967
- Fare std = 49.6975

After standardization, both variables had approximately:

- Mean = 0
- Standard deviation = 1

This was only an exploratory check and was not used as a separate modeling input.

---

# Classification Modeling

The data was split using an 80/20 stratified train-test split.

- Training = 712 rows
- Testing = 179 rows

Training target distribution:

- Not survived = 61.66%
- Survived = 38.34%

Train-only preprocessing was implemented using `ColumnTransformer` and `Pipeline`.

Models evaluated:

- Logistic Regression
- Decision Tree
- Random Forest

## Model Comparison

| Model | Accuracy | Precision | Recall | F1 | AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.8045 | 0.7931 | 0.6667 | 0.7244 | 0.8437 |
| Decision Tree | 0.8156 | 0.7903 | 0.7101 | 0.7489 | 0.7904 |
| Random Forest | 0.8156 | 0.8000 | 0.6957 | 0.7442 | 0.8287 |

The three models produced similar accuracy. Logistic Regression had the highest AUC among the initial models, while Decision Tree and Random Forest achieved higher accuracy.

Confusion matrices and ROC curves were generated for the classification models.

---

# Class Imbalance

Three approaches were compared:

| Method | Precision | Recall | F1 |
|---|---:|---:|---:|
| Baseline | 0.7931 | 0.6667 | 0.7244 |
| Class Weight Balanced | 0.7297 | 0.7826 | 0.7525 |
| SMOTE | 0.7397 | 0.7826 | 0.7606 |

Class weighting and SMOTE increased recall compared with the baseline. SMOTE produced the highest F1 among the three approaches.

SMOTE was applied only to the training data.

---

# Random Forest Grid Search

GridSearchCV was used for Random Forest.

Best parameters:

```text
max_depth = 5
max_features = sqrt
n_estimators = 100