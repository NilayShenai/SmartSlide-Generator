import os
import sys
from flask import Blueprint, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import tempfile
import threading
import uuid

# Import the API functions from your new utils.py
from .utils import (
    allowed_file, read_document_content, generate_presentation_content,
    process_presentation_job, active_jobs, job_results, cleanup_old_files
)

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

# API endpoints that integrate with your utils.py functions
@main.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@main.route('/api/config', methods=['GET'])
def get_config():
    """Get available configuration options"""
    from .utils import THEMES, TEXT_SIZES
    return jsonify({
        'themes': list(THEMES.keys()),
        'text_sizes': list(TEXT_SIZES.keys()),
        'tones': ["professional", "friendly", "urgent", "academic", "casual", "inspiring"],
        'audiences': ["general public", "technical professionals", "students", "executives", "policymakers", "researchers"],
        'output_formats': ["pptx"],
        'max_slides': 20,
        'min_slides': 3,
        'supported_file_types': ['txt', 'docx', 'pdf']
    })

@main.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload document file for content extraction"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported. Allowed: txt, docx, pdf'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        filepath = os.path.join(uploads_dir, unique_filename)
        file.save(filepath)
        
        # Read document content
        doc_content = read_document_content(filepath)
        
        # Predict number of slides if possible
        try:
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            from ppt_maker_flo import predict_num_slides, ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.0)
            predicted_slides = predict_num_slides(doc_content, llm)
        except Exception as e:
            print(f"Could not predict slides: {e}")
            predicted_slides = 5
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': unique_filename,
            'filepath': filepath,
            'content_preview': doc_content[:500] + "..." if len(doc_content) > 500 else doc_content,
            'content_length': len(doc_content),
            'predicted_slides': predicted_slides
        })
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@main.route('/api/generate', methods=['POST'])
def generate_presentation():
    """Generate presentation (async)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('topic') and not data.get('doc_filepath'):
            return jsonify({'error': 'Either topic or document file is required'}), 400
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Prepare configuration
        config = {
            'topic': data.get('topic', ''),
            'num_slides': str(data.get('num_slides', 5)),
            'tone': data.get('tone', 'professional'),
            'audience': data.get('audience', 'general public'),
            'theme': data.get('theme', 'corporate'),
            'text_size': data.get('text_size', 'medium'),
            'filename': data.get('filename', 'presentation'),
            'file_format': data.get('file_format', 'pptx'),
            'flowcharts': data.get('flowcharts', [])
        }
        
        # Handle document content if provided
        if data.get('doc_filepath'):
            doc_content = read_document_content(data['doc_filepath'])
            config['doc_content'] = doc_content
        
        # Initialize job tracking
        active_jobs[job_id] = {
            'status': 'started',
            'progress': 0,
            'created_at': datetime.now().isoformat(),
            'config': config
        }
        
        # Start background processing
        thread = threading.Thread(target=process_presentation_job, args=(job_id, config))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'started',
            'message': 'Presentation generation started'
        })
        
    except Exception as e:
        return jsonify({'error': f'Generation failed: {str(e)}'}), 500

@main.route('/api/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status and progress"""
    try:
        if job_id in active_jobs:
            return jsonify(active_jobs[job_id])
        elif job_id in job_results:
            return jsonify(job_results[job_id])
        else:
            return jsonify({'error': 'Job not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Status check failed: {str(e)}'}), 500

@main.route('/api/download/<job_id>', methods=['GET'])
def download_presentation(job_id):
    """Download generated presentation"""
    try:
        if job_id not in job_results:
            return jsonify({'error': 'Job not found'}), 404
        
        result = job_results[job_id]
        if result['status'] != 'completed':
            return jsonify({'error': 'Presentation not ready'}), 400
        
        # Use the specific download path
        download_dir = r"C:\Users\Arnav\Documents\LangChain projects\ai_ppt_maker_langchain_web\outputs"
        download_filepath = os.path.join(download_dir, result['filename'])
        
        # Determine file format from the config or filename
        file_format = result['config'].get('file_format', 'pptx')
        user_filename = result['config'].get('filename', 'presentation')
        
        # Add correct extension based on file format
        if file_format == 'pdf':
            if not user_filename.endswith('.pdf'):
                user_filename += '.pdf'
            mimetype = 'application/pdf'
        else:
            if not user_filename.endswith('.pptx'):
                user_filename += '.pptx'
            mimetype = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        
        # Check if file exists in the download directory
        if not os.path.exists(download_filepath):
            # If not found in download dir, try the original filepath as fallback
            original_filepath = result['filepath']
            if os.path.exists(original_filepath):
                # Copy from original location to download directory
                import shutil
                os.makedirs(download_dir, exist_ok=True)
                shutil.copy2(original_filepath, download_filepath)
            else:
                return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            download_filepath,
            as_attachment=True,
            download_name=user_filename,  # Use user's original filename with correct extension
            mimetype=mimetype  # Use correct mimetype for PDF or PPTX
        )
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@main.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all recent jobs"""
    try:
        all_jobs = {}
        
        # Add active jobs
        for job_id, job_data in active_jobs.items():
            all_jobs[job_id] = job_data
        
        # Add completed jobs
        for job_id, job_data in job_results.items():
            if job_id not in all_jobs:
                all_jobs[job_id] = job_data
        
        # Sort by creation time (most recent first)
        sorted_jobs = dict(sorted(
            all_jobs.items(),
            key=lambda x: x[1].get('created_at', ''),
            reverse=True
        ))
        
        return jsonify({
            'jobs': sorted_jobs,
            'total': len(sorted_jobs)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to list jobs: {str(e)}'}), 500

@main.route('/api/cleanup', methods=['POST'])
def manual_cleanup():
    """Manually trigger cleanup of old files"""
    try:
        cleanup_old_files()
        return jsonify({'message': 'Cleanup completed successfully'})
    except Exception as e:
        return jsonify({'error': f'Cleanup failed: {str(e)}'}), 500

@main.route('/api/preview/<job_id>', methods=['GET'])
def preview_presentation(job_id):
    """Get presentation preview/metadata"""
    try:
        if job_id not in job_results:
            return jsonify({'error': 'Job not found'}), 404
        
        result = job_results[job_id]
        if result['status'] != 'completed':
            return jsonify({'error': 'Presentation not ready'}), 400
        
        # Return metadata without the actual file
        preview_data = {
            'job_id': job_id,
            'filename': result['filename'],
            'slides_count': result['slides_count'],
            'created_at': result['created_at'],
            'theme': result['config']['theme'],
            'text_size': result['config']['text_size'],
            'tone': result['config']['tone'],
            'audience': result['config']['audience']
        }
        
        return jsonify(preview_data)
        
    except Exception as e:
        return jsonify({'error': f'Preview failed: {str(e)}'}), 500

# Error handlers
@main.app_errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413

@main.app_errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

@main.app_errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404
