from inventory_system.db.models import db, Log
from flask_login import current_user

class AuditLogger:
    @staticmethod
    def log(action, details, user=None):
        """
        Creates a new log entry.
        
        Args:
            action (str): A short summary of the action (e.g., 'Add Product').
            details (str): Detailed description of the event.
            user (User, optional): The user performing the action. Defaults to current_user.
        """
        if user is None:
            user = current_user
            
        # Ensure we have a valid user ID, or None for system actions if user is not authenticated
        user_id = user.id if user and user.is_authenticated else None
        
        try:
            new_log = Log(
                user_id=user_id,
                action=action,
                details=details
            )
            db.session.add(new_log)
            db.session.commit()
        except Exception as e:
            # Fallbacklogging to console if DB write fails, to ensure we know something happened
            print(f"FAILED TO WRITE AUDIT LOG: {action} - {details}. Error: {e}")
            db.session.rollback()
