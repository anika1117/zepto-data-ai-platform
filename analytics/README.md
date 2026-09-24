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

Female passengers had a substantially higher observed survival rate than male passengers. The survival rate for females was 74.04%, compared with 18.89% for males. This shows a strong relationship between sex and survival in the Titanic dataset.

### Survival by Passenger Class

- 1st class = 62.62%
- 2nd class = 47.28%
- 3rd class = 24.24%

Passengers in higher passenger classes had higher survival rates. The survival rate was 62.62% for first class, 47.28% for second class, and 24.24% for third class. This indicates that passenger class was associated with survival outcomes.

### Survival by Sex and Passenger Class

| Sex | Class | Survival Rate |
|---|---:|---:|
| Female | 1 | 96.74% |
| Female | 2 | 92.11% |
| Female | 3 | 50.00% |
| Male | 1 | 36.89% |
| Male | 2 | 15.74% |
| Male | 3 | 13.54% |

Survival varied across both sex and passenger class. Female passengers in first and second class had survival rates above 90%, while male passengers in second and third class had much lower survival rates. This combined view shows that sex and passenger class together provide a clearer picture of the survival differences.

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

The correlation heatmap shows that the two strongest absolute correlations were between pclass and fare (-0.5482) and between sibsp and parch (0.4145). The negative pclass-fare relationship indicates that passenger class and fare were inversely related, while the positive sibsp-parch relationship indicates that passengers with more siblings or spouses aboard also tended to have more parents or children aboard. These relationships help describe the structure of the passenger data.

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
| Logistic Regression | 0.8090 | 0.7833 | 0.6912 | 0.7344 | 0.8610 |
| Decision Tree | 0.7697 | 0.6901 | 0.7206 | 0.7050 | 0.7541 |
| Random Forest | 0.8202 | 0.7813 | 0.7353 | 0.7576 | 0.8179 |

### Final Classifier Recommendation

Based on the observed test-set metrics, Logistic Regression achieved an accuracy of 0.8090, precision of 0.7833, recall of 0.6912, F1 score of 0.7344, and AUC of 0.8610. Decision Tree achieved an accuracy of 0.7697, precision of 0.6901, recall of 0.7206, F1 score of 0.7050, and AUC of 0.7541, while Random Forest achieved an accuracy of 0.8202, precision of 0.7813, recall of 0.7353, F1 score of 0.7576, and AUC of 0.8179. For deployment, the Random Forest pipeline provides the highest accuracy and F1 score among the three initial classifiers while maintaining a strong balance across the other reported metrics. The final fitted pipeline was saved with Joblib and verified by reloading it and generating a prediction on raw input.

## Class Imbalance

Three approaches were compared:

| Method | Precision | Recall | F1 |
|---|---:|---:|---:|
| Baseline | 0.7833 | 0.6912 | 0.7344 |
| Class Weight Balanced | 0.7183 | 0.7500 | 0.7338 |
| SMOTE | 0.7353 | 0.7353 | 0.7353 |

Class weighting and SMOTE increased recall compared with the baseline. SMOTE produced the highest F1 among the three imbalance approaches in this experiment.

SMOTE was applied only to the training data.

## Random Forest Grid Search

GridSearchCV was used for Random Forest.

Best parameters:

- `max_depth` = 5
- `max_features` = sqrt
- `n_estimators` = 200

Best cross-validation F1 = 0.7408

The Random Forest was configured with `oob_score=True`. The resulting OOB score was 0.8214.

## Regression Side Task

A multivariate linear regression model was used to predict `fare` from the available features.

- MAE = 21.0986
- RMSE = 41.7021
- R² = 0.3482
- Adjusted R² = 0.3091

A residual plot was generated to examine the relationship between residuals and fitted values. The residual spread shows some variation across fitted values, indicating mild heteroscedasticity.
