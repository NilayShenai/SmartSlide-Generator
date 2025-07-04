# utils.py - Utility functions for Enhanced PowerPoint Generator

import os
import sys
from pathlib import Path
import platform
import re
import traceback

# Add the parent directory to Python path for importing ppt_maker_flo
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

def convert_pptx_to_pdf(pptx_path: str, pdf_path: str):
    """Convert PPTX file to PDF using PowerPoint automation"""
    try:
        if platform.system() == "Windows":
            try:
                import comtypes.client
                import comtypes
                import time
                
                # Initialize COM for this thread
                comtypes.CoInitialize()
                
                # Ensure absolute paths
                pptx_abs_path = os.path.abspath(pptx_path)
                pdf_abs_path = os.path.abspath(pdf_path)
                
                # Check if source file exists
                if not os.path.exists(pptx_abs_path):
                    raise Exception(f"Source PPTX file not found: {pptx_abs_path}")
                
                print(f"Converting {pptx_abs_path} to {pdf_abs_path}")
                
                # Initialize PowerPoint application with error handling
                powerpoint = None
                presentation = None
                
                try:
                    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
                    powerpoint.Visible = True  # Must be visible for some PowerPoint versions
                    powerpoint.DisplayAlerts = False  # Disable alerts that might block automation
                    time.sleep(2)  # Give PowerPoint more time to initialize
                    
                    # Open the presentation
                    presentation = powerpoint.Presentations.Open(pptx_abs_path, ReadOnly=True, Untitled=False, WithWindow=False)
                    time.sleep(2)  # Give time to fully load
                    
                    # Try SaveAs method first (simpler)
                    try:
                        # Use absolute path and ensure directory exists
                        pdf_dir = os.path.dirname(pdf_abs_path)
                        os.makedirs(pdf_dir, exist_ok=True)
                        
                        presentation.SaveAs(pdf_abs_path, 32)  # 32 = ppSaveAsPDF
                        time.sleep(3)  # Wait longer for file to be written
                        print("Used SaveAs method for PDF conversion")
                    except Exception as save_error:
                        print(f"SaveAs failed: {save_error}, trying ExportAsFixedFormat...")
                        # Fallback to ExportAsFixedFormat
                        presentation.ExportAsFixedFormat(
                            OutputFileName=pdf_abs_path,
                            FixedFormatType=2,  # ppFixedFormatTypePDF
                            Intent=1,  # ppFixedFormatIntentPrint
                            FrameSlides=False,
                            HandoutOrder=1,
                            OutputType=1,  # ppPrintOutputSlides
                            PrintHiddenSlides=False,
                            PrintRange=None,
                            RangeType=1,  # ppPrintAll
                            SlideShowName="",
                            IncludeDocProps=True,
                            KeepIRMSettings=True,
                            DocStructureTags=True,
                            BitmapMissingFonts=True,
                            UseDocumentICCProfile=False
                        )
                        time.sleep(3)  # Wait for export to complete
                        print("Used ExportAsFixedFormat method for PDF conversion")
                    
                    # Wait longer for the export to complete and file to be flushed
                    time.sleep(3)
                    
                    # Verify PDF was created and is valid
                    max_attempts = 10
                    for attempt in range(max_attempts):
                        if os.path.exists(pdf_abs_path):
                            file_size = os.path.getsize(pdf_abs_path)
                            if file_size > 1000:  # PDF should be at least 1KB
                                # Try to verify it's a valid PDF by checking header
                                try:
                                    with open(pdf_abs_path, 'rb') as f:
                                        header = f.read(5)
                                        if header.startswith(b'%PDF-'):
                                            print(f"Successfully converted to PDF: {pdf_abs_path}")
                                            return True
                                        else:
                                            print(f"Invalid PDF header: {header}")
                                except Exception as read_error:
                                    print(f"Cannot read PDF file: {read_error}")
                            else:
                                print(f"PDF file too small ({file_size} bytes), waiting...")
                        
                        time.sleep(1)  # Wait before retrying
                    
                    raise Exception("PDF file was not created properly or is invalid")
                        
                except Exception as ppt_error:
                    raise Exception(f"PowerPoint automation failed: {ppt_error}")
                    
                finally:
                    # Clean up PowerPoint process with more thorough cleanup
                    try:
                        if 'presentation' in locals() and presentation:
                            presentation.Close()
                            time.sleep(1)
                        if 'powerpoint' in locals() and powerpoint:
                            powerpoint.Quit()
                            time.sleep(2)  # Give more time for cleanup
                    except Exception as cleanup_error:
                        print(f"Cleanup warning: {cleanup_error}")
                        pass
                    
                    # Uninitialize COM
                    try:
                        comtypes.CoUninitialize()
                    except:
                        pass
                    
            except ImportError:
                raise Exception("comtypes not available for PDF conversion - install with: pip install comtypes")
            except Exception as e:
                raise Exception(f"PDF conversion error: {e}")
        else:
            raise Exception("PDF conversion only supported on Windows with PowerPoint installed")
            
    except Exception as e:
        print(f"PDF conversion error: {e}")
        raise

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(parent_dir / '.env')
except ImportError:
    print("Warning: python-dotenv not installed, environment variables might not load")

import json
import tempfile
import threading
import uuid
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any
import traceback

# Import your existing PowerPoint generator functions
try:
    from ppt_maker_flo import (
        ChatGoogleGenerativeAI,
        create_enhanced_ppt,
        parse_slides_enhanced,
        extract_text_from_llm_output,
        create_enhanced_few_shot_prompt,
        predict_num_slides,
        THEMES,
        TEXT_SIZES
    )
except ImportError as e:
    print(f"Error importing ppt_maker_flo: {e}")
    print("Current working directory:", os.getcwd())
    print("Python path:", sys.path)
    raise

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure logging for production
if os.environ.get('DYNO'):  # Running on Heroku
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Add memory monitoring
    import psutil
    logger.info(f"Memory usage: {psutil.virtual_memory().percent}%")
    logger.info(f"Available memory: {psutil.virtual_memory().available / 1024 / 1024:.1f} MB")

# Global variables for job tracking
active_jobs: Dict[str, Dict] = {}
job_results: Dict[str, Dict] = {}

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'docx', 'pdf'}

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """Clean up files older than 24 hours"""
    try:
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=24)
        
        # Use environment-appropriate paths
        if os.environ.get('DYNO'):  # Check if running on Heroku
            upload_folder = '/tmp'  # On Heroku, use /tmp for both uploads and outputs
            output_folder = '/tmp'
        else:
            upload_folder = 'uploads'
            output_folder = 'outputs'
        
        # Clean upload folder
        if os.path.exists(upload_folder):
            for filename in os.listdir(upload_folder):
                filepath = os.path.join(upload_folder, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        logger.info(f"Cleaned up old upload: {filename}")
        
        # Clean output folder
        if os.path.exists(output_folder):
            for filename in os.listdir(output_folder):
                filepath = os.path.join(output_folder, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        logger.info(f"Cleaned up old output: {filename}")
                    
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def read_document_content(filepath: str) -> str:
    """Read content from uploaded document"""
    try:
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
                
        elif ext == '.docx':
            try:
                from docx import Document as DocxDocument
                doc = DocxDocument(filepath)
                return "\n".join([para.text for para in doc.paragraphs])
            except ImportError:
                logger.error("python-docx not installed for .docx support")
                return "Error: python-docx not installed for .docx support"
            except Exception as e:
                logger.error(f"Error reading .docx file: {e}")
                return f"Error reading .docx file: {str(e)}"
                
        elif ext == '.pdf':
            try:
                import PyPDF2
                with open(filepath, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                logger.error("PyPDF2 not installed for PDF support")
                return "Error: PyPDF2 not installed for PDF support"
            except Exception as e:
                logger.error(f"Error reading PDF file: {e}")
                return f"Error reading PDF file: {str(e)}"
        else:
            return "Unsupported file format"
            
    except Exception as e:
        logger.error(f"Error reading document {filepath}: {e}")
        return f"Error reading document: {str(e)}"

def generate_presentation_content(config: Dict) -> str:
    """Generate presentation content using AI"""
    try:
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.0
        )
        
        if config.get('doc_content'):
            # Use document content with few-shot examples for consistent formatting
            logger.info(f"Generating content from document using few-shot examples")
            
            # Use few-shot prompt for document summarization
            few_shot_prompt = create_enhanced_few_shot_prompt()
            
            # Modify the suffix to handle document content
            from langchain.prompts import PromptTemplate
            
            # Create a custom prompt that includes examples but handles document content
            doc_template = f"""Here are examples of how to create presentations:

{few_shot_prompt.prefix}

{chr(10).join([few_shot_prompt.example_prompt.format(**example) for example in few_shot_prompt.examples])}

Now, create a {{num_slides}}-slide PowerPoint presentation by summarizing the following document content.
Follow the exact same format as shown in the examples above.

Document Content:
{{doc_content}}

Topic: Document Summary
Number of slides: {{num_slides}}
Tone: {{tone}}
Target audience: {{audience}}
Theme: {{theme}}

Create a {{num_slides}}-slide presentation following the exact format shown. Include image_query and flowchart_description where appropriate.
"""
            
            doc_prompt = PromptTemplate(
                input_variables=["doc_content", "num_slides", "tone", "audience", "theme"],
                template=doc_template
            )
            
            chain = doc_prompt | llm
            output = chain.invoke({
                "doc_content": config["doc_content"],
                "num_slides": config["num_slides"],
                "tone": config["tone"],
                "audience": config["audience"],
                "theme": config["theme"]
            })
            
        else:
            # Generate from topic using few-shot prompts
            logger.info(f"Generating content for topic: {config.get('topic')}")
            
            # Use the enhanced few-shot prompt
            few_shot_prompt = create_enhanced_few_shot_prompt()
            chain = few_shot_prompt | llm
            
            prompt_input = {
                "topic": config["topic"],
                "num_slides": config["num_slides"],
                "tone": config["tone"],
                "audience": config["audience"],
                "theme": config["theme"]
            }
            logger.info(f"Using few-shot prompt with input: {prompt_input}")
            
            output = chain.invoke(prompt_input)
        
        logger.info(f"LLM output type: {type(output)}")
        logger.info(f"LLM output: {str(output)[:500]}...")
        
        extracted_text = extract_text_from_llm_output(output)
        logger.info(f"Extracted text length: {len(extracted_text) if extracted_text else 0}")
        
        return extracted_text
        
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        raise

def process_presentation_job(job_id: str, config: Dict):
    """Background task to process presentation generation"""
    try:
        print(f"Starting job processing for job_id: {job_id}")
        
        # Ensure job exists in active_jobs
        if job_id not in active_jobs:
            print(f"WARNING: Job {job_id} not found in active_jobs at start of processing")
            active_jobs[job_id] = {
                'status': 'started',
                'progress': 0,
                'created_at': datetime.now().isoformat(),
                'config': config
            }
        
        # Update job status
        active_jobs[job_id]['status'] = 'generating_content'
        active_jobs[job_id]['progress'] = 20
        print(f"Job {job_id}: Updated status to generating_content")
        
        # Generate content
        logger.info(f"Job {job_id}: Generating AI content")
        content = generate_presentation_content(config)
        
        active_jobs[job_id]['status'] = 'parsing_content'
        active_jobs[job_id]['progress'] = 40
        
        # Parse slides
        logger.info(f"Job {job_id}: Parsing slide content")
        slides_data = parse_slides_enhanced(content)
        
        if not slides_data:
            raise Exception("Could not parse slide content")
        
        active_jobs[job_id]['status'] = 'creating_presentation'
        active_jobs[job_id]['progress'] = 60
        
        # Create presentation
        logger.info(f"Job {job_id}: Creating presentation")
        
        # Set output folder based on environment
        if os.environ.get('DYNO'):  # Check if running on Heroku
            output_folder = '/tmp'
        else:
            output_folder = 'outputs'
            os.makedirs(output_folder, exist_ok=True)
        
        # Get file format from config (default to pptx)
        file_format = config.get('file_format', 'pptx')
        
        # Create the full path where we want the file to be saved
        user_filename = config['filename']
        
        # Remove any existing extension and add the correct one
        base_filename = user_filename.split('.')[0] if '.' in user_filename else user_filename
        
        if file_format == 'pdf':
            final_extension = '.pdf'
        else:
            final_extension = '.pptx'
            file_format = 'pptx'  # Ensure we use pptx for the creation
        
        # Create output filename with job ID
        if os.environ.get('DYNO'):  # Check if running on Heroku
            # On Heroku, use forward slashes and construct path manually to avoid Windows path issues
            output_filename = f"/tmp/{job_id}_{base_filename}"
        else:
            # On local development, use os.path.join for proper path construction
            output_filename = os.path.join(output_folder, f"{job_id}_{base_filename}")
        
        # Process flowcharts - convert simple format to Mermaid if needed
        processed_flowcharts = []
        flowcharts = config.get('flowcharts', [])
        logger.info(f"Processing {len(flowcharts)} flowcharts")
        
        for i, flowchart in enumerate(flowcharts):
            logger.info(f"Processing flowchart {i+1}: {flowchart}")
            if isinstance(flowchart, dict) and 'description' in flowchart:
                original_desc = flowchart['description']
                logger.info(f"Original flowchart description: {original_desc[:100]}...")
                
                converted_desc = convert_simple_flowchart_to_mermaid(original_desc)
                if converted_desc:
                    processed_flowcharts.append({
                        'title': flowchart.get('title', 'Flowchart'),
                        'description': converted_desc
                    })
                    logger.info(f"Successfully converted simple flowchart format to Mermaid")
                    logger.info(f"Converted description: {converted_desc[:100]}...")
                else:
                    # Keep original if conversion failed
                    processed_flowcharts.append(flowchart)
                    logger.warning(f"Flowchart conversion failed, using original format")
            else:
                processed_flowcharts.append(flowchart)
                logger.info(f"Using flowchart as-is (not dict or missing description)")
        
        logger.info(f"Final processed flowcharts: {len(processed_flowcharts)}")
        
        # Convert flowcharts from dict format to tuple format for create_enhanced_ppt
        flowcharts_tuples = []
        for flowchart in processed_flowcharts:
            if isinstance(flowchart, dict):
                title = flowchart.get('title', 'Flowchart')
                description = flowchart.get('description', '')
                flowcharts_tuples.append((title, description))
                logger.info(f"Converted flowchart: {title}")
            else:
                logger.warning(f"Unexpected flowchart format: {type(flowchart)}")
        
        logger.info(f"Final flowcharts for PPT creation: {len(flowcharts_tuples)} tuples")
        
        # Pass the full path (without extension) to create_enhanced_ppt
        create_enhanced_ppt(
            slides_data=slides_data,
            filename=output_filename,
            output_format=file_format,
            theme=config['theme'],
            text_size=config['text_size'],
            flowcharts=flowcharts_tuples
        )
        
        # Handle PDF conversion if requested
        if config.get('file_format') == 'pdf':
            logger.info(f"Job {job_id}: Converting to PDF")
            active_jobs[job_id]['status'] = 'converting_to_pdf'
            active_jobs[job_id]['progress'] = 80
            
            pptx_file = f"{output_filename}.pptx"
            pdf_file = f"{output_filename}.pdf"
            
            try:
                # Verify PPTX file exists before conversion
                if not os.path.exists(pptx_file):
                    raise Exception(f"PPTX file not found for conversion: {pptx_file}")
                
                logger.info(f"Converting PPTX to PDF: {pptx_file} -> {pdf_file}")
                
                # Convert PPTX to PDF
                success = convert_pptx_to_pdf(pptx_file, pdf_file)
                
                if not success:
                    raise Exception("PDF conversion returned failure status")
                
                # Verify PDF was created successfully
                if not os.path.exists(pdf_file):
                    raise Exception("PDF file was not created")
                
                pdf_size = os.path.getsize(pdf_file)
                if pdf_size == 0:
                    raise Exception("PDF file is empty")
                
                # Additional verification: Check if it's a valid PDF
                try:
                    with open(pdf_file, 'rb') as f:
                        header = f.read(10)
                        if not header.startswith(b'%PDF-'):
                            raise Exception(f"Invalid PDF file format. Header: {header}")
                except Exception as verify_error:
                    raise Exception(f"PDF verification failed: {verify_error}")
                
                logger.info(f"PDF created successfully: {pdf_file} ({pdf_size} bytes)")
                
                # Remove the temporary PPTX file
                try:
                    if os.path.exists(pptx_file):
                        os.remove(pptx_file)
                        logger.info(f"Removed temporary PPTX file: {pptx_file}")
                except Exception as cleanup_error:
                    logger.warning(f"Could not remove temporary PPTX file: {cleanup_error}")
                    
                final_output_filename = f"{job_id}_{base_filename}.pdf"
                final_filepath = pdf_file
                logger.info(f"PDF conversion successful: {final_filepath}")
                
            except Exception as pdf_error:
                logger.error(f"PDF conversion failed: {pdf_error}")
                logger.warning("Falling back to PPTX format")
                
                # Clean up any partial PDF file
                try:
                    if os.path.exists(pdf_file):
                        os.remove(pdf_file)
                except:
                    pass
                
                final_output_filename = f"{job_id}_{base_filename}.pptx"
                final_filepath = pptx_file
        else:
            final_output_filename = f"{job_id}_{base_filename}.pptx"
            if os.environ.get('DYNO'):  # Check if running on Heroku
                final_filepath = f"/tmp/{job_id}_{base_filename}.pptx"
            else:
                final_filepath = f"{output_filename}.pptx"
        
        active_jobs[job_id]['status'] = 'completed'
        active_jobs[job_id]['progress'] = 100
        
        # Store results with the correct filename
        job_results[job_id] = {
            'status': 'completed',
            'filename': final_output_filename,
            'filepath': final_filepath,
            'slides_count': len(slides_data),
            'created_at': datetime.now().isoformat(),
            'config': config
        }
        
        logger.info(f"Job {job_id}: Completed successfully")
        print(f"Job {job_id}: Moved from active_jobs to job_results")
        print(f"Active jobs remaining: {list(active_jobs.keys())}")
        print(f"Completed jobs: {list(job_results.keys())}")
        
        # Remove from active jobs
        if job_id in active_jobs:
            del active_jobs[job_id]
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        print(f"Job {job_id} FAILED: {e}")
        
        # Ensure job failure is recorded
        if job_id in active_jobs:
            active_jobs[job_id]['status'] = 'failed'
            active_jobs[job_id]['error'] = str(e)
        
        job_results[job_id] = {
            'status': 'failed',
            'error': str(e),
            'created_at': datetime.now().isoformat()
        }

# Utility functions for external use
class PPTGeneratorAPI:
    """Utility class for easier API integration"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
    
    def health_check(self):
        """Check if API is healthy"""
        import requests
        try:
            response = requests.get(f"{self.base_url}/api/health")
            return response.status_code == 200
        except:
            return False
    
    def get_config(self):
        """Get available configuration options"""
        import requests
        response = requests.get(f"{self.base_url}/api/config")
        return response.json() if response.status_code == 200 else None
    
    def upload_document(self, file_path: str):
        """Upload document file"""
        import requests
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.base_url}/api/upload", files=files)
        return response.json()
    
    def generate_presentation(self, config: Dict):
        """Start presentation generation"""
        import requests
        response = requests.post(f"{self.base_url}/api/generate", json=config)
        return response.json()
    
    def get_job_status(self, job_id: str):
        """Get job status"""
        import requests
        response = requests.get(f"{self.base_url}/api/status/{job_id}")
        return response.json()
    
    def download_presentation(self, job_id: str, save_path: str):
        """Download completed presentation"""
        import requests
        response = requests.get(f"{self.base_url}/api/download/{job_id}")
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        return False

def convert_simple_flowchart_to_mermaid(description: str) -> str:
    """Convert simple flowchart format (A->B;B->C) to Mermaid syntax"""
    try:
        logger.info(f"Converting flowchart: {description[:50]}...")
        
        # If it already looks like Mermaid syntax, return as-is
        if description.strip().lower().startswith(('flowchart', 'graph', 'sequencediagram')):
            logger.info("Input appears to be valid Mermaid syntax, returning as-is")
            return description
        
        # Clean the input
        description = description.strip()
        if not description:
            logger.warning("Empty flowchart description provided")
            return None
        
        # Parse simple format like "A->B;B->C" or "Start->Process->End"
        connections = []
        
        # Split by semicolon, comma, or newline
        parts = re.split(r'[;\n,]', description)
        logger.info(f"Split into {len(parts)} parts: {parts}")
        
        nodes = set()
        edges = []
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            # Handle different arrow formats: ->, →, -->, =>
            if '->' in part:
                arrow_parts = part.split('->')
            elif '→' in part:
                arrow_parts = part.split('→')
            elif '-->' in part:
                arrow_parts = part.split('-->')
            elif '=>' in part:
                arrow_parts = part.split('=>')
            else:
                # Single nodes or no arrows, skip
                logger.warning(f"No arrows found in part: {part}")
                continue
                
            for i in range(len(arrow_parts) - 1):
                from_node = arrow_parts[i].strip()
                to_node = arrow_parts[i + 1].strip()
                
                if from_node and to_node:
                    # Clean node names (remove special characters that might break Mermaid)
                    from_clean = re.sub(r'[^\w\s-]', '', from_node).strip()
                    to_clean = re.sub(r'[^\w\s-]', '', to_node).strip()
                    
                    # Create node IDs (replace spaces with underscores)
                    from_id = re.sub(r'\s+', '_', from_clean)
                    to_id = re.sub(r'\s+', '_', to_clean)
                    
                    if from_id and to_id:
                        nodes.add((from_id, from_clean))
                        nodes.add((to_id, to_clean))
                        edges.append((from_id, to_id))
                        logger.debug(f"Added edge: {from_id} -> {to_id}")
        
        if not edges:
            # If no valid connections found, return None
            logger.warning("No valid edges found in flowchart description")
            return None
        
        logger.info(f"Found {len(nodes)} nodes and {len(edges)} edges")
        
        # Generate Mermaid flowchart
        mermaid_lines = ['flowchart TD']
        
        # Add node definitions (use brackets for better readability)
        for node_id, node_label in nodes:
            if node_label.lower() in ['start', 'begin']:
                mermaid_lines.append(f'    {node_id}([{node_label}])')
            elif node_label.lower() in ['end', 'finish', 'stop']:
                mermaid_lines.append(f'    {node_id}([{node_label}])')
            elif '?' in node_label or 'decision' in node_label.lower():
                mermaid_lines.append(f'    {node_id}{{{node_label}}}')
            else:
                mermaid_lines.append(f'    {node_id}[{node_label}]')
        
        # Add connections
        for from_id, to_id in edges:
            mermaid_lines.append(f'    {from_id} --> {to_id}')
        
        result = '\n'.join(mermaid_lines)
        logger.info(f"Successfully converted to Mermaid: {len(mermaid_lines)} lines")
        return result
        
    except Exception as e:
        logger.error(f"Error converting simple flowchart: {e}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        return None
