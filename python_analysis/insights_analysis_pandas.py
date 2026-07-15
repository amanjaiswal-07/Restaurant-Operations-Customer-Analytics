"""
Restaurant Operations Customer Analytics — PURE PANDAS (no SQL)

Answers every question from the Local / Dining / Hospitality / Behavior /
Review insight sections using only pandas: groupby, merge, value_counts,
pivot_table, etc.

Usage:
    python insights_analysis_pandas.py
"""

import pandas as pd

pd.set_option("display.width", 150)
pd.set_option("display.max_columns", 10)

DATA_DIR = "."

# ---------------------------------------------------------------------
# 1. Load CSVs
# ---------------------------------------------------------------------
consumers = pd.read_csv(f"{DATA_DIR}/consumers.csv", encoding="utf-8-sig")
consumer_preferences = pd.read_csv(f"{DATA_DIR}/consumer_preferences.csv", encoding="utf-8-sig")
ratings = pd.read_csv(f"{DATA_DIR}/ratings.csv", encoding="utf-8-sig")
restaurants = pd.read_csv(f"{DATA_DIR}/restaurants.csv", encoding="utf-8-sig")
restaurant_cuisines = pd.read_csv(f"{DATA_DIR}/restaurant_cuisines.csv", encoding="utf-8-sig")


def show(title, result):
    print(f"\n=== {title} ===")
    print(result.to_string())


# ---------------------------------------------------------------------
# LOCAL INSIGHTS
# ---------------------------------------------------------------------

# 1. Consumer distribution by city & state
result = (
    consumers.groupby(["City", "State"])
    .size()
    .rename("num_consumers")
    .sort_values(ascending=False)
)
show("1. Consumer distribution by city & state", result)

# 2. Age distribution by state
age_bins = [0, 29, 60, 200]
age_labels = ["Under 30", "30-60", "Over 60"]
consumers["Age_Group"] = pd.cut(consumers["Age"], bins=age_bins, labels=age_labels)
result = (
    consumers.groupby(["State", "Age_Group"], observed=True)
    .size()
    .rename("num_consumers")
    .sort_values(ascending=False)
    .sort_index(level="State", sort_remaining=False)
)
show("2. Age distribution by state", result)

# 3. Smokers vs non-smokers (%) by city
smoker_pct = (
    consumers.groupby("City")["Smoker"]
    .value_counts(normalize=True)
    .mul(100)
    .round(1)
    .rename("pct")
    .unstack("Smoker")
)
smoker_pct["total_consumers"] = consumers.groupby("City").size()
show("3. Smokers vs non-smokers (%) by city", smoker_pct)

# 4. Parking availability by city
result = (
    restaurants.groupby(["City", "Parking"], dropna=False)
    .size()
    .rename("num_restaurants")
    .sort_values(ascending=False)
    .sort_index(level="City", sort_remaining=False)
)
show("4. Parking availability by city", result)

# ---------------------------------------------------------------------
# DINING INSIGHTS
# ---------------------------------------------------------------------

# 5. Parking vs price level
result = (
    restaurants.groupby(["Price", "Parking"], dropna=False)
    .size()
    .rename("num_restaurants")
    .sort_values(ascending=False)
    .sort_index(level="Price", sort_remaining=False)
)
show("5. Parking vs price level", result)

# 6. Restaurants by state
result = restaurants.groupby("State").size().rename("num_restaurants").sort_values(ascending=False)
show("6. Restaurants by state", result)

# 7. Franchise vs non-franchise ratings
rating_map = {0: "Unsatisfactory", 1: "Satisfactory", 2: "Highly Satisfactory"}
ratings_merged = ratings.merge(restaurants[["Restaurant_ID", "Franchise"]], on="Restaurant_ID")
ratings_merged["Rating_Category"] = ratings_merged["Overall_Rating"].map(rating_map)
result = (
    ratings_merged.groupby(["Franchise", "Rating_Category"])
    .size()
    .rename("num_ratings")
    .sort_values(ascending=False)
    .sort_index(level="Franchise", sort_remaining=False)
)
show("7. Franchise vs non-franchise ratings", result)

# 8. Top preferred cuisines
result = (
    consumer_preferences["Preferred_Cuisine"]
    .value_counts()
    .rename("num_consumers")
    .head(5)
)
show("8. Top preferred cuisines", result)

# ---------------------------------------------------------------------
# HOSPITALITY INSIGHTS
# ---------------------------------------------------------------------

# 9. Alcohol service mix (all restaurants combined)
counts = restaurants["Alcohol_Service"].value_counts(dropna=False)
pct = (counts / len(restaurants) * 100).round(2)
result = pd.DataFrame({"num_restaurants": counts, "pct": pct})
show("9. Alcohol service mix (all restaurants combined)", result)

# 10. Transportation methods used by consumers
counts = consumers["Transportation_Method"].value_counts(dropna=False)
pct = (counts / len(consumers) * 100).round(1)
result = pd.DataFrame({"num_consumers": counts, "pct": pct})
show("10. Transportation methods used by consumers", result)

# 11. Alcohol service vs consumer ratings
ratings_merged2 = ratings.merge(restaurants[["Restaurant_ID", "Alcohol_Service"]], on="Restaurant_ID")
ratings_merged2["Rating_Category"] = ratings_merged2["Overall_Rating"].map(rating_map)
result = (
    ratings_merged2.groupby(["Alcohol_Service", "Rating_Category"], dropna=False)
    .size()
    .rename("num_ratings")
    .sort_values(ascending=False)
    .sort_index(level="Alcohol_Service", sort_remaining=False)
)
show("11. Alcohol service vs consumer ratings", result)

# 12. Smoking policy distribution
counts = restaurants["Smoking_Allowed"].value_counts(dropna=False)
pct = (counts / len(restaurants) * 100).round(2)
result = pd.DataFrame({"num_restaurants": counts, "pct": pct})
show("12. Smoking policy distribution", result)

# ---------------------------------------------------------------------
# BEHAVIOR INSIGHTS
# ---------------------------------------------------------------------

# 13. Common occupations by state
result = (
    consumers.groupby(["State", "Occupation"], dropna=False)
    .size()
    .rename("num_consumers")
    .sort_values(ascending=False)
    .sort_index(level="State", sort_remaining=False)
)
show("13. Common occupations by state", result)

# 14. Drink level distribution by state
counts = consumers.groupby(["State", "Drink_Level"]).size().rename("num_consumers")
state_totals = consumers.groupby("State").size()
pct = counts / counts.index.get_level_values("State").map(state_totals) * 100
result = pd.DataFrame({"num_consumers": counts, "pct_of_state": pct.round(1)})
result = result.sort_values("num_consumers", ascending=False).sort_index(level="State", sort_remaining=False)
show("14. Drink level distribution by state", result)

# 15. Marital status vs smoking & drinking habits
result = (
    consumers.groupby(["Marital_Status", "Smoker", "Drink_Level"], dropna=False)
    .size()
    .rename("num_consumers")
    .sort_values(ascending=False)
    .sort_index(level=["Marital_Status", "Smoker"], sort_remaining=False)
)
show("15. Marital status vs smoking & drinking habits", result)

# 16. Occupation vs budget level
result = (
    consumers.groupby(["Occupation", "Budget"], dropna=False)
    .size()
    .rename("num_consumers")
    .sort_values(ascending=False)
    .sort_index(level="Occupation", sort_remaining=False)
)
show("16. Occupation vs budget level", result)

# ---------------------------------------------------------------------
# REVIEW INSIGHTS — top 5 restaurants
# ---------------------------------------------------------------------
for label, column in [
    ("17. Top 5 restaurants by FOOD rating", "Food_Rating"),
    ("18. Top 5 restaurants by SERVICE rating", "Service_Rating"),
    ("19. Top 5 restaurants by OVERALL rating", "Overall_Rating"),
]:
    merged = ratings.merge(restaurants[["Restaurant_ID", "Name"]], on="Restaurant_ID")
    summary = merged.groupby("Name")[column].value_counts().unstack(fill_value=0)
    summary = summary.rename(columns={0: "unsatisfactory", 1: "satisfactory", 2: "highly_satisfactory"})
    summary["total_ratings"] = summary.sum(axis=1)
    summary = summary.sort_values("highly_satisfactory", ascending=False).head(5)
    show(label, summary[["highly_satisfactory", "satisfactory", "unsatisfactory", "total_ratings"]])