import logging
import os
import sys
import azure.functions as func
import pdfplumber

if os.environ.get("AZURE_FUNCTIONS_ENVIRONMENT") == "Development":
    sys.path.append('../../')

from shared.database import Database, FileStatus
from shared.session_file_manager import SessionFileManager

app = func.FunctionApp()
data_folder_path = os.environ.get("DATA_FOLDER")
database = Database(os.environ["SQLALCHEMY_DATABASE_URI"])

@app.function_name(name="convertPdfToText")
@app.queue_trigger(arg_name="msg", queue_name="pdf-to-text-process-queue",
                   connection="AzureWebJobsStorage")  # Queue trigger
def main(msg: func.QueueMessage) -> None:
    try:
        payload = msg.get_json()
        session_id = payload.get("session_id")
        file_name = payload.get("file_name")

        session_file_manager = SessionFileManager(data_folder_path, session_id)

        # Update the status to 'IN_PROCESS' in the database
        update_status(session_id, file_name, 'IN_PROCESS')

        pdf_path = session_file_manager.get_file_path(file_name)
        txt_filename = os.path.splitext(file_name)[0] + '.txt'

        if not os.path.isfile(pdf_path):
            raise Exception('Source Pdf file not Exists')

        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()

            session_file_manager.save_file_content(text, txt_filename)

        # Update the status to 'COMPLETED' in the database
        update_status(session_id, file_name, 'COMPLETED')

        logging.info(f"PDF converted to text: {session_id} - {file_name}")

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        # Update the status to 'FAILED' in the database
        update_status(session_id, file_name, 'FAILED')
        raise e

def update_status(session_id, file_name, status):
    # Create a SQLAlchemy engine and session
    session = database.get_session()

    # Query the FileStatus table by session_id and file_name
    file_status = session.query(FileStatus).filter_by(session_id=session_id, file_name=file_name).first()

    if file_status:
        # Update the status
        file_status.status = status
    else:
        # Create a new FileStatus record
        file_status = FileStatus(session_id=session_id, file_name=file_name, status=status)
        session.add(file_status)

    # Commit the changes to the database
    session.commit()

    # Close the session
    session.close()


