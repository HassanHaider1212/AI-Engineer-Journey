# 📊 Data Science Basics

> **Master the fundamentals of data analysis and feature engineering**

## 🎯 Learning Objectives

By the end of this module, you will:
- Manipulate and analyze data using Pandas and NumPy
- Create compelling visualizations with Matplotlib and Seaborn
- Perform exploratory data analysis (EDA) systematically
- Engineer features for machine learning models
- Handle missing data and outliers effectively
- Work with time series and categorical data

## 📚 Core Concepts

### 1. Data Manipulation with Pandas
- **DataFrames and Series** - Core data structures
- **Indexing and selection** - loc, iloc, boolean indexing
- **Data cleaning** - Handling missing values, duplicates
- **Data transformation** - apply, map, groupby operations
- **Merging and joining** - Combining datasets
- **Time series operations** - Date/time handling

### 2. Numerical Computing with NumPy
- **Arrays and broadcasting** - Efficient numerical operations
- **Linear algebra** - Matrix operations and decompositions
- **Statistical functions** - Descriptive statistics
- **Random number generation** - Reproducible randomness
- **Performance optimization** - Vectorized operations

### 3. Data Visualization
- **Matplotlib** - Basic plotting and customization
- **Seaborn** - Statistical visualizations
- **Plot types** - Histograms, scatter plots, box plots, heatmaps
- **Styling and aesthetics** - Professional-looking plots
- **Interactive visualizations** - Plotly basics

### 4. Exploratory Data Analysis (EDA)
- **Data profiling** - Understanding data structure and quality
- **Univariate analysis** - Single variable distributions
- **Bivariate analysis** - Relationships between variables
- **Multivariate analysis** - Complex relationships
- **Statistical testing** - Hypothesis testing basics

### 5. Feature Engineering
- **Categorical encoding** - One-hot, label, target encoding
- **Numerical transformations** - Scaling, normalization, log transforms
- **Feature creation** - Domain-specific features
- **Feature selection** - Correlation analysis, importance ranking
- **Time-based features** - Lag features, rolling statistics

### 6. Data Quality and Preprocessing
- **Missing data strategies** - Imputation methods
- **Outlier detection** - Statistical and ML-based methods
- **Data validation** - Consistency checks
- **Data pipeline design** - Reproducible preprocessing

## 🛠️ Hands-on Projects

### Project 1: E-commerce Customer Analysis
**Objective**: Analyze customer behavior and purchasing patterns

**Dataset**: E-commerce transaction data with customer demographics

**Tasks**:
- Load and explore the dataset
- Clean and preprocess the data
- Analyze customer segments
- Visualize purchasing patterns
- Engineer features for customer lifetime value

**Learning Outcomes**:
- Data cleaning and preprocessing
- Customer segmentation techniques
- Time series analysis
- Business intelligence insights

### Project 2: Real Estate Price Prediction
**Objective**: Build features for predicting property prices

**Dataset**: Real estate listings with property features and prices

**Tasks**:
- Perform comprehensive EDA
- Handle missing values and outliers
- Engineer location-based features
- Create property characteristic features
- Analyze price distributions and correlations

**Learning Outcomes**:
- Geographic data analysis
- Feature engineering for regression
- Domain knowledge application
- Data quality assessment

### Project 3: Social Media Sentiment Analysis
**Objective**: Prepare text data for sentiment classification

**Dataset**: Social media posts with sentiment labels

**Tasks**:
- Text preprocessing and cleaning
- Feature extraction from text
- Sentiment distribution analysis
- Word frequency and n-gram analysis
- Prepare data for ML models

**Learning Outcomes**:
- Text data preprocessing
- Natural language processing basics
- Feature extraction techniques
- Data visualization for text

## 📁 Project Structure

```
02_data_science_basics/
├── notebooks/
│   ├── 01_pandas_fundamentals.ipynb     # Pandas basics and operations
│   ├── 02_numpy_operations.ipynb        # NumPy arrays and functions
│   ├── 03_data_visualization.ipynb      # Matplotlib and Seaborn
│   ├── 04_exploratory_analysis.ipynb    # EDA techniques and workflows
│   ├── 05_feature_engineering.ipynb     # Feature creation and selection
│   └── 06_data_quality.ipynb            # Data cleaning and validation
├── src/
│   ├── __init__.py
│   ├── data_loader.py                   # Data loading utilities
│   ├── preprocessing.py                 # Data preprocessing functions
│   ├── feature_engineering.py           # Feature creation functions
│   ├── visualization.py                 # Custom plotting functions
│   └── analysis.py                      # Statistical analysis functions
├── data/
│   ├── raw/                             # Original datasets
│   ├── processed/                       # Cleaned datasets
│   └── external/                        # External reference data
├── tests/
│   ├── __init__.py
│   ├── test_preprocessing.py
│   ├── test_feature_engineering.py
│   └── test_analysis.py
├── requirements.txt
└── README.md
```

## 🧪 Testing Strategy

### Data Quality Tests
- **Schema validation** - Check data types and structure
- **Completeness checks** - Missing value analysis
- **Consistency validation** - Cross-field validation
- **Uniqueness checks** - Duplicate detection

### Statistical Tests
- **Distribution tests** - Normality, skewness
- **Correlation analysis** - Feature relationships
- **Outlier detection** - Statistical and ML methods
- **Hypothesis testing** - Significance tests

### Performance Tests
- **Memory usage** - Large dataset handling
- **Processing time** - Optimization benchmarks
- **Scalability** - Performance with data size

## 📊 Assessment Criteria

### Data Analysis Skills (40%)
- [ ] Effective use of Pandas operations
- [ ] Proper data cleaning techniques
- [ ] Meaningful visualizations
- [ ] Statistical analysis accuracy

### Feature Engineering (30%)
- [ ] Creative feature creation
- [ ] Appropriate encoding methods
- [ ] Feature selection rationale
- [ ] Domain knowledge application

### Code Quality (20%)
- [ ] Clean, readable code
- [ ] Proper documentation
- [ ] Efficient implementations
- [ ] Error handling

### Insights and Communication (10%)
- [ ] Clear findings presentation
- [ ] Business relevance
- [ ] Actionable recommendations
- [ ] Visual storytelling

## 🚀 Getting Started

1. **Set up environment**:
   ```bash
   pip install pandas numpy matplotlib seaborn plotly jupyter
   ```

2. **Download datasets**:
   - E-commerce data from Kaggle
   - Real estate data from public APIs
   - Social media data from Twitter API

3. **Start with notebooks**:
   - Begin with `01_pandas_fundamentals.ipynb`
   - Work through each notebook systematically
   - Complete all exercises and challenges

4. **Build projects**:
   - Start with the e-commerce analysis
   - Apply techniques to real datasets
   - Document your findings

## 📚 Key Libraries and Tools

### Core Libraries
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **Matplotlib** - Basic plotting
- **Seaborn** - Statistical visualizations
- **Plotly** - Interactive visualizations

### Specialized Tools
- **Scikit-learn** - Feature engineering utilities
- **Feature-engine** - Advanced feature engineering
- **Pandas-profiling** - Automated EDA
- **Sweetviz** - Data comparison and analysis

### Data Sources
- **Kaggle** - Competition datasets
- **UCI ML Repository** - Academic datasets
- **Google Dataset Search** - Public datasets
- **Government APIs** - Open data sources

## 🎯 Best Practices

### Data Exploration
1. **Always start with data.shape and data.info()**
2. **Check for missing values systematically**
3. **Examine data types and ranges**
4. **Look for obvious data quality issues**

### Visualization
1. **Choose appropriate plot types for your data**
2. **Use consistent styling across plots**
3. **Add meaningful titles and labels**
4. **Consider your audience when designing**

### Feature Engineering
1. **Understand your domain before creating features**
2. **Start simple, then add complexity**
3. **Validate features with domain experts**
4. **Document feature creation logic**

### Code Organization
1. **Use functions for repeated operations**
2. **Create reusable preprocessing pipelines**
3. **Separate data loading from analysis**
4. **Version control your notebooks**

## 📈 Next Steps

After completing this module:
1. **Review your analysis** - Ensure insights are actionable
2. **Document your process** - Create a data analysis report
3. **Share your findings** - Present to peers or stakeholders
4. **Move to Phase 2** - Machine Learning Fundamentals

---

**Remember**: Data science is about asking the right questions and finding meaningful patterns. Focus on understanding your data deeply before jumping into modeling.
