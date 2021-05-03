# Glucose Data Analysis

This project analyzes changes in glucose, insulin, exercise, and instantaneous glucose trends in time series data  

--- --------------------------------

### Note: This project is a work in progress and will have new findings/investigations explained in the **highlights** section (below)

----------------------------------------------------------------



## Motivation
- To put my data analytics skills to the test, I wanted to work with real world data to find insights in the data that would help others
- The data used in this project comes from someone in my life that is important to me (I will keep them anonymous on their request) 
- This person is a diabetic. **I wanted to see if I could find insights in past data or create predictive models to help them deal with their diabetes better**. 


--- ------------------------------

## Tech/Framework

Data Analysis Done Using

- Python 
- Pandas 
- Sklearn (for data cleaning and models)
- Plotly (interactive graphs)
- Seaborn 
- Matplotlib
- Numpy 
- Scipy (statistical models and hypothesis testing)

## Highlights

- Making functions to clean over **180 excel sheets** containing glucose and exercise data 
- Investigating daily summary statistics over the last 4 months by plotting average exercise and glucose on the same axes to visualize trends 
- Exploring data for March specifically and finding statistically significant results between walking amounts and low blood glucose levels at night using **levene and t-tests** for hypothesis testing
- Researching the effects of instantaneous trend changes in glucose levels in March to see how instantaneous trends affect volatility of glucose over longer periods of time
- Identifying anomalies in less than 1% of the glucose time series data by using the interquartile range method, as well as **Isolation Forest, Density-Based SCAN, and SVM models** to understand the causes of past dangerous glucose levels

---------------------------------

## Notebooks/Files 
1. **cleaning_data.py**: File that contains data transformations from excel sheets -> single dataframe
2. **summary_exploration.ipynb**: Notebook that contains the graphs of the summary information (data aggregated daily)
3. **march_analysis/ipynb**: Notebook that contains the walking and low blood glucose **statistical hypothesis testing** as well as instantaneous trend analysis for March 
4. **glucose_2021_analysis.ipynb**: Notebook that contains trend exploration from January to April 2021 for **anomaly detection**

--- ------------------------------

## Screenshots

**Refer to graphs folder for all images**

1. Summary Data Analysis 

![Summary Graphs](https://github.com/Nick-palmar/glucose_data_exploration/blob/main/graphs/exercise_v_bs.png)

---------------------------------

2. March Blood Sugar Analysis 

- Examining Exercise vs Low Glucose Levels at Night

![Exercise Day Before Night Lows](https://github.com/Nick-palmar/glucose_data_exploration/blob/main/graphs/march_exercise_before_night_low.png)

![Exercise 2 Days Before Night Lows](https://github.com/Nick-palmar/glucose_data_exploration/blob/main/graphs/march_exercise_2_days_before_night_low.png)

![Exercise Not Before Night Lows](https://github.com/Nick-palmar/glucose_data_exploration/blob/main/graphs/march_exercise_not_before_night_low.png)

- Amount of Exercise Violin Plots 
![Exercise and Low Violin Plots](https://github.com/Nick-palmar/glucose_data_exploration/blob/main/graphs/exercise_low_violin_plots.png)

![Exercise and In Range Violin Plots](https://github.com/Nick-palmar/glucose_data_exploration/blob/main/graphs/exercise_in_range_violin_plots.png)

- Instantaneous Blood Sugar Trend Analysis

**Coming Soon**

---------------------------------

3. 2021 Glucose Level Outlier Detection 

- 2021 Glucose Trends  

![2021 Glucose Trends Graph](https://github.com/Nick-palmar/glucose_data_exploration/blob/main/graphs/time_series_01-04_2021.png)

- 2021 Outlier Detection Using Isolation Forest  

![2021 Glucose Outliers Graph](https://github.com/Nick-palmar/glucose_data_exploration/blob/main/graphs/iso_forest_outliers.png)



