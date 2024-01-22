import pandas as pd

# Specify the encoding as 'ISO-8859-1'
df = pd.read_csv(r"c:\Users\AY\Desktop\have_shame.txt", encoding='ISO-8859-1', sep=";")


df.to_excel(r"c:\Users\AY\Desktop\have_shame.xlsx", index=False)


a=2