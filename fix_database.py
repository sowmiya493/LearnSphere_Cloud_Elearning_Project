
from app import app, db
from sqlalchemy import inspect, text

with app.app_context():
    # Display the exact database used by Flask
    print("Database location:")
    print(db.engine.url.database)

    # Create any missing tables
    db.create_all()

    # Inspect the actual progress table
    inspector = inspect(db.engine)
    columns = {
        column["name"]
        for column in inspector.get_columns("progress")
    }

    print("Existing progress columns:", columns)

    # Add the missing columns if needed
    with db.engine.begin() as connection:
        if "completed" not in columns:
            connection.execute(text(
                "ALTER TABLE progress "
                "ADD COLUMN completed BOOLEAN NOT NULL DEFAULT 1"
            ))
            print("Added completed column.")
        else:
            print("completed column already exists.")

        if "completed_at" not in columns:
            connection.execute(text(
                "ALTER TABLE progress ADD COLUMN completed_at DATETIME"
            ))
            print("Added completed_at column.")
        else:
            print("completed_at column already exists.")

    # Verify the final schema
    inspector = inspect(db.engine)
    final_columns = [
        column["name"]
        for column in inspector.get_columns("progress")
    ]

    print("Final progress columns:", final_columns)
    print("Database repair completed.")
