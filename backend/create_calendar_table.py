from sqlalchemy import create_engine, text
from app.db.database import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)

create_table_sql = """
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AkademikTakvim' AND xtype='U')
BEGIN
    CREATE TABLE AkademikTakvim (
        TakvimID INT IDENTITY(1,1) PRIMARY KEY,
        AkademikYil NVARCHAR(20) NOT NULL,
        Donem NVARCHAR(20) NOT NULL,
        SinavTuru NVARCHAR(20) NOT NULL,
        BaslangicTarihi DATE NOT NULL,
        BitisTarihi DATE NOT NULL,
        AktifMi BIT NOT NULL DEFAULT 0
    );
END
"""

insert_data_sql = """
IF NOT EXISTS (SELECT * FROM AkademikTakvim WHERE AkademikYil = '2026-2027' AND Donem = 'Güz' AND SinavTuru = 'Vize')
BEGIN
    INSERT INTO AkademikTakvim (AkademikYil, Donem, SinavTuru, BaslangicTarihi, BitisTarihi, AktifMi)
    VALUES ('2026-2027', 'Güz', 'Vize', '2026-11-15', '2026-11-25', 1);
END
"""

with engine.connect() as conn:
    conn.execute(text(create_table_sql))
    conn.execute(text(insert_data_sql))
    conn.commit()

print("Table 'AkademikTakvim' created and test data inserted successfully.")
