import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from imblearn.over_sampling import SMOTE
from sklearn.tree import plot_tree
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_curve,
    roc_auc_score
)

df=pd.read_csv("analytics/titanic.csv")
print("Dataset shape:")
print(df.shape)
print("\nMissing values:")
print(df.isnull().sum())
X=df.drop(columns=["survived"])
y=df["survived"]
X_train, X_test, y_train, y_test=train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
print("\nTraining shape:")
print(X_train.shape)
print("\nTesting shape:")
print(X_test.shape)
print("\nTraining target distribution:")
print(y_train.value_counts(normalize=True))
print("\nTesting target distribution:")
print(y_test.value_counts(normalize=True))
numeric_features=[
    "pclass",
    "age",
    "sibsp",
    "parch",
    "fare"
]
categorical_features=[
    "sex",
    "embarked"
]
numeric_pipeline=Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])
categorical_pipeline=Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])
preprocessor=ColumnTransformer([
    ("num", numeric_pipeline, numeric_features),
    ("cat", categorical_pipeline, categorical_features)
])
models={
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(random_state=42)
}
results=[]
for name, model in models.items():
    pipeline=Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    pipeline.fit(X_train, y_train)
    y_pred=pipeline.predict(X_test)
    y_prob=pipeline.predict_proba(X_test)[:, 1]
    accuracy=accuracy_score(y_test, y_pred)
    precision=precision_score(y_test, y_pred)
    recall=recall_score(y_test, y_pred)
    f1=f1_score(y_test, y_pred)
    auc=roc_auc_score(y_test, y_prob)

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "AUC": auc
    })

    print(f"\n{name}")
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1:", f1)
    print("AUC:", auc)

comparison=pd.DataFrame(results)
print("\nModel Comparison:")
print(comparison)
roc_data={}
for name, model in models.items():
    pipeline=Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])
    pipeline.fit(X_train, y_train)
    y_pred=pipeline.predict(X_test)
    y_prob=pipeline.predict_proba(X_test)[:, 1]
    cm=confusion_matrix(y_test, y_pred)
    plt.figure()
    plt.imshow(cm)
    plt.title(f"{name} Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    for i in range(2):
        for j in range(2):
            plt.text(j, i, cm[i, j], ha="center", va="center")

    plt.xticks([0, 1], ["Not Survived", "Survived"])
    plt.yticks([0, 1], ["Not Survived", "Survived"])
    plt.tight_layout()
    plt.savefig(f"analytics/{name.lower().replace(' ', '_')}_confusion_matrix.png")
    plt.show()
    fpr, tpr, _=roc_curve(y_test, y_prob)
    roc_data[name]=(fpr, tpr, roc_auc_score(y_test, y_prob))
plt.figure()
for name, (fpr, tpr, auc_value) in roc_data.items():
    plt.plot(fpr, tpr, label=f"{name} AUC={auc_value:.3f}")
plt.plot([0, 1], [0, 1], linestyle="--")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curves")
plt.legend()
plt.tight_layout()
plt.savefig("analytics/roc_curves.png")
plt.show()

tree_pipeline=Pipeline([
    ("preprocessor", preprocessor),
    ("model", DecisionTreeClassifier(random_state=42))
])
tree_pipeline.fit(X_train, y_train)
feature_names=tree_pipeline.named_steps["preprocessor"].get_feature_names_out()
plt.figure(figsize=(18, 10))

plot_tree(
    tree_pipeline.named_steps["model"],
    feature_names=feature_names,
    class_names=["Not Survived", "Survived"],
    filled=True,
    rounded=True,
    max_depth=4
)
plt.title("Decision Tree")
plt.tight_layout()
plt.savefig("analytics/decision_tree.png")
plt.show()
print("\nClass distribution:")
print(y_train.value_counts())
print(y_train.value_counts(normalize=True))

imbalance_results=[]
baseline_pipeline=Pipeline([
    ("preprocessor", preprocessor),
    ("model", LogisticRegression(max_iter=1000))
])
baseline_pipeline.fit(X_train, y_train)
baseline_pred=baseline_pipeline.predict(X_test)
imbalance_results.append({
    "Method": "Baseline",
    "Precision": precision_score(y_test, baseline_pred),
    "Recall": recall_score(y_test, baseline_pred),
    "F1": f1_score(y_test, baseline_pred)
})

balanced_pipeline=Pipeline([
    ("preprocessor", preprocessor),
    ("model", LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    ))
])
balanced_pipeline.fit(X_train, y_train)
balanced_pred=balanced_pipeline.predict(X_test)
imbalance_results.append({
    "Method": "Class Weight Balanced",
    "Precision": precision_score(y_test, balanced_pred),
    "Recall": recall_score(y_test, balanced_pred),
    "F1": f1_score(y_test, balanced_pred)
})


X_train_processed=preprocessor.fit_transform(X_train)
X_test_processed=preprocessor.transform(X_test)
smote=SMOTE(random_state=42)
X_train_smote, y_train_smote=smote.fit_resample(
    X_train_processed,
    y_train
)
smote_model=LogisticRegression(max_iter=1000)
smote_model.fit(X_train_smote, y_train_smote)
smote_pred=smote_model.predict(X_test_processed)
imbalance_results.append({
    "Method": "SMOTE",
    "Precision": precision_score(y_test, smote_pred),
    "Recall": recall_score(y_test, smote_pred),
    "F1": f1_score(y_test, smote_pred)
})

imbalance_comparison=pd.DataFrame(imbalance_results)
print("\nImbalance comparison:")
print(imbalance_comparison)
rf_pipeline=Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestClassifier(
        random_state=42,
        oob_score=True
    ))
])
param_grid={
    "model__n_estimators": [100, 200],
    "model__max_depth": [None, 5, 10],
    "model__max_features": ["sqrt", "log2"]
}
grid_search=GridSearchCV(
    rf_pipeline,
    param_grid=param_grid,
    cv=5,
    scoring="f1",
    n_jobs=-1
)
grid_search.fit(X_train, y_train)
best_rf=grid_search.best_estimator_
print("\nRandom Forest Grid Search:")
print("Best parameters:")
print(grid_search.best_params_)
print("Best cross-validation F1:")
print(grid_search.best_score_)
print("OOB score:")
print(best_rf.named_steps["model"].oob_score_)
regression_features=[
    "survived",
    "pclass",
    "age",
    "sibsp",
    "parch",
    "sex",
    "embarked"
]
X_reg=df[regression_features]
y_reg=df["fare"]
X_reg_train, X_reg_test, y_reg_train, y_reg_test=train_test_split(
    X_reg,
    y_reg,
    test_size=0.2,
    random_state=42
)
reg_numeric=[
    "survived",
    "pclass",
    "age",
    "sibsp",
    "parch"
]
reg_categorical=[
    "sex",
    "embarked"
]
reg_numeric_pipeline=Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])
reg_categorical_pipeline=Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])
reg_preprocessor=ColumnTransformer([
    ("num", reg_numeric_pipeline, reg_numeric),
    ("cat", reg_categorical_pipeline, reg_categorical)
])
regression_pipeline=Pipeline([
    ("preprocessor", reg_preprocessor),
    ("model", LinearRegression())
])
regression_pipeline.fit(X_reg_train, y_reg_train)
fare_pred=regression_pipeline.predict(X_reg_test)
mae=mean_absolute_error(y_reg_test, fare_pred)
rmse=np.sqrt(mean_squared_error(y_reg_test, fare_pred))
r2=r2_score(y_reg_test, fare_pred)
n=len(y_reg_test)
p=len(
    regression_pipeline
    .named_steps["preprocessor"]
    .get_feature_names_out()
)
adjusted_r2=1 - ((1 - r2) * (n - 1) / (n - p - 1))
print("\nRegression Results:")
print("MAE:", mae)
print("RMSE:", rmse)
print("R2:", r2)
print("Adjusted R2:", adjusted_r2)
residuals=y_reg_test - fare_pred

plt.figure()
plt.scatter(fare_pred, residuals)
plt.axhline(0, linestyle="--")
plt.xlabel("Predicted Fare")
plt.ylabel("Residual")
plt.title("Fare Regression Residual Plot")
plt.tight_layout()
plt.savefig("analytics/fare_residual_plot.png")
plt.show()
smote_prob=smote_model.predict_proba(X_test_processed)[:, 1]
smote_accuracy=accuracy_score(y_test, smote_pred)
smote_precision=precision_score(y_test, smote_pred)
smote_recall=recall_score(y_test, smote_pred)
smote_f1=f1_score(y_test, smote_pred)
smote_auc=roc_auc_score(y_test, smote_prob)
print("\nSMOTE Logistic Regression:")
print("Accuracy:", smote_accuracy)
print("Precision:", smote_precision)
print("Recall:", smote_recall)
print("F1:", smote_f1)
print("AUC:", smote_auc)
joblib.dump(best_rf, "analytics/best_model_pipeline.joblib")
print("\nSaved model pipeline:")
print("analytics/best_model_pipeline.joblib")
loaded_pipeline=joblib.load(
    "analytics/best_model_pipeline.joblib"
)
sample_input=X_test.iloc[[0]]
sample_prediction=loaded_pipeline.predict(sample_input)
sample_actual=y_test.iloc[0]
print("Reloaded pipeline prediction:", sample_prediction[0])
print("Actual value:", sample_actual)