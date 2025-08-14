"""
Database migration script to remove company approval workflow
"""

from sqlalchemy import create_engine, text
from app.database.engine import engine

def remove_approval_columns():
    """Remove approval-related columns from companies table"""
    print("🔄 Removing approval-related columns from companies table...")
    
    with engine.begin() as conn:
        try:
            # List of approval-related columns to remove
            columns_to_remove = [
                'approval_stage',
                'l1_approved_by',
                'l1_approved_date',
                'admin_approved_by', 
                'admin_approved_date',
                'rejection_reason',
                'sla_breach_date',
                'escalation_level',
                'go_nogo_checklist_completed',
                'checklist_items'
            ]
            
            # Check if table exists and get existing columns
            check_table = text("SELECT table_name FROM information_schema.tables WHERE table_name = 'companies';")
            table_exists = conn.execute(check_table).fetchone()
            
            if not table_exists:
                print("Companies table does not exist. Skipping migration.")
                return
            
            # Get existing columns
            get_columns = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'companies';
            """)
            existing_columns = [row[0] for row in conn.execute(get_columns).fetchall()]
            
            # Remove columns that exist
            for column in columns_to_remove:
                if column in existing_columns:
                    try:
                        drop_column = text(f"ALTER TABLE companies DROP COLUMN IF EXISTS {column};")
                        conn.execute(drop_column)
                        print(f"   ✅ Removed column: {column}")
                    except Exception as e:
                        print(f"   ⚠️  Could not remove column {column}: {e}")
                else:
                    print(f"   ℹ️  Column {column} does not exist, skipping")
            
            # Update existing companies to have ACTIVE status if they have PENDING_APPROVAL
            update_status = text("""
                UPDATE companies 
                SET status = 'ACTIVE' 
                WHERE status = 'PENDING_APPROVAL';
            """)
            result = conn.execute(update_status)
            updated_count = result.rowcount
            print(f"   ✅ Updated {updated_count} companies from PENDING_APPROVAL to ACTIVE status")
            
            print("✅ Successfully removed approval workflow from companies table")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            raise

def main():
    """Run the migration"""
    print("🚀 Starting database migration: Remove Company Approval Workflow")
    remove_approval_columns()
    print("✅ Migration completed successfully!")

if __name__ == "__main__":
    main()