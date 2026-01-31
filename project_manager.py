import os
import json
import datetime

class ProjectManager:
    def __init__(self, storage_folder="triai_projects"):
        self.storage_folder = storage_folder
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        """Creates the main storage directory if it doesn't exist."""
        if not os.path.exists(self.storage_folder):
            os.makedirs(self.storage_folder)

    def create_project(self, project_name):
        """Creates a new project folder and an empty history file."""
        # Sanitize name to be file-system safe
        safe_name = "".join([c for c in project_name if c.isalnum() or c in (' ', '_', '-')]).strip()
        project_path = os.path.join(self.storage_folder, safe_name)
        
        if not os.path.exists(project_path):
            os.makedirs(project_path)
            
        # Initialize the conversation history file
        history_file = os.path.join(project_path, "history.json")
        initial_data = {
            "project_name": project_name,
            "created_at": str(datetime.datetime.now()),
            "conversation": []
        }
        
        with open(history_file, 'w') as f:
            json.dump(initial_data, f, indent=4)
            
        return safe_name

    def save_interaction(self, project_name, user_prompt, ai_responses, consensus):
        """
        Saves a full turn (User Prompt + All AI Responses + Consensus) to the history.
        """
        project_path = os.path.join(self.storage_folder, project_name)
        history_file = os.path.join(project_path, "history.json")
        
        if not os.path.exists(history_file):
            return False

        # Load existing history
        with open(history_file, 'r') as f:
            data = json.load(f)
        
        # Append new interaction
        new_entry = {
            "timestamp": str(datetime.datetime.now()),
            "role": "turn",
            "user_prompt": user_prompt,
            "ai_responses": ai_responses, # Dictionary of {'gemini': '...', 'gpt': '...'}
            "consensus": consensus
        }
        data["conversation"].append(new_entry)
        
        # Save back to file
        with open(history_file, 'w') as f:
            json.dump(data, f, indent=4)
            
        return True

    def load_project_history(self, project_name):
        """Returns the full conversation history for a project."""
        history_file = os.path.join(self.storage_folder, project_name, "history.json")
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                return json.load(f)
        return None

    def list_projects(self):
        """Lists all available projects."""
        return [name for name in os.listdir(self.storage_folder) 
                if os.path.isdir(os.path.join(self.storage_folder, name))]
    
    def delete_project(self, project_name):
        """Deletes a project and all its files."""
        import shutil
        import stat
        import time
        
        project_path = os.path.join(self.storage_folder, project_name)
        
        if not os.path.exists(project_path):
            return False
        
        # Windows-safe deletion with error handling
        def handle_remove_readonly(func, path, exc):
            """Error handler for Windows readonly files"""
            os.chmod(path, stat.S_IWRITE)
            func(path)
        
        try:
            shutil.rmtree(project_path, onerror=handle_remove_readonly)
            return True
        except Exception as e:
            print(f"Error deleting project: {e}")
            # Try again after a short delay (files might be locked)
            time.sleep(0.5)
            try:
                shutil.rmtree(project_path, onerror=handle_remove_readonly)
                return True
            except:
                return False
