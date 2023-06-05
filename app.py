import os
from flask import Flask, render_template, request, jsonify
from shared.database import Database, FileStatus
from shared.azure_queue import AzureQueue
from shared.session_file_manager import SessionFileManager
from utils.helper_functions import allowed_file
import uuid

data_folder_path = os.environ.get("DATA_FOLDER")
queue_connection_string = os.getenv("QUEUE_AZURE_STORAGE_CONNECTION_STRING")
pdf_to_text_queue_name = os.getenv("PDF_TO_TEXT_QUEUE_NAME")

app = Flask(__name__)
database = Database(os.environ["SQLALCHEMY_DATABASE_URI"])

# Create the database file and tables (if they don't exist)
@app.before_request
def create_database():
    database.create_database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    session_id = str(uuid.uuid4())  # Generate a unique session ID
    session_file_manager = SessionFileManager(data_folder_path, session_id)
    database_session = database.get_session()
    azure_queue = AzureQueue(queue_connection_string,pdf_to_text_queue_name)

    files = request.files.getlist('file')  # Get the list of uploaded files
    for file in files:
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file. Only PDF files are allowed.'}), 400

    azure_queue.create_queue()
    for file in files:

        # save file
        session_file_manager.save_uploaded_file(file, file.filename)

        # save record to file_status table
        file_status = FileStatus(session_id, file.filename, 'NOT_STARTED')
        database_session.add(file_status)

        # add msg to Q
        message = { "session_id": session_id, "file_name": file.filename }
        azure_queue.send_message(message)

    database_session.commit()
    database_session.close()

    return jsonify({'session_id': session_id})

@app.route('/status/<session_id>', methods=['GET'])
def get_status(session_id):
    database_session = database.get_session()
    file_statuses = database_session.query(FileStatus).filter_by(session_id=session_id).all()
    database_session.close()

    status_list = []
    for file_status in file_statuses:
        status_list.append({
            'file_name': file_status.file_name,
            'status': file_status.status
        })

    return jsonify({'status': status_list})

if __name__ == '__main__':
    app.run()
