-- =====================================================================
-- Restaurant Operations Customer Analytics — SQL Queries
-- Tables: consumers, consumer_preferences, ratings, restaurants,
--         restaurant_cuisines
-- =====================================================================

-- =========================
-- LOCAL INSIGHTS
-- =========================

-- 1. Distribution of consumers by city and state
SELECT City, State, COUNT(*) AS num_consumers
FROM consumers
GROUP BY City, State
ORDER BY num_consumers DESC;

-- 2. Age distribution of consumers by state
SELECT State,
       CASE WHEN Age < 30 THEN 'Under 30'
            WHEN Age <= 60 THEN '30-60'
            ELSE 'Over 60' END AS Age_Group,
       COUNT(*) AS num_consumers
FROM consumers
GROUP BY State, Age_Group
ORDER BY State, num_consumers DESC;

-- 3. % of smokers / non-smokers by city
SELECT City,
       ROUND(100.0 * SUM(CASE WHEN Smoker = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_smokers,
       ROUND(100.0 * SUM(CASE WHEN Smoker = 'No'  THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_nonsmokers,
       COUNT(*) AS total_consumers
FROM consumers
GROUP BY City;

-- 4. Parking availability by city
SELECT City, Parking, COUNT(*) AS num_restaurants
FROM restaurants
GROUP BY City, Parking
ORDER BY City, num_restaurants DESC;


-- =========================
-- DINING INSIGHTS
-- =========================

-- 5. Parking vs. price level
SELECT Price, Parking, COUNT(*) AS num_restaurants
FROM restaurants
GROUP BY Price, Parking
ORDER BY Price, num_restaurants DESC;

-- 6. Distribution of restaurants by state
SELECT State, COUNT(*) AS num_restaurants
FROM restaurants
GROUP BY State
ORDER BY num_restaurants DESC;

-- 7. Franchise vs. non-franchise consumer ratings
SELECT rs.Franchise,
       CASE r.Overall_Rating WHEN 0 THEN 'Unsatisfactory'
                              WHEN 1 THEN 'Satisfactory'
                              ELSE 'Highly Satisfactory' END AS Rating_Category,
       COUNT(*) AS num_ratings
FROM ratings r
JOIN restaurants rs ON r.Restaurant_ID = rs.Restaurant_ID
GROUP BY rs.Franchise, Rating_Category
ORDER BY rs.Franchise, num_ratings DESC;

-- 8. Top preferred cuisines
SELECT Preferred_Cuisine, COUNT(*) AS num_consumers
FROM consumer_preferences
GROUP BY Preferred_Cuisine
ORDER BY num_consumers DESC
LIMIT 5;


-- =========================
-- HOSPITALITY INSIGHTS
-- =========================

-- 9. Alcohol service mix across all restaurants (combined across cities)
SELECT Alcohol_Service, COUNT(*) AS num_restaurants,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM restaurants), 2) AS pct
FROM restaurants
GROUP BY Alcohol_Service
ORDER BY num_restaurants DESC;

-- 10. Most common transportation methods
SELECT Transportation_Method, COUNT(*) AS num_consumers,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM consumers), 1) AS pct
FROM consumers
GROUP BY Transportation_Method
ORDER BY num_consumers DESC;

-- 11. Alcohol service vs. consumer ratings
SELECT rs.Alcohol_Service,
       CASE r.Overall_Rating WHEN 0 THEN 'Unsatisfactory'
                              WHEN 1 THEN 'Satisfactory'
                              ELSE 'Highly Satisfactory' END AS Rating_Category,
       COUNT(*) AS num_ratings
FROM ratings r
JOIN restaurants rs ON r.Restaurant_ID = rs.Restaurant_ID
GROUP BY rs.Alcohol_Service, Rating_Category
ORDER BY rs.Alcohol_Service, num_ratings DESC;

-- 12. Smoking policy distribution
SELECT Smoking_Allowed, COUNT(*) AS num_restaurants,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM restaurants), 2) AS pct
FROM restaurants
GROUP BY Smoking_Allowed;


-- =========================
-- BEHAVIOR INSIGHTS
-- =========================

-- 13. Common occupations by state
SELECT State, Occupation, COUNT(*) AS num_consumers
FROM consumers
GROUP BY State, Occupation
ORDER BY State, num_consumers DESC;

-- 14. Drink level distribution by state
SELECT State, Drink_Level, COUNT(*) AS num_consumers,
       ROUND(100.0 * COUNT(*) / (
            SELECT COUNT(*) FROM consumers c2 WHERE c2.State = consumers.State
       ), 1) AS pct_of_state
FROM consumers
GROUP BY State, Drink_Level
ORDER BY State, num_consumers DESC;

-- 15. Marital status vs. smoking & drinking habits
SELECT Marital_Status, Smoker, Drink_Level, COUNT(*) AS num_consumers
FROM consumers
GROUP BY Marital_Status, Smoker, Drink_Level
ORDER BY Marital_Status, Smoker, num_consumers DESC;

-- 16. Occupation vs. budget level
SELECT Occupation, Budget, COUNT(*) AS num_consumers
FROM consumers
GROUP BY Occupation, Budget
ORDER BY Occupation, num_consumers DESC;


-- =========================
-- REVIEW INSIGHTS
-- =========================

-- 17. Top 5 restaurants by food rating (ranked by count of "Highly Satisfactory")
SELECT rs.Name,
       SUM(CASE WHEN r.Food_Rating = 2 THEN 1 ELSE 0 END) AS highly_satisfactory,
       SUM(CASE WHEN r.Food_Rating = 1 THEN 1 ELSE 0 END) AS satisfactory,
       SUM(CASE WHEN r.Food_Rating = 0 THEN 1 ELSE 0 END) AS unsatisfactory,
       COUNT(*) AS total_ratings
FROM ratings r
JOIN restaurants rs ON r.Restaurant_ID = rs.Restaurant_ID
GROUP BY rs.Name
ORDER BY highly_satisfactory DESC
LIMIT 5;

-- 18. Top 5 restaurants by service rating
SELECT rs.Name,
       SUM(CASE WHEN r.Service_Rating = 2 THEN 1 ELSE 0 END) AS highly_satisfactory,
       SUM(CASE WHEN r.Service_Rating = 1 THEN 1 ELSE 0 END) AS satisfactory,
       SUM(CASE WHEN r.Service_Rating = 0 THEN 1 ELSE 0 END) AS unsatisfactory,
       COUNT(*) AS total_ratings
FROM ratings r
JOIN restaurants rs ON r.Restaurant_ID = rs.Restaurant_ID
GROUP BY rs.Name
ORDER BY highly_satisfactory DESC
LIMIT 5;

-- 19. Top 5 restaurants by overall rating
SELECT rs.Name,
       SUM(CASE WHEN r.Overall_Rating = 2 THEN 1 ELSE 0 END) AS highly_satisfactory,
       SUM(CASE WHEN r.Overall_Rating = 1 THEN 1 ELSE 0 END) AS satisfactory,
       SUM(CASE WHEN r.Overall_Rating = 0 THEN 1 ELSE 0 END) AS unsatisfactory,
       COUNT(*) AS total_ratings
FROM ratings r
JOIN restaurants rs ON r.Restaurant_ID = rs.Restaurant_ID
GROUP BY rs.Name
ORDER BY highly_satisfactory DESC
LIMIT 5;