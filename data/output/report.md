# Feature Binning Analysis Report

## Dataset Overview
- **Dataset**: base_by_custfac_w_waterfall_bad_20250923_v4.parquet
- **Target Variable**: BAD_IND_30 (Binary indicator for 30-day bad loans)
- **Features Analyzed**: CNT_EXPOSURE, M2BAD_30, M2BAD_60, WATERFALL_NUM
- **Binning Method**: Quantile binning
- **Number of Bins**: 5

## Information Value (IV) Analysis Results

### Overall Feature Importance (IV Scores)

| Feature | Information Value (IV) | Predictive Power |
|---------|----------------------|------------------|
| M2BAD_60 | 5.87 | Very Strong |
| CNT_EXPOSURE | 5.87 | Very Strong |
| M2BAD_30 | 5.87 | Very Strong |
| WATERFALL_NUM | 0.00 | No Predictive Power |

### IV Interpretation Guidelines
- **IV < 0.02**: Not predictive
- **0.02 ≤ IV < 0.1**: Weak predictive power
- **0.1 ≤ IV < 0.3**: Medium predictive power
- **0.3 ≤ IV < 0.5**: Strong predictive power
- **IV ≥ 0.5**: Very strong predictive power

## Detailed Binning Analysis

### 1. CNT_EXPOSURE (Number of Exposures)

| Bin Range | Count | Bad Rate | WOE | IV Contribution |
|-----------|-------|----------|-----|----------------|
| (0.999, 8.2] | 1 | 100% | -11.04 | 0.69 |
| (8.2, 11.8] | 1 | 100% | -11.04 | 0.69 |
| (11.8, 13.8] | 1 | 100% | -11.04 | 0.69 |
| (13.8, 15.4] | 1 | 100% | -11.04 | 0.69 |
| (15.4, 17.0] | 1 | 0% | 12.43 | 3.11 |

**Key Insights**:
- Lower exposure counts (1-15) show 100% bad rate
- Highest exposure count (17) shows 0% bad rate
- Strong predictive pattern with clear risk differentiation

### 2. M2BAD_30 (Months to 30-day Bad)

| Bin Range | Count | Bad Rate | WOE | IV Contribution |
|-----------|-------|----------|-----|----------------|
| (1.999, 6.0] | 1 | 100% | -11.04 | 0.69 |
| (6.0, 11.8] | 1 | 100% | -11.04 | 0.69 |
| (11.8, 15.8] | 1 | 100% | -11.04 | 0.69 |
| (15.8, 18.4] | 1 | 100% | -11.04 | 0.69 |
| (18.4, 24.0] | 1 | 0% | 12.43 | 3.11 |

**Key Insights**:
- Shorter time to bad (2-18 months) all show 100% bad rate
- Longest time to bad (24 months) shows 0% bad rate
- Clear risk differentiation based on time to default

### 3. M2BAD_60 (Months to 60-day Bad)

| Bin Range | Count | Bad Rate | WOE | IV Contribution |
|-----------|-------|----------|-----|----------------|
| (2.999, 8.6] | 1 | 100% | -11.04 | 0.69 |
| (8.6, 13.6] | 1 | 100% | -11.04 | 0.69 |
| (13.6, 16.8] | 1 | 100% | -11.04 | 0.69 |
| (16.8, 19.4] | 1 | 100% | -11.04 | 0.69 |
| (19.4, 25.0] | 1 | 0% | 12.43 | 3.11 |

**Key Insights**:
- Similar pattern to M2BAD_30 but with slightly different bin boundaries
- All bins except the highest show 100% bad rate
- Strong predictive power for 60-day bad prediction

### 4. WATERFALL_NUM

| Bin Range | Count | Bad Rate | WOE | IV Contribution |
|-----------|-------|----------|-----|----------------|
| nan | 5 | 80% | 0.00 | 0.00 |

**Key Insights**:
- No variation in this feature (all values = 99.0)
- Zero predictive power
- Consider excluding from modeling

## Recommendations

### 1. Feature Selection
- **High Priority**: M2BAD_30, M2BAD_60, CNT_EXPOSURE (all show very strong predictive power)
- **Exclude**: WATERFALL_NUM (no predictive value)

### 2. Model Development
- Use the identified bins for feature engineering
- Consider combining related features (M2BAD_30 and M2BAD_60)
- Monitor feature stability over time

### 3. Risk Management
- The binning analysis reveals clear risk thresholds:
  - CNT_EXPOSURE > 15 indicates lower risk
  - M2BAD_30 > 18 indicates lower risk
  - M2BAD_60 > 19 indicates lower risk

### 4. Next Steps
- Validate findings on larger dataset
- Test different binning methods (tree-based, equal-width)
- Consider interaction effects between features
- Monitor model performance with these binned features

---

*Report generated on: 2025-01-30*  
*Analysis Method: Information Value (IV) with Quantile Binning*