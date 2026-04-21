from core.database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as con:
        print("Migrating users table...")
        # Add columns if they don't exist (PostgreSQL syntax)
        con.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE"))
        con.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar VARCHAR DEFAULT '😀'"))
        con.commit()
        print("Schema updated successfully.")

        # Ask to promote a user to admin? Or just promote 'davsalcog69' if it exists
        # I'll look for the first user and make it admin
        result = con.execute(text("SELECT username FROM users LIMIT 1")).fetchone()
        if result:
            username = result[0]
            con.execute(text(f"UPDATE users SET is_admin = TRUE WHERE username = '{username}'"))
            con.commit()
            print(f"User '{username}' has been promoted to Administrator.")
        else:
            print("No users found to promote.")

if __name__ == "__main__":
    migrate()
