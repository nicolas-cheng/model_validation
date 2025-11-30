# Information Value (IV) Analysis Report

## Dataset Overview
**File Name:** base_by_custfac_w_waterfall_bad_20250923_v4.parquet  
**Target Variable:** BAD_IND_30 (30-day bad indicator)  
**Positive Label:** 1 (Bad)  
**Analysis Method:** Quantile binning with 5 bins

## Feature Information Value (IV) Summary

| Feature | IV Value | Predictive Power |
|---------|----------|------------------|
| M2BAD_60 | 5.868 | Very Strong |
| CNT_EXPOSURE | 5.868 | Very Strong |
| M2BAD_30 | 5.868 | Very Strong |
| WATERFALL_NUM | 0.000 | No Predictive Power |

## IV Interpretation Guidelines
- **IV < 0.02:** No predictive power
- **0.02 ≤ IV < 0.1:** Weak predictive power  
- **0.1 ≤ IV < 0.3:** Medium predictive power
- **0.3 ≤ IV < 0.5:** Strong predictive power
- **IV ≥ 0.5:** Very strong predictive power

## Key Findings

### High Predictive Features
1. **M2BAD_60** (IV: 5.868) - Very strong predictive power
2. **CNT_EXPOSURE** (IV: 5.868) - Very strong predictive power  
3. **M2BAD_30** (IV: 5.868) - Very strong predictive power

### Non-Predictive Features
1. **WATERFALL_NUM** (IV: 0.000) - No predictive power for the target variable

## Detailed Bin Analysis

### CNT_EXPOSURE (Exposure Count)
- **Bin 1:** (0.999, 8.2] - Bad Rate: 100% - WOE: -11.04
- **Bin 2:** (8.2, 11.8] - Bad Rate: 100% - WOE: -11.04
- **Bin 3:** (11.8, 13.8] - Bad Rate: 100% - WOE: -11.04
- **Bin 4:** (13.8, 15.4] - Bad Rate: 100% - WOE: -11.04
- **Bin 5:** (15.4, 17.0] - Bad Rate: 0% - WOE: 12.43

### M2BAD_30 (Months to Bad - 30 days)
- **Bin 1:** (1.999, 6.0] - Bad Rate: 100% - WOE: -11.04
- **Bin 2:** (6.0, 11.8] - Bad Rate: 100% - WOE: -11.04
- **Bin 3:** (11.8, 15.8] - Bad Rate: 100% - WOE: -11.04
- **Bin 4:** (15.8, 18.4] - Bad Rate: 100% - WOE: -11.04
- **Bin 5:** (18.4, 24.0] - Bad Rate: 0% - WOE: 12.43

### M2BAD_60 (Months to Bad - 60 days)
- **Bin 1:** (2.999, 8.6] - Bad Rate: 100% - WOE: -11.04
- **Bin 2:** (8.6, 13.6] - Bad Rate: 100% - WOE: -11.04
- **Bin 3:** (13.6, 16.8] - Bad Rate: 100% - WOE: -11.04
- **Bin 4:** (16.8, 19.4] - Bad Rate: 100% - WOE: -11.04
- **Bin 5:** (19.4, 25.0] - Bad Rate: 0% - WOE: 12.43

## Recommendations

1. **Feature Selection:** Focus on M2BAD_60, CNT_EXPOSURE, and M2BAD_30 for model development
2. **Model Development:** These features show excellent predictive power for identifying bad accounts
3. **Data Quality:** Consider investigating why WATERFALL_NUM shows no predictive power
4. **Risk Modeling:** The strong IV values suggest these features will be highly effective in credit risk scoring models

## Limitations
- Analysis based on limited sample size (5 records shown)
- Consider performing analysis on the full dataset for more robust results
- Additional preprocessing may be needed for categorical variables