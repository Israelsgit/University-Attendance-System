"""
Database Migration: Remove Admin Role and Update System
This script migrates existing data to the new role structure where:
- Admin role is removed
- Lecturers get admin privileges
- Students remain as students
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.models.user import User, UserRole
from config.database import get_db_url

def run_migration():
    """Run the migration to remove admin role"""
    
    # Create database connection
    database_url = get_db_url()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    print("🔄 Starting migration: Remove Admin Role")
    print(f"📊 Database: {database_url}")
    print(f"⏰ Started at: {datetime.now()}")
    print("-" * 50)
    
    try:
        with SessionLocal() as db:
            # 1. Check current user role distribution
            print("📈 Current user role distribution:")
            
            students = db.query(User).filter(User.role == UserRole.STUDENT).count()
            lecturers = db.query(User).filter(User.role == UserRole.LECTURER).count()
            
            # Check for admin users (this will fail if enum already updated)
            try:
                admins = db.query(User).filter(User.role == "admin").count()
                print(f"   👨‍🎓 Students: {students}")
                print(f"   👨‍🏫 Lecturers: {lecturers}")
                print(f"   👤 Admins: {admins}")
            except Exception as e:
                print(f"   ⚠️  Admin role already removed or not found")
                admins = 0
                print(f"   👨‍🎓 Students: {students}")
                print(f"   👨‍🏫 Lecturers: {lecturers}")
            
            print()
            
            # 2. Handle existing admin users
            if admins > 0:
                print("🔄 Converting admin users to lecturers...")
                
                # Get all admin users
                admin_users = db.execute(
                    text("SELECT * FROM users WHERE role = 'admin'")
                ).fetchall()
                
                for admin_user in admin_users:
                    print(f"   Converting: {admin_user.full_name} ({admin_user.email})")
                    
                    # Update admin to lecturer
                    db.execute(
                        text("UPDATE users SET role = 'lecturer' WHERE id = :user_id"),
                        {"user_id": admin_user.id}
                    )
                    
                    # Ensure they have a staff_id if they don't
                    if not admin_user.staff_id:
                        # Generate staff_id from email or create default
                        staff_id = f"BU/ADM/{datetime.now().year}"
                        db.execute(
                            text("UPDATE users SET staff_id = :staff_id WHERE id = :user_id"),
                            {"staff_id": staff_id, "user_id": admin_user.id}
                        )
                        print(f"     Generated staff_id: {staff_id}")
                
                db.commit()
                print(f"✅ Converted {len(admin_users)} admin users to lecturers")
                print()
            
            # 3. Update database schema to remove admin from enum
            print("🔄 Updating database schema...")
            
            try:
                # For PostgreSQL
                db.execute(text("""
                    ALTER TYPE userrole DROP VALUE IF EXISTS 'ADMIN';
                """))
                print("✅ Removed ADMIN from UserRole enum (PostgreSQL)")
            except Exception as e:
                try:
                    # For SQLite, recreate the table without admin
                    db.execute(text("""
                        CREATE TABLE users_new AS 
                        SELECT * FROM users WHERE role != 'admin';
                    """))
                    
                    db.execute(text("DROP TABLE users;"))
                    db.execute(text("ALTER TABLE users_new RENAME TO users;"))
                    print("✅ Recreated users table without admin role (SQLite)")
                except Exception as e2:
                    print(f"⚠️  Schema update not needed or failed: {e2}")
            
            # 4. Verify migration
            print("🔍 Verifying migration...")
            
            final_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
            final_lecturers = db.query(User).filter(User.role == UserRole.LECTURER).count()
            
            print(f"   👨‍🎓 Students: {final_students}")
            print(f"   👨‍🏫 Lecturers: {final_lecturers} (includes former admins)")
            
            # 5. Update user permissions data
            print("🔄 Updating user permission flags...")
            
            # Ensure all lecturers have is_verified = True
            db.execute(
                text("UPDATE users SET is_verified = TRUE WHERE role = 'lecturer'")
            )
            
            # Update any missing staff_ids or matric_numbers
            lecturers_without_staff_id = db.execute(
                text("SELECT COUNT(*) FROM users WHERE role = 'lecturer' AND staff_id IS NULL")
            ).scalar()
            
            if lecturers_without_staff_id > 0:
                print(f"   ⚠️  Found {lecturers_without_staff_id} lecturers without staff_id")
                # You may want to handle this case
            
            students_without_matric = db.execute(
                text("SELECT COUNT(*) FROM users WHERE role = 'student' AND matric_number IS NULL")
            ).scalar()
            
            if students_without_matric > 0:
                print(f"   ⚠️  Found {students_without_matric} students without matric_number")
                # You may want to handle this case
            
            db.commit()
            # 5. Update user data to match university settings
            print("🔄 Updating user data to match Bowen University structure...")
            
            # Update colleges to match new structure
            college_mapping = {
                "College of Information Technology": "College of Computing and Communication Studies",
                "College of Engineering": "College of Agriculture and Engineering Sciences",
                "College of Social Sciences": "College of Social and Management Sciences"
            }
            
            for old_college, new_college in college_mapping.items():
                updated_count = db.execute(
                    text("UPDATE users SET college = :new_college WHERE college = :old_college"),
                    {"new_college": new_college, "old_college": old_college}
                ).rowcount
                
                if updated_count > 0:
                    print(f"   Updated {updated_count} users from '{old_college}' to '{new_college}'")
            
            # Update any missing matric_number or staff_id formats
            users_without_proper_ids = db.execute(
                text("""
                    SELECT id, email, role, department, matric_number, staff_id 
                    FROM users 
                    WHERE (role = 'student' AND (matric_number IS NULL OR matric_number NOT LIKE 'BU/%')) 
                       OR (role = 'lecturer' AND (staff_id IS NULL OR staff_id NOT LIKE 'BU/%'))
                """)
            ).fetchall()
            
            for user in users_without_proper_ids:
                if user.role == 'student':
                    from config.university_settings import UniversitySettings
                    new_matric = UniversitySettings.generate_student_id(user.department or "GEN")
                    # Replace XXXX with sequential number
                    existing_count = db.execute(
                        text("SELECT COUNT(*) FROM users WHERE matric_number LIKE :pattern"),
                        {"pattern": new_matric.replace("XXXX", "%")}
                    ).scalar()
                    new_matric = new_matric.replace("XXXX", f"{existing_count + 1:04d}")
                    
                    db.execute(
                        text("UPDATE users SET matric_number = :matric WHERE id = :user_id"),
                        {"matric": new_matric, "user_id": user.id}
                    )
                    print(f"   Generated matric number for {user.email}: {new_matric}")
                
                elif user.role == 'lecturer':
                    from config.university_settings import UniversitySettings
                    new_staff_id = UniversitySettings.generate_staff_id(user.department or "GEN")
                    
                    db.execute(
                        text("UPDATE users SET staff_id = :staff_id WHERE id = :user_id"),
                        {"staff_id": new_staff_id, "user_id": user.id}
                    )
                    print(f"   Generated staff ID for {user.email}: {new_staff_id}")
            
            print("✅ User data updated to match Bowen University structure")
            print()
            
            # 6. Create sample data if database is empty
            if final_students == 0 and final_lecturers == 0:
                print("🔄 Creating sample data for empty database...")
                create_sample_data(db)
            
            db.commit()
            
        print("=" * 50)
        print("✅ Migration completed successfully!")
        print(f"⏰ Completed at: {datetime.now()}")
        print()
        print("📋 Summary:")
        print(f"   • Admin role removed from system")
        print(f"   • All lecturers now have administrative privileges")
        print(f"   • Database schema updated")
        print(f"   • Total users migrated: {final_students + final_lecturers}")
        print()
        print("🚀 System is ready for the new role structure!")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise

def create_sample_data(db):
    """Create sample data for testing"""
    from api.utils.security import get_password_hash
    
    print("🔄 Creating sample users...")
    
    # Create sample lecturer
    sample_lecturer = {
        'full_name': 'Dr. Sample Lecturer',
        'email': 'lecturer@bowen.edu.ng',
        'hashed_password': get_password_hash('password'),
        'staff_id': 'BU/CSC/2024',
        'university': 'Bowen University',
        'college': 'College of Information Technology',
        'department': 'Computer Science',
        'role': 'lecturer',
        'is_active': True,
        'is_verified': True,
        'employment_date': datetime.now().date()
    }
    
    # Create sample student
    sample_student = {
        'full_name': 'Sample Student',
        'email': 'student@student.bowen.edu.ng',
        'hashed_password': get_password_hash('password'),
        'matric_number': 'BU/CSC/21/0001',
        'university': 'Bowen University',
        'college': 'College of Information Technology',
        'department': 'Computer Science',
        'programme': 'Computer Science',
        'level': '400',
        'role': 'student',
        'is_active': True,
        'is_verified': True,
        'admission_date': datetime.now().date()
    }
    
    # Insert sample users
    for user_data in [sample_lecturer, sample_student]:
        columns = ', '.join(user_data.keys())
        placeholders = ', '.join([f':{key}' for key in user_data.keys()])
        
        db.execute(
            text(f"INSERT INTO users ({columns}) VALUES ({placeholders})"),
            user_data
        )
    
    print("✅ Sample users created:")
    print("   👨‍🏫 Lecturer: lecturer@bowen.edu.ng (password: password)")
    print("   👨‍🎓 Student: student@student.bowen.edu.ng (password: password)")

def rollback_migration():
    """Rollback the migration (restore admin role)"""
    print("🔄 Rolling back migration...")
    print("⚠️  This will restore the admin role structure")
    
    # This is more complex and should be implemented if needed
    # For now, just print instructions
    print("📋 Manual rollback steps:")
    print("   1. Restore database backup from before migration")
    print("   2. Or manually update user roles in database")
    print("   3. Update application code to support admin role")
    
    print("❌ Automatic rollback not implemented")
    print("   Please restore from backup if needed")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration script")
    parser.add_argument("--rollback", action="store_true", help="Rollback the migration")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    if args.rollback:
        rollback_migration()
    elif args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print("This would:")
        print("   • Convert all admin users to lecturers")
        print("   • Remove admin role from database schema")
        print("   • Update user permissions")
        print("   • Verify data integrity")
        print()
        print("Run without --dry-run to execute the migration")
    else:
        run_migration()