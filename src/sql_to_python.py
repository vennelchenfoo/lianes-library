import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
# ==============================
# 1. Caminho do arquivo CSV
# ==============================
csv_path = "/Users/jeorgecassiodesousasilva/Documents/lianes library/lianes-library/data/books_clean_debug2.csv"

# ==============================
# 2. Ler o CSV com tratamento de erros
# ==============================
# engine="python" + on_bad_lines="skip" evita o erro:
# pandas.errors.ParserError: Expected X fields in line Y, saw Z
books_df = pd.read_csv(
    csv_path,
    engine="python",
    on_bad_lines="skip"   # ou "warn" se quiser ver avisos
)

print("Colunas encontradas no CSV:")
print(books_df.columns)
print()

print("Primeiras linhas do CSV:")
print(books_df.head())
print()

# Só para exemplo, ver títulos únicos (se a coluna existir)
if "title" in books_df.columns:
    title_unique = books_df["title"].unique()
    print(f"Quantidade de títulos únicos: {len(title_unique)}")
    # print(title_unique)  # cuidado: pode ser muita coisa


# =====================================
# 3. Preparar DataFrame para tabela `books`
# =====================================
# Sua tabela `books` (no MySQL) tem, por exemplo:
# book_id (INT, AUTO_INCREMENT, PRIMARY KEY)

schema = "lianes_library"
host = "127.0.0.1"
user = "root"
raw_password = "your_password_here"
password = urllib.parse.quote_plus(raw_password)
port = 3306

connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{schema}"

engine = create_engine(connection_string)

books_df.to_sql('title',
                    if_exists = 'append',
                    con = connection_string,
                    index = False)
# ISBN (VARCHAR)
# title (VARCHAR)
# author (VARCHAR)
# cost_book (DECIMAL)
# book_status (ENUM)

# Vamos mapear as colunas do CSV para
