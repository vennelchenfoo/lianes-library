
import pandas as pd

csv_path = "/Users/jeorgecassiodesousasilva/Documents/lianes library/lianes-library/data/books_clean_debug2.csv"

    
# leitura tolerante: usa parser Python e pula linhas malformadas
books_df = pd.read_csv(
        csv_path,
        engine='python',
        on_bad_lines='skip',
        encoding='utf-8',
        sep=','
    )
print('DataFrame shape:', books_df.shape)
print('Preview:')
print(books_df.head(5).to_string(index=False))

