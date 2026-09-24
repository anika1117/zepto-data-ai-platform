import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

CSV_PATH = "analytics/titanic.csv"

df = sns.load_dataset("titanic")
df.to_csv(CSV_PATH, index=False)
print("Shape:")
print(df.shape)

print("\nInfo:")
df.info()

print("\nDescribe:")
print(df.describe())

missing = df.isnull().mean() * 100
missing = missing[missing > 0].sort_values(ascending=False)

print("\nMissing values:")
print(missing)

df = df.drop(columns=["deck"])

df["age"] = df["age"].fillna(df["age"].median())

df = df.dropna(subset=["embarked", "embark_town"])
df.to_csv(CSV_PATH, index=False)

print("\nShape after cleaning:")
print(df.shape)

print("\nRemaining missing values:")
print(df.isnull().sum())
for column in ["age", "fare"]:
    plt.figure()
    sns.histplot(df[column], kde=True)
    plt.title(f"{column.title()} Distribution")
    plt.xlabel(column)
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(f"analytics/{column}_histogram.png")
    plt.show()

    plt.figure()
    sns.boxplot(x=df[column])
    plt.title(f"{column.title()} Boxplot")
    plt.xlabel(column)
    plt.tight_layout()
    plt.savefig(f"analytics/{column}_boxplot.png")
    plt.show()


for column in ["age", "fare"]:
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = df[
        (df[column] < lower) |
        (df[column] > upper)
    ]

    print(f"\n{column} IQR:")
    print("Q1:", q1)
    print("Q3:", q3)
    print("IQR:", iqr)
    print("Lower bound:", lower)
    print("Upper bound:", upper)
    print("Outlier count:", len(outliers))


fare_mean = df["fare"].mean()
fare_median = df["fare"].median()
fare_mode = df["fare"].mode().iloc[0]

print("\nFare statistics:")
print("Mean:", fare_mean)
print("Median:", fare_median)
print("Mode:", fare_mode)

if fare_mean > fare_median > fare_mode:
    print("Fare distribution: right-skewed")
elif fare_mean < fare_median < fare_mode:
    print("Fare distribution: left-skewed")
else:
    print("Fare distribution: approximately symmetric")
print("\nSurvival rate by sex:")
sex_survival = df.groupby("sex")["survived"].mean()
print(sex_survival)

plt.figure()
sex_survival.plot(kind="bar")
plt.title("Survival Rate by Sex")
plt.xlabel("Sex")
plt.ylabel("Survival Rate")
plt.tight_layout()
plt.savefig("analytics/survival_by_sex.png")
plt.show()


print("\nSurvival rate by passenger class:")
class_survival = df.groupby("pclass")["survived"].mean()
print(class_survival)

plt.figure()
class_survival.plot(kind="bar")
plt.title("Survival Rate by Passenger Class")
plt.xlabel("Passenger Class")
plt.ylabel("Survival Rate")
plt.tight_layout()
plt.savefig("analytics/survival_by_class.png")
plt.show()


female_first = df[
    (df["sex"] == "female") &
    (df["pclass"] == 1)
]

male_third = df[
    (df["sex"] == "male") &
    (df["pclass"] == 3)
]

female_first_or_second = df[
    (df["sex"] == "female") &
    ((df["pclass"] == 1) | (df["pclass"] == 2))
]

print("\nBoolean masking examples:")
print("Female and 1st class survival rate:", female_first["survived"].mean())
print("Male and 3rd class survival rate:", male_third["survived"].mean())
print("Female and 1st or 2nd class survival rate:", female_first_or_second["survived"].mean())


sex_class_survival = df.groupby(["sex", "pclass"])["survived"].mean()

print("\nSurvival rate by sex and passenger class:")
print(sex_class_survival)

sex_class_survival.unstack().plot(kind="bar")
plt.title("Survival Rate by Sex and Passenger Class")
plt.xlabel("Sex")
plt.ylabel("Survival Rate")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("analytics/survival_by_sex_class.png")
plt.show()


correlation_columns = [
    "survived",
    "pclass",
    "age",
    "sibsp",
    "parch",
    "fare"
]

corr = df[correlation_columns].corr()

print("\nCorrelation matrix:")
print(corr)

plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Titanic Correlation Matrix")
plt.tight_layout()
plt.savefig("analytics/correlation_heatmap.png")
plt.show()


pairs = []

for i in range(len(correlation_columns)):
    for j in range(i + 1, len(correlation_columns)):
        col1 = correlation_columns[i]
        col2 = correlation_columns[j]
        value = corr.loc[col1, col2]
        pairs.append((col1, col2, value))

pairs = sorted(pairs, key=lambda x: abs(x[2]), reverse=True)

print("\nTop 2 strongest correlations:")
for pair in pairs[:2]:
    print(pair[0], "and", pair[1], ":", pair[2])
print("\nStandardization check:")

standardized = df[["age", "fare"]].copy()

for column in ["age", "fare"]:
    mean = standardized[column].mean()
    std = standardized[column].std()
    standardized[column] = (standardized[column] - mean) / std

print("\nBefore standardization:")
print(df[["age", "fare"]].agg(["mean", "std"]))

print("\nAfter standardization:")
print(standardized.agg(["mean", "std"]))