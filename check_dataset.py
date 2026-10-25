import pandas as pd

dataset = pd.read_csv("banking_knowledge_base_1000.csv")

print("Dataset loaded successfully!")
print("Total records:", len(dataset))
print("Columns:", list(dataset.columns))

print("\nFirst 3 records:")
print(dataset.head(3).to_string(index=False))
