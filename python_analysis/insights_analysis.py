"""
Restaurant Operations Customer Analytics

Loads the five CSV tables into an in-memory SQLite database, then answers
every question from the Local / Dining / Hospitality / Behavior / Review
insight sections using SQL (via pandas.read_sql). A pure-pandas version of
a couple of the queries is included at the bottom for comparison.

Usage:
    python insights_analysis.py
"""

import sqlite3
import pandas as pd

pd.set_option("display.width", 150)
pd.set_option("display.max_columns", 10)

DATA_DIR = "."

# ---------------------------------------------------------------------
# 1. Load CSVs into SQLite
# ---------------------------------------------------------------------
conn = sqlite3.connect(":memory:")

tables = {
    "consumers": "consumers.csv",
    "consumer_preferences": "consumer_preferences.csv",
    "ratings": "ratings.csv",
    "restaurants": "restaurants.csv",
    "restaurant_cuisines": "restaurant_cuisines.csv",
}

for table, filename in tables.items():
    df = pd.read_csv(f"{DATA_DIR}/{filename}", encoding="utf-8-sig")
    df.to_sql(table, conn, if_exists="replace", index=False)


def run(title, query):
    print(f"\n=== {title} ===")
    print(pd.read_sql(query, conn).to_string(index=False))


# ---------------------------------------------------------------------
# LOCAL INSIGHTS
# ---------------------------------------------------------------------
run("1. Consumer distribution by city & state", """
    SELECT City, State, COUNT(*) AS num_consumers
    FROM consumers
    GROUP BY City, State
    ORDER BY num_consumers DESC;
""")

run("2. Age distribution by state", """
    SELECT State,
           CASE WHEN Age < 30 THEN 'Under 30'
                WHEN Age <= 60 THEN '30-60'
                ELSE 'Over 60' END AS Age_Group,
           COUNT(*) AS num_consumers
    FROM consumers
    GROUP BY State, Age_Group
    ORDER BY State, num_consumers DESC;
""")

run("3. Smokers vs non-smokers (%) by city", """
    SELECT City,
           ROUND(100.0 * SUM(CASE WHEN Smoker='Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_smokers,
           ROUND(100.0 * SUM(CASE WHEN Smoker='No'  THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_nonsmokers,
           COUNT(*) AS total_consumers
    FROM consumers
    GROUP BY City;
""")

run("4. Parking availability by city", """
    SELECT City, Parking, COUNT(*) AS num_restaurants
    FROM restaurants
    GROUP BY City, Parking
    ORDER BY City, num_restaurants DESC;
""")

# ---------------------------------------------------------------------
# DINING INSIGHTS
# ---------------------------------------------------------------------
run("5. Parking vs price level", """
    SELECT Price, Parking, COUNT(*) AS num_restaurants
    FROM restaurants
    GROUP BY Price, Parking
    ORDER BY Price, num_restaurants DESC;
""")

run("6. Restaurants by state", """
    SELECT State, COUNT(*) AS num_restaurants
    FROM restaurants
    GROUP BY State
    ORDER BY num_restaurants DESC;
""")

run("7. Franchise vs non-franchise ratings", """
    SELECT rs.Franchise,
           CASE r.Overall_Rating WHEN 0 THEN 'Unsatisfactory'
                                  WHEN 1 THEN 'Satisfactory'
                                  ELSE 'Highly Satisfactory' END AS Rating_Category,
           COUNT(*) AS num_ratings
    FROM ratings r
    JOIN restaurants rs ON r.Restaurant_ID = rs.Restaurant_ID
    GROUP BY rs.Franchise, Rating_Category
    ORDER BY rs.Franchise, num_ratings DESC;
""")

run("8. Top preferred cuisines", """
    SELECT Preferred_Cuisine, COUNT(*) AS num_consumers
    FROM consumer_preferences
    GROUP BY Preferred_Cuisine
    ORDER BY num_consumers DESC
    LIMIT 5;
""")

# ---------------------------------------------------------------------
# HOSPITALITY INSIGHTS
# ---------------------------------------------------------------------
run("9. Alcohol service mix (all restaurants combined)", """
    SELECT Alcohol_Service, COUNT(*) AS num_restaurants,
           ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM restaurants), 2) AS pct
    FROM restaurants
    GROUP BY Alcohol_Service
    ORDER BY num_restaurants DESC;
""")

run("10. Transportation methods used by consumers", """
    SELECT Transportation_Method, COUNT(*) AS num_consumers,
           ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM consumers), 1) AS pct
    FROM consumers
    GROUP BY Transportation_Method
    ORDER BY num_consumers DESC;
""")

run("11. Alcohol service vs consumer ratings", """
    SELECT rs.Alcohol_Service,
           CASE r.Overall_Rating WHEN 0 THEN 'Unsatisfactory'
                                  WHEN 1 THEN 'Satisfactory'
                                  ELSE 'Highly Satisfactory' END AS Rating_Category,
           COUNT(*) AS num_ratings
    FROM ratings r
    JOIN restaurants rs ON r.Restaurant_ID = rs.Restaurant_ID
    GROUP BY rs.Alcohol_Service, Rating_Category
    ORDER BY rs.Alcohol_Service, num_ratings DESC;
""")

run("12. Smoking policy distribution", """
    SELECT Smoking_Allowed, COUNT(*) AS num_restaurants,
           ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM restaurants), 2) AS pct
    FROM restaurants
    GROUP BY Smoking_Allowed;
""")

# ---------------------------------------------------------------------
# BEHAVIOR INSIGHTS
# ---------------------------------------------------------------------
run("13. Common occupations by state", """
    SELECT State, Occupation, COUNT(*) AS num_consumers
    FROM consumers
    GROUP BY State, Occupation
    ORDER BY State, num_consumers DESC;
""")

run("14. Drink level distribution by state", """
    SELECT State, Drink_Level, COUNT(*) AS num_consumers,
           ROUND(100.0 * COUNT(*) / (
               SELECT COUNT(*) FROM consumers c2 WHERE c2.State = consumers.State
           ), 1) AS pct_of_state
    FROM consumers
    GROUP BY State, Drink_Level
    ORDER BY State, num_consumers DESC;
""")

run("15. Marital status vs smoking & drinking habits", """
    SELECT Marital_Status, Smoker, Drink_Level, COUNT(*) AS num_consumers
    FROM consumers
    GROUP BY Marital_Status, Smoker, Drink_Level
    ORDER BY Marital_Status, Smoker, num_consumers DESC;
""")

run("16. Occupation vs budget level", """
    SELECT Occupation, Budget, COUNT(*) AS num_consumers
    FROM consumers
    GROUP BY Occupation, Budget
    ORDER BY Occupation, num_consumers DESC;
""")

# ---------------------------------------------------------------------
# REVIEW INSIGHTS — top 5 restaurants
# ---------------------------------------------------------------------
for label, column in [
    ("17. Top 5 restaurants by FOOD rating", "Food_Rating"),
    ("18. Top 5 restaurants by SERVICE rating", "Service_Rating"),
    ("19. Top 5 restaurants by OVERALL rating", "Overall_Rating"),
]:
    run(label, f"""
        SELECT rs.Name,
               SUM(CASE WHEN r.{column} = 2 THEN 1 ELSE 0 END) AS highly_satisfactory,
               SUM(CASE WHEN r.{column} = 1 THEN 1 ELSE 0 END) AS satisfactory,
               SUM(CASE WHEN r.{column} = 0 THEN 1 ELSE 0 END) AS unsatisfactory,
               COUNT(*) AS total_ratings
        FROM ratings r
        JOIN restaurants rs ON r.Restaurant_ID = rs.Restaurant_ID
        GROUP BY rs.Name
        ORDER BY highly_satisfactory DESC
        LIMIT 5;
    """)

# ---------------------------------------------------------------------
# Pure-pandas equivalent example (no SQL) — restaurants by state
# ---------------------------------------------------------------------
print("\n=== Pure-pandas example: restaurants by state ===")
restaurants_df = pd.read_csv(f"{DATA_DIR}/restaurants.csv", encoding="utf-8-sig")
print(
    restaurants_df.groupby("State").size()
    .sort_values(ascending=False)
    .rename("num_restaurants")
    .to_string()
)

conn.close()