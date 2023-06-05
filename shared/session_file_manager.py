import os
import shutil

class SessionFileManager:
    def __init__(self, data_folder_path, session_id):
        self.data_folder_path = data_folder_path
        self.session_id = session_id
        self.session_dir = self.create_session_directory()

    def create_session_directory(self):
        session_dir = os.path.join(self.data_folder_path, self.session_id)
        os.makedirs(session_dir, exist_ok=True)
        return session_dir

    def save_uploaded_file(self, file, filename):
        filepath = os.path.join(self.session_dir, filename)
        file.save(filepath)
        return filepath

    def save_file_content(self, content, filename):
        filepath = os.path.join(self.session_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath

    def get_file_path(self, filename):
        filepath = os.path.join(self.session_dir, filename)
        return filepath

    def delete_session_directory(self):
        shutil.rmtree(self.session_dir)