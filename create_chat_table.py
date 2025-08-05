"""Script to create chat_history table directly."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_connection():
    """Get database connection."""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'quickdeliver'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '')
    )

def create_chat_history_table():
    """Create chat_history table."""
    
    create_table_sql = """
    -- Drop table if exists (for clean recreation)
    DROP TABLE IF EXISTS chat_history CASCADE;

    -- Create chat_history table
    CREATE TABLE chat_history (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      session_data jsonb NOT NULL,
      message_count integer DEFAULT 0,
      created_at timestamptz DEFAULT now()
    );

    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
    CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history(created_at);
    """
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("Creating chat_history table...")
        
        # Execute table creation
        cursor.execute(create_table_sql)
        
        conn.commit()
        print("✅ chat_history table created successfully!")
        
        # Verify table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'chat_history'
            );
        """)
        
        exists = cursor.fetchone()[0]
        if exists:
            print("✅ Verified: chat_history table exists in database")
        else:
            print("❌ Error: chat_history table was not created")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Creating chat_history table...")
    create_chat_history_table()