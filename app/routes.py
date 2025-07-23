import os
import sys
import shutil
from flask import Blueprint, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import tempfile
import threading
import uuid

from .utils import (
    allowed_file, read_document_content, generate_presentation_content,
    process_presentation_job, active_jobs, job_results, cleanup_old_files,
    logger
)

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route('/favicon.ico')
def favicon():
    from flask import abort
    return '', 204

@main.route('/robots.txt')
def robots():
    return 'User-agent: *\nDisallow: /api/\nDisallow: /outputs/\nDisallow: /uploads/', 200, {'Content-Type': 'text/plain'}

@main.route('/manifest.json')
def manifest():
    return '', 204

@main.route('/<path:filename>')
def catch_static_files(filename):
    static_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf']
    if any(filename.lower().endswith(ext) for ext in static_extensions):
        return '', 204
    from flask import abort
    abort(404)

@main.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@main.route('/api/config', methods=['GET'])
def get_config():
    from .utils import THEMES, TEXT_SIZES
    return jsonify({
        'themes': list(THEMES.keys()),
        'text_sizes': list(TEXT_SIZES.keys()),
        'tones': ["professional", "friendly", "urgent", "academic", "casual", "inspiring"],
        'audiences': ["general public", "technical professionals", "students", "executives", "policymakers", "researchers"],
        'output_formats': ["pptx", "pdf"],
        'max_slides': 20,
        'min_slides': 3,
        'supported_file_types': ['txt', 'docx', 'pdf']
    })

@main.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported. Allowed: txt, docx, pdf'}), 400
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        if os.environ.get('DYNO'):
            uploads_dir = '/tmp'
        else:
            uploads_dir = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
        
        filepath = os.path.join(uploads_dir, unique_filename)
        file.save(filepath)
        
        doc_content = read_document_content(filepath)
        
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
    try:
        data = request.get_json()
        
        if not data.get('topic') and not data.get('doc_filepath'):
            return jsonify({'error': 'Either topic or document file is required'}), 400
        
        job_id = str(uuid.uuid4())
        print(f"Generated job_id: {job_id}")
        
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
        
        if data.get('doc_filepath'):
            doc_content = read_document_content(data['doc_filepath'])
            config['doc_content'] = doc_content
        
        active_jobs[job_id] = {
            'status': 'started',
            'progress': 0,
            'created_at': datetime.now().isoformat(),
            'config': config
        }
        
        print(f"Job {job_id} initialized in active_jobs")
        print(f"Current active jobs: {list(active_jobs.keys())}")
        
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
    try:
        if not job_id or len(job_id) < 10:
            return jsonify({'error': 'Invalid job ID format'}), 400
        
        logger.info(f"Checking status for job_id: {job_id}")
        logger.info(f"Active jobs: {list(active_jobs.keys())}")
        logger.info(f"Completed jobs: {list(job_results.keys())}")
        
        if job_id in active_jobs:
            response_data = active_jobs[job_id].copy()
            response_data['source'] = 'active_jobs'
            return jsonify(response_data)
        elif job_id in job_results:
            response_data = job_results[job_id].copy()
            response_data['source'] = 'job_results'
            return jsonify(response_data)
        else:
            return jsonify({
                'error': 'Job not found',
                'job_id': job_id,
                'active_jobs_count': len(active_jobs),
                'completed_jobs_count': len(job_results),
                'debug_info': {
                    'active_job_ids': list(active_jobs.keys()),
                    'completed_job_ids': list(job_results.keys())
                }
            }), 404
            
    except Exception as e:
        logger.error(f"Status check failed for job {job_id}: {e}")
        return jsonify({'error': f'Status check failed: {str(e)}'}), 500

@main.route('/api/download/<job_id>', methods=['GET'])
def download_presentation(job_id):
    try:
        if job_id not in job_results:
            return jsonify({'error': 'Job not found'}), 404
        
        result = job_results[job_id]
        if result['status'] != 'completed':
            return jsonify({'error': 'Presentation not ready'}), 400
        
        if os.environ.get('DYNO'):
            download_dir = '/tmp'
        else:
            download_dir = os.path.join(os.getcwd(), 'outputs')
        download_filepath = os.path.join(download_dir, result['filename'])
        
        file_format = result['config'].get('file_format', 'pptx')
        user_filename = result['config'].get('filename', 'presentation')
        
        if file_format == 'pdf':
            if not user_filename.endswith('.pdf'):
                user_filename += '.pdf'
            mimetype = 'application/pdf'
        else:
            if not user_filename.endswith('.pptx'):
                user_filename += '.pptx'
            mimetype = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        
        if not os.path.exists(download_filepath):
            original_filepath = result['filepath']
            if os.path.exists(original_filepath):
                os.makedirs(download_dir, exist_ok=True)
                shutil.copy2(original_filepath, download_filepath)
            else:
                return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            download_filepath,
            as_attachment=True,
            download_name=user_filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@main.route('/api/jobs', methods=['GET'])
def list_jobs():
    try:
        all_jobs = {}
        
        for job_id, job_data in active_jobs.items():
            all_jobs[job_id] = job_data
        
        for job_id, job_data in job_results.items():
            if job_id not in all_jobs:
                all_jobs[job_id] = job_data
        
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
    try:
        cleanup_old_files()
        return jsonify({'message': 'Cleanup completed successfully'})
    except Exception as e:
        return jsonify({'error': f'Cleanup failed: {str(e)}'}), 500

@main.route('/api/preview/<job_id>', methods=['GET'])
def preview_presentation(job_id):
    try:
        if job_id not in job_results:
            return jsonify({'error': 'Job not found'}), 404
        
        result = job_results[job_id]
        if result['status'] != 'completed':
            return jsonify({'error': 'Presentation not ready'}), 400
        
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

@main.route('/api/debug/jobs', methods=['GET'])
def debug_jobs():
    return jsonify({
        'active_jobs': {
            'count': len(active_jobs),
            'jobs': {job_id: {'status': job_data.get('status'), 'progress': job_data.get('progress')} 
                     for job_id, job_data in active_jobs.items()}
        },
        'completed_jobs': {
            'count': len(job_results),
            'jobs': {job_id: {'status': job_data.get('status')} 
                     for job_id, job_data in job_results.items()}
        },
        'total_jobs': len(active_jobs) + len(job_results)
    })

@main.app_errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413

@main.app_errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

@main.app_errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'API endpoint not found', 'path': request.path}), 404
    return jsonify({'error': 'Resource not found', 'path': request.path, 'message': 'The requested resource was not found on this server'}), 404