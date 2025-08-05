"""Database utilities for PostgreSQL connection and operations."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import bcrypt
import json
from dotenv import load_dotenv
load_dotenv()

class DatabaseManager:
    """Database manager for PostgreSQL operations."""
    
    def __init__(self):
        self.connection_params = self._load_connection_params()
    def _load_connection_params(self) -> Dict[str, str]:
        """Loads database connection parameters from environment variables."""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'quickdeliver'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
        # Initialize database tables on first use
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Ensure database tables exist, create them if they don't."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if users table exists
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'users'
                        );
                    """)
                    
                    if not cursor.fetchone()[0]:
                        print("Creating database tables...")
                        self._create_tables(cursor)
                        conn.commit()
                        print("✅ Database tables created successfully!")
        except Exception as e:
            print(f"Warning: Could not check/create tables: {e}")
    
    def _create_tables(self, cursor):
        """Create all necessary database tables."""
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                username text UNIQUE NOT NULL,
                email text UNIQUE NOT NULL,
                name text NOT NULL,
                password_hash text NOT NULL,
                subscription text DEFAULT 'Basic',
                created_at timestamptz DEFAULT now(),
                updated_at timestamptz DEFAULT now()
            );
            
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """)
        
        # Create orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                order_number text UNIQUE NOT NULL,
                restaurant text NOT NULL,
                items jsonb NOT NULL DEFAULT '[]',
                total decimal(10,2) NOT NULL DEFAULT 0.00,
                status text NOT NULL DEFAULT 'Pending',
                created_at timestamptz DEFAULT now(),
                updated_at timestamptz DEFAULT now()
            );
            
            CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
            CREATE INDEX IF NOT EXISTS idx_orders_order_number ON orders(order_number);
            CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
            CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
        """)
        
        # Create bills table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                month text NOT NULL,
                amount decimal(10,2) NOT NULL DEFAULT 0.00,
                status text NOT NULL DEFAULT 'Pending',
                due_date date NOT NULL,
                created_at timestamptz DEFAULT now(),
                updated_at timestamptz DEFAULT now()
            );
            
            CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id);
            CREATE INDEX IF NOT EXISTS idx_bills_status ON bills(status);
            CREATE INDEX IF NOT EXISTS idx_bills_due_date ON bills(due_date);
        """)
        
        # Create chat_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                session_data jsonb NOT NULL,
                message_count integer DEFAULT 0,
                created_at timestamptz DEFAULT now()
            );
            
            CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
            CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history(created_at);
        """)
        
        # Create trigger function and triggers
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = now();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            
            DROP TRIGGER IF EXISTS update_users_updated_at ON users;
            CREATE TRIGGER update_users_updated_at 
                BEFORE UPDATE ON users 
                FOR EACH ROW 
                EXECUTE FUNCTION update_updated_at_column();
                
            DROP TRIGGER IF EXISTS update_orders_updated_at ON orders;
            CREATE TRIGGER update_orders_updated_at 
                BEFORE UPDATE ON orders 
                FOR EACH ROW 
                EXECUTE FUNCTION update_updated_at_column();
                
            DROP TRIGGER IF EXISTS update_bills_updated_at ON bills;
            CREATE TRIGGER update_bills_updated_at 
                BEFORE UPDATE ON bills 
                FOR EACH ROW 
                EXECUTE FUNCTION update_updated_at_column();
        """)
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager."""
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            st.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False) -> Optional[List[Dict]]:
        """Execute a database query."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, params)
                    
                    if fetch:
                        result = cursor.fetchall()
                        return [dict(row) for row in result]
                    else:
                        conn.commit()
                        return None
        except Exception as e:
            print(f"Query execution error: {e}")
            import traceback
            traceback.print_exc()
            st.error(f"Query execution error: {e}")
            return None
    
    def create_user(self, username: str, email: str, password: str, name: str) -> bool:
        """Create a new user in the database."""
        try:
            # Hash the password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            query = """
                INSERT INTO users (username, email, name, password_hash, subscription)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (username, email, name, password_hash, 'Basic')
            
            self.execute_query(query, params)
            return True
            
        except psycopg2.IntegrityError:
            # Username or email already exists
            return False
        except Exception as e:
            st.error(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data."""
        query = """
            SELECT id, username, email, name, password_hash, subscription, created_at
            FROM users 
            WHERE username = %s
        """
        
        result = self.execute_query(query, (username,), fetch=True)
        
        if result and len(result) > 0:
            user = result[0]
            stored_hash = user['password_hash']
            
            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                # Remove password hash from returned data
                user.pop('password_hash', None)
                return user
        
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user data by username."""
        query = """
            SELECT id, username, email, name, subscription, created_at
            FROM users 
            WHERE username = %s
        """
        
        result = self.execute_query(query, (username,), fetch=True)
        return result[0] if result else None
    
    def get_user_orders(self, user_id: str) -> List[Dict]:
        """Get user's orders from database."""
        query = """
            SELECT id, order_number, restaurant, items, total, status, created_at
            FROM orders 
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        
        result = self.execute_query(query, (user_id,), fetch=True)
        return result if result else []
    
    def get_user_bills(self, user_id: str) -> List[Dict]:
        """Get user's bills from database."""
        query = """
            SELECT id, month, amount, status, due_date, created_at
            FROM bills 
            WHERE user_id = %s
            ORDER BY due_date DESC
        """
        
        result = self.execute_query(query, (user_id,), fetch=True)
        return result if result else []
    
    def create_order(self, user_id: str, order_data: Dict) -> bool:
        """Create a new order."""
        try:
            query = """
                INSERT INTO orders (user_id, order_number, restaurant, items, total, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (
                user_id,
                order_data.get('order_number'),
                order_data.get('restaurant'),
                order_data.get('items', []),
                order_data.get('total', 0),
                order_data.get('status', 'Pending')
            )
            
            self.execute_query(query, params)
            return True
            
        except Exception as e:
            st.error(f"Error creating order: {e}")
            return False
    
    def update_user_subscription(self, user_id: str, subscription: str) -> bool:
        """Update user's subscription plan."""
        try:
            query = """
                UPDATE users 
                SET subscription = %s, updated_at = now()
                WHERE id = %s
            """
            
            self.execute_query(query, (subscription, user_id))
            return True
            
        except Exception as e:
            st.error(f"Error updating subscription: {e}")
            return False
    
    def check_username_exists(self, username: str) -> bool:
        """Check if username already exists."""
        query = "SELECT 1 FROM users WHERE username = %s"
        result = self.execute_query(query, (username,), fetch=True)
        return len(result) > 0 if result else False
    
    def check_email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        query = "SELECT 1 FROM users WHERE email = %s"
        result = self.execute_query(query, (email,), fetch=True)
        return len(result) > 0 if result else False
    
    def save_chat_history(self, username: str, chat_history: List[Dict]) -> bool:
        """Save chat history to database."""
        try:
            print(f"Starting save_chat_history for username: {username}")
            
            if not chat_history:
                print("No chat history to save")
                return False
                
            # Get user ID
            user = self.get_user_by_username(username)
            if not user:
                print(f"User not found: {username}")
                return False
            
            user_id = user['id']
            print(f"Saving chat for user_id: {user_id}")
            
            # Prepare session data
            from datetime import datetime
            session_data = {
                'messages': chat_history,
                'conversation_summary': self._generate_conversation_summary(chat_history),
                'saved_at': datetime.now().isoformat()
            }
            
            print(f"Session data prepared with {len(chat_history)} messages")
            
            # Use direct connection for better error handling
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    print("Executing INSERT query...")
                    cursor.execute("""
                        INSERT INTO chat_history (user_id, session_data, message_count)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (user_id, json.dumps(session_data), len(chat_history)))
                    
                    result = cursor.fetchone()
                    print(f"Query executed, result: {result}")
                    conn.commit()
                    print("Transaction committed")
                    
                    if result:
                        print(f"Chat history saved with ID: {result['id']}")
                        return True
                    else:
                        print("Failed to save chat history - no result returned")
                        return False
            
        except Exception as e:
            print(f"Error saving chat history: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_chat_history(self, username: str) -> List[Dict]:
        """Get chat history for user."""
        try:
            print(f"Starting get_chat_history for username: {username}")
            
            # Get user ID
            user = self.get_user_by_username(username)
            if not user:
                print(f"User not found for chat history: {username}")
                return []
            
            user_id = user['id']
            print(f"Getting chat history for user_id: {user_id}")
            
            # Use direct connection for better error handling
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    print("Executing SELECT query...")
                    cursor.execute("""
                        SELECT session_data, message_count, created_at
                        FROM chat_history 
                        WHERE user_id = %s
                        ORDER BY created_at DESC
                        LIMIT 10
                    """, (user_id,))
                    
                    result = cursor.fetchall()
                    print(f"Chat history query returned {len(result)} results")
                    
                    # Convert to list of dicts
                    return [dict(row) for row in result]
            
        except Exception as e:
            print(f"Error fetching chat history: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def delete_chat_history(self, username: str) -> bool:
        """Delete all chat history for user."""
        try:
            # Get user ID
            user = self.get_user_by_username(username)
            if not user:
                print(f"User not found for deletion: {username}")
                return False
            
            user_id = user['id']
            print(f"Deleting chat history for user_id: {user_id}")
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM chat_history WHERE user_id = %s", (user_id,))
                    deleted_count = cursor.rowcount
                    conn.commit()
                    
                    print(f"Deleted {deleted_count} chat history records")
                    return True
            
        except Exception as e:
            print(f"Error deleting chat history: {e}")
            import traceback
            traceback.print_exc()
            st.error(f"Error deleting chat history: {e}")
            return False
    
    def _generate_conversation_summary(self, chat_history: List[Dict]) -> str:
        """Generate a summary of the conversation."""
        if not chat_history:
            return "Empty conversation"
        
        # Look for keywords to determine conversation topic
        all_messages = ' '.join([msg.get('content', '') for msg in chat_history]).lower()
        
        if 'refund' in all_messages:
            return "Refund Request"
        elif 'track' in all_messages or 'order' in all_messages:
            return "Order Tracking"
        elif 'bill' in all_messages or 'payment' in all_messages:
            return "Billing Inquiry"
        elif 'recommend' in all_messages:
            return "Restaurant Recommendations"
        else:
            return "General Support"


# Global database manager instance
db_manager = DatabaseManager()