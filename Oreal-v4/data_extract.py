import pandas as pd

# Input file (raw data)
input_file = "split_1.csv"
# Output file (just comments)
output_file = "unlabeled.csv"

# Read the CSV (no headers)
df = pd.read_csv(input_file, header=None)

# The comment is usually in column 5 (zero-based index = 5)
comments = df.iloc[:, 5]

# Create new dataframe with only "comment" column
comments_df = pd.DataFrame({"comment": comments})

# Save to CSV
comments_df.to_csv(output_file, index=False)

print(f"Extracted {len(comments_df)} comments to {output_file}")
