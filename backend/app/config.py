import urllib

driver = '{ODBC Driver 18 for SQL Server}'
params = urllib.parse.quote_plus(
    f"DRIVER={driver};"
    f"SERVER=<your-server-name>.database.windows.net,1433;"
    f"DATABASE=<your-database-name>;"
    f"UID=<your-username>;"
    f"PWD=<your-password>;"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)

SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
