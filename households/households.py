import pandas as pd
import numpy as np

# ===============================================================================
# WEALTH REDISTRIBUTION MODEL
# ===============================================================================
#
# OBJECTIVE:
#   Redistribute a fixed pool of wealth across households to equalize the
#   marginal utility of consumption, accounting for:
#   - AGE: Younger households have more years to spread resources over
#   - DEPENDENTS: Larger households need more resources for the same welfare
#
# KEY ECONOMIC CONCEPT - MARGINAL UTILITY:
#   Marginal utility = the additional satisfaction from consuming $1 more
#
#   Optimal allocation: Give resources where they create the most value.
#   If household A has higher marginal utility than B, transferring $1 from
#   B to A increases total welfare. Keep transferring until marginal utilities
#   are equal across all households.
#
# DATA SOURCE:
#   Uses realistic US household data by age (18-100) with net worth values
#   approximating Survey of Consumer Finances patterns.
#
# ASSUMPTIONS:
#   1. Fixed lifespan: Everyone lives to age 100 (based on data range)
#   2. Constant consumption: Each household consumes the same amount per year
#   3. Linear utility: Each dollar provides equal satisfaction (σ = 0)
#      This means we're equalizing average consumption per equivalent-adult-year
#   4. No future income: We're only redistributing existing wealth
#   5. Equivalence scale: Dependents add 30% to household needs per person
#
# ===============================================================================

# -------------------------------
# 1. GLOBAL PARAMETERS
# -------------------------------

DATA_FILE = "households/data/household_data.csv"  # Path to household data
MAX_LIFE_EXPECTANCY = 100     # Maximum age in our dataset

# Equivalence scale: How much more a dependent adds to household needs
# 0.3 means each dependent increases needs by 30%
# Example: household with 2 dependents has equivalence factor of 1 + 0.3*2 = 1.6
DEPENDENT_WEIGHT = 0.3


# -------------------------------
# 2. LOAD HOUSEHOLD DATA FROM CSV
# -------------------------------

def load_household_data(filepath):
    """
    Load household data from CSV file.

    Expected columns:
      - age: Age of household head (18-100)
      - dependents: Number of dependent members (0, 1, 2, 3)
      - net_worth: Current household net worth in dollars

    The data represents realistic US household wealth patterns by age,
    based on Survey of Consumer Finances trends:
      - Young adults (18-25): Low/negative net worth
      - Working age (25-55): Accumulation phase
      - Pre-retirement (55-65): Peak wealth
      - Retirement (65+): Drawdown phase with eventual decline
    """
    df = pd.read_csv(filepath)

    # Add household ID
    df["household_id"] = range(1, len(df) + 1)

    # Validate required columns
    required_cols = ["age", "dependents", "net_worth"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"CSV missing required columns: {missing_cols}")

    return df


# Load the household data
households = load_household_data(DATA_FILE)

# Calculate total resources from the data
TOTAL_RESOURCES = households["net_worth"].sum()
NUM_HOUSEHOLDS = len(households)

print(f"Loaded {NUM_HOUSEHOLDS} households from {DATA_FILE}")
print(f"Total wealth in population: ${TOTAL_RESOURCES:,.0f}")
print(f"Age range: {households['age'].min()} to {households['age'].max()}")
print(f"Average net worth: ${households['net_worth'].mean():,.0f}")


# -------------------------------
# 3. CORE ECONOMIC FUNCTIONS
# -------------------------------

def equivalence_scale(dependents, weight=DEPENDENT_WEIGHT):
    """
    Calculate equivalence scale φ(d) for household size adjustment.

    A household with dependents needs more resources to achieve the same
    standard of living as a single-person household.

    Formula: φ(d) = 1 + weight × number_of_dependents

    Example:
      - 0 dependents: φ = 1.0 (baseline)
      - 1 dependent:  φ = 1.3 (needs 30% more)
      - 2 dependents: φ = 1.6 (needs 60% more)
    """
    return 1 + weight * dependents


def remaining_life_years(age, max_age=MAX_LIFE_EXPECTANCY):
    """
    Calculate remaining life years L for a person of given age.

    This is how many more years they will consume resources.
    Simplification: assumes everyone lives exactly to max_age.

    Example:
      - Age 25: L = 85 - 25 = 60 years remaining
      - Age 65: L = 85 - 65 = 20 years remaining
      - Age 85+: L = 0 years remaining
    """
    return max(0, max_age - age)


def marginal_utility(consumption_per_year):
    """
    Calculate marginal utility for a given consumption level.

    With linear utility (our assumption), marginal utility is constant.
    This means each additional dollar provides the same satisfaction.

    More realistic models use diminishing marginal utility where
    the first $1000 matters more than the millionth $1000.

    For linear utility: MU = 1 / consumption_per_year
    (Lower consumption → higher marginal utility → more benefit from transfers)
    """
    return 1.0 / np.maximum(consumption_per_year, 1e-10)


# -------------------------------
# 4. COMPUTE ADJUSTMENT FACTORS
# -------------------------------

# φ (phi): Equivalence scale - adjusts for household size
# Larger households need more resources for same welfare
households["phi"] = households["dependents"].apply(equivalence_scale)

# L: Remaining life years - how long resources must last
# Younger people need larger total allocations (spread over more years)
households["L"] = households["age"].apply(remaining_life_years)

# L × φ: Combined adjustment factor
# This is total "equivalent-adult-years" the household will consume
# Example: 2 dependents (φ=1.6) × 40 years remaining (L=40) = 64 eq-adult-years
households["L_phi"] = households["L"] * households["phi"]


# -------------------------------
# 5. SOLVE FOR EQUALIZED MARGINAL UTILITY
# -------------------------------
#
# GOAL: Find the optimal consumption level that equalizes marginal utility.
#
# MATH:
#   Total resources = Sum of (consumption per eq-adult-year × L × φ) for all households
#   $1,000,000 = c̄ × (L₁×φ₁ + L₂×φ₂ + ... + L₁₀₀×φ₁₀₀)
#
#   Solving for c̄ (consumption per equivalent-adult-year):
#   c̄ = Total Resources / Sum(L×φ)
#
# INTERPRETATION:
#   This is the annual consumption per equivalent adult that uses up all
#   resources exactly, with everyone receiving the same c̄.
#
#   With linear utility, equal c̄ means equal marginal utility!
#

# Sum of all equivalent-adult-years across all households
total_adjusted_life = households["L_phi"].sum()

# Equalized annual consumption per equivalent-adult
# This is the key result: everyone gets the same c̄
c_bar = TOTAL_RESOURCES / total_adjusted_life

print(f"\nOptimal consumption per equivalent-adult-year: ${c_bar:,.2f}")
print(f"Total equivalent-adult-years in population: {total_adjusted_life:,.1f}")
print(f"This is the amount each household gets annually per equivalent adult.\n")


# -------------------------------
# 6. COMPUTE TARGET ALLOCATIONS AND TRANSFERS
# -------------------------------

# Each household's target lifetime consumption = c̄ × L × φ
# Example: If c̄=$500/year, L=40 years, φ=1.6 dependents:
#          Target = $500 × 40 × 1.6 = $32,000 lifetime
households["target_lifetime_consumption"] = (
    c_bar * households["L_phi"]
)

# Annual consumption for the household (total, not per person)
households["annual_consumption"] = c_bar * households["phi"]

# Transfer needed: positive = receive money, negative = give money
# Transfer = Target allocation - Current net worth
households["transfer"] = (
    households["target_lifetime_consumption"] - households["net_worth"]
)

# Net worth after redistribution (this should equal target_lifetime_consumption)
households["net_worth_after_redistribution"] = (
    households["net_worth"] + households["transfer"]
)


# -------------------------------
# 7. VERIFY MARGINAL UTILITY EQUALIZATION
# -------------------------------

# Calculate marginal utility for each household
# With linear utility and equal c̄, these should all be equal
households["marginal_utility"] = marginal_utility(c_bar)

# Verify the marginal utilities are indeed equal
mu_min = households["marginal_utility"].min()
mu_max = households["marginal_utility"].max()
mu_std = households["marginal_utility"].std()

print(f"Marginal Utility Verification:")
print(f"  All households: {mu_min:.6f} (they're all equal with linear utility!)")
print(f"  Standard deviation: {mu_std:.10f} (should be ~0)")


# -------------------------------
# 8. CONSISTENCY CHECKS
# -------------------------------

# Check 1: Total allocated equals total resources
assert np.isclose(
    households["target_lifetime_consumption"].sum(),
    TOTAL_RESOURCES
), "Total allocation does not sum to total resources!"

# Check 2: Transfers balance (money in = money out)
assert np.isclose(
    households["transfer"].sum(),
    0
), "Transfers do not balance!"

print(">> All consistency checks passed!\n")


# -------------------------------
# 9. DETAILED OUTPUT
# -------------------------------

print("=" * 90)
print("WEALTH REDISTRIBUTION RESULTS")
print("=" * 90)

# Show a sample of households with key information
summary_columns = [
    "household_id",
    "age",
    "dependents",
    "L",           # remaining years
    "phi",         # equivalence scale
    "net_worth",
    "net_worth_after_redistribution",
    "transfer",
    "annual_consumption",
    "target_lifetime_consumption"
]

print("\nSample of 10 households:")
print(households[summary_columns].head(10).to_string(index=False))

# Aggregate statistics
print("\n" + "-" * 90)
print("AGGREGATE STATISTICS")
print("-" * 90)
print(households[["net_worth", "target_lifetime_consumption", "transfer", "annual_consumption"]].describe())

# Redistribution summary
print("\n" + "-" * 90)
print("REDISTRIBUTION SUMMARY")
print("-" * 90)

recipients = households[households["transfer"] > 0]
contributors = households[households["transfer"] < 0]

print(f"\nRecipients (receive money):")
print(f"  Count: {len(recipients)} households")
print(f"  Total received: ${recipients['transfer'].sum():,.0f}")
print(f"  Average transfer: ${recipients['transfer'].mean():,.0f}")

print(f"\nContributors (give money):")
print(f"  Count: {len(contributors)} households")
print(f"  Total contributed: ${abs(contributors['transfer'].sum()):,.0f}")
print(f"  Average transfer: ${abs(contributors['transfer'].mean()):,.0f}")

# Key insight: Who benefits?
print(f"\n" + "-" * 90)
print("KEY INSIGHTS")
print("-" * 90)
print(f"\nWho receives transfers (positive transfer)?")
print(f"  - Young households (more years to consume)")
print(f"  - Households with dependents (higher needs)")
print(f"  - Poor households (below average wealth)")

print(f"\nWho contributes (negative transfer)?")
print(f"  - Old households (fewer years remaining)")
print(f"  - Single-person households (lower needs)")
print(f"  - Wealthy households (above average wealth)")

print("\n" + "=" * 90)


# -------------------------------
# 10. EXPORT RESULTS TO CSV
# -------------------------------

output_file = "households/data/redistribution_results.csv"

# Select columns to export
# Select columns to export
export_columns = [
    "household_id",
    "age",
    "dependents",
    "net_worth",
    "net_worth_after_redistribution",
    "transfer",
    "L",
    "phi",
    "L_phi",
    "annual_consumption",
    "target_lifetime_consumption",
    "marginal_utility"
]

# Save to CSV
households[export_columns].to_csv(output_file, index=False)

print(f"\n>> Results exported to: {output_file}")
print(f"  Columns: {', '.join(export_columns)}")
print(f"  Rows: {len(households)}")
