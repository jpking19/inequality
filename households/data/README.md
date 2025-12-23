# Household Data Documentation

## File: household_data.csv

### Description

This dataset contains realistic household financial data for ages 18-100, approximating US household wealth patterns based on Survey of Consumer Finances (SCF) trends.

### Data Columns

| Column       | Type  | Description                                 |
| ------------ | ----- | ------------------------------------------- |
| `age`        | int   | Age of household head (18-100 years)        |
| `dependents` | int   | Number of dependent household members (0-3) |
| `net_worth`  | float | Total household net worth in USD            |

### Data Characteristics

**Net Worth by Life Stage:**

- **Ages 18-25**: Low initial wealth ($5k-$35k)

  - Reflects student debt, entry-level income
  - Negative real wealth common but simplified here as low positive values

- **Ages 25-40**: Accumulation phase ($35k-$178k)

  - Career establishment
  - Home purchases begin
  - Family formation (dependents increase)

- **Ages 40-55**: Peak accumulation ($178k-$582k)

  - Peak earning years
  - Mortgage paydown
  - Retirement savings acceleration

- **Ages 55-65**: Pre-retirement ($582k-$1.03M)

  - Maximum net worth typically achieved
  - Mortgage often paid off
  - Peak retirement account balances

- **Ages 65-75**: Early retirement ($1.03M-$1.33M)

  - Modest wealth growth from investments
  - Conservative drawdowns begin

- **Ages 75-100**: Later retirement decline ($1.33M-$62k)
  - Systematic drawdowns for living expenses
  - Medical costs increase
  - Estate transfers to heirs
  - Natural wealth decline with age

**Dependents Distribution:**

- Concentrated in ages 25-55 (child-rearing years)
- 0-3 dependents per household
- Most households (especially older) have 0 dependents

### Data Sources & Methodology

This is **simulated data** based on:

- Federal Reserve Survey of Consumer Finances trends
- Median net worth by age group patterns
- Life-cycle wealth accumulation theory

**Note**: Real household wealth has much higher variance than shown here. This represents "average" or "typical" trajectories for modeling purposes.

### Usage

```python
import pandas as pd

# Load the data
df = pd.read_csv('households/data/household_data.csv')

# Total wealth in dataset
total_wealth = df['net_worth'].sum()  # ~$49.6M across 84 households

# Average by age group
df.groupby(pd.cut(df['age'], bins=[18,30,40,50,60,70,100]))['net_worth'].mean()
```

### Future Enhancements

Planned improvements:

- [ ] Add income data by age
- [ ] Add realistic dependent distributions from census data
- [ ] Add wealth variance/percentiles (P10, P50, P90)
- [ ] Add household type (single, married, etc.)
- [ ] Add geographic variation
- [ ] Add education level effects
- [ ] Add race/ethnicity wealth gaps
