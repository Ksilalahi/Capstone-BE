import pandas as pd
from sqlalchemy import create_engine, text
from db_config import engine

FILE_PATH = "data/MyBank Data Baru.xlsx"

# EXTRACT
def extract():

    def load_sheet(name):
        df = pd.read_excel(FILE_PATH, sheet_name=name)

        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )
        return df

    df_users = load_sheet("Accounts")
    df_merchants = load_sheet("Merchants")
    df_trx = load_sheet("Transactions")
    df_inter = load_sheet("User_interactions")

    return df_users, df_merchants, df_trx, df_inter

# TRANSFORM
def transform(df_users, df_merchants, df_trx, df_inter):

    def clean_df(df):
        df = df.replace(['', 'NULL', 'null', 'NaN', 'nan'], pd.NA)
        return df

    df_users = clean_df(df_users)
    df_merchants = clean_df(df_merchants)
    df_trx = clean_df(df_trx)
    df_inter = clean_df(df_inter)

    # USERS
    users = df_users.copy()
    if 'jenis_kelamin' not in users.columns:
        if 'gender' in users.columns:
            users['jenis_kelamin'] = users['gender']
        else:
            users['jenis_kelamin'] = pd.NA

    users['jenis_kelamin'] = (
        users['jenis_kelamin']
        .astype(str)
        .str.strip()
        .str.lower()
    )

    mapping_gender = {
        'l': 'Laki-laki',
        'p': 'Perempuan',
        'male': 'Laki-laki',
        'female': 'Perempuan',
        'm': 'Laki-laki',
        'f': 'Perempuan'
    }

    users['jenis_kelamin'] = users['jenis_kelamin'].map(mapping_gender)
    users = users.dropna(subset=['jenis_kelamin'])
    users = users.dropna(subset=['no_rek'])
    users['saldo'] = pd.to_numeric(users['saldo'], errors='coerce')

    for col in ['tanggal_lahir','created_at','updated_at','last_login_at']:
        if col in users.columns:
            users[col] = pd.to_datetime(users[col], errors='coerce', dayfirst=True)

    users = users.drop_duplicates('no_rek')
    users = users.dropna(subset=['nama'])

    # MERCHANTS
    merchants = df_merchants.copy()
    merchants = merchants.dropna(subset=['merchant_id'])
    merchants = merchants.drop_duplicates('merchant_id')
    merchants = merchants.dropna(subset=['merchant_name'])

    # TRANSACTIONS
    transactions = df_trx.copy()
    transactions = transactions.dropna(subset=['trx_id','no_rek','merchant_id'])
    transactions['nominal'] = pd.to_numeric(transactions['nominal'], errors='coerce')
    transactions['tanggal_transaksi'] = pd.to_datetime(
        transactions['tanggal_transaksi'], errors='coerce', dayfirst=True
    )

    transactions = transactions.dropna(subset=['tanggal_transaksi','nominal'])
    transactions = transactions.drop_duplicates('trx_id')

    # FK VALIDATION
    transactions = transactions[
        transactions['no_rek'].isin(users['no_rek'])
    ]
    
    transactions = transactions[
        transactions['merchant_id'].isin(merchants['merchant_id'])
    ]

    # INTERACTIONS
    interactions = df_inter.copy()
    interactions = interactions.dropna(subset=['interaction_id','no_rek'])
    interactions['timestamp'] = pd.to_datetime(
        interactions['timestamp'], errors='coerce', dayfirst=True
    )

    interactions = interactions.dropna(subset=['timestamp'])
    interactions = interactions.drop_duplicates('interaction_id')

    # FK VALIDATION
    interactions = interactions[
        interactions['no_rek'].isin(users['no_rek'])
    ]

    # VALIDATION
    print("\n=== DATA VALIDATION ===")
    print("Users:", users.shape)
    print("Merchants:", merchants.shape)
    print("Transactions:", transactions.shape)
    print("Interactions:", interactions.shape)

    print("\nNULL CHECK:")
    print("Users:\n", users.isnull().sum())
    print("Transactions:\n", transactions.isnull().sum())
    print("Interactions:\n", interactions.isnull().sum())

    return users, merchants, transactions, interactions

# LOAD
def load(users, merchants, transactions, interactions):

    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))

        conn.execute(text("TRUNCATE TABLE interactions"))
        conn.execute(text("TRUNCATE TABLE transactions"))
        conn.execute(text("TRUNCATE TABLE merchants"))
        conn.execute(text("TRUNCATE TABLE users"))

        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

    users.to_sql('users', con=engine, if_exists='append', index=False)
    merchants.to_sql('merchants', con=engine, if_exists='append', index=False)
    transactions.to_sql('transactions', con=engine, if_exists='append', index=False)
    interactions.to_sql('interactions', con=engine, if_exists='append', index=False)

    print("DATA BERHASIL MASUK KE DATABASE")

# MAIN
def main():
    df_users, df_merchants, df_trx, df_inter = extract()
    users, merchants, transactions, interactions = transform(
        df_users, df_merchants, df_trx, df_inter
    )
    load(users, merchants, transactions, interactions)

if __name__ == "__main__":
    main()