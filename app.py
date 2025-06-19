"""RO2 Table Converter - Web Interface"""

import logging
from pathlib import Path
from typing import Dict, Any, List
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from datetime import datetime

from asset.ct_processor import CTProcessor
from asset.xlsx_processor import XLSXProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ro2-table-converter-secret-key-2025'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Define directories as Path objects
UPLOAD_FOLDER = Path('uploads')
OUTPUT_FOLDER = Path('outputs')

# Ensure directories exist
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

# Supported file extensions
ALLOWED_EXTENSIONS = {'.ct', '.xlsx'}


class WebConverter:
    """Web-based file converter with improved naming and workflow."""
    
    @staticmethod
    def is_allowed_file(filename: str) -> bool:
        """Check if the file extension is supported."""
        return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_smart_output_name(input_path: Path, target_extension: str) -> str:
        """
        Generate smart output filename without redundant '_converted' suffix.
        
        Args:
            input_path: Input file path
            target_extension: Target file extension (.xlsx or .ct)
            
        Returns:
            Smart output filename
        """
        base_name = input_path.stem
          # Remove '_converted' suffix if present
        if base_name.endswith('_converted'):
            base_name = base_name[:-10]  # Remove '_converted'
        
        output_name = f"{base_name}{target_extension}"
        
        # Simple collision handling
        # This keeps filenames clean without timestamps
        
        return output_name
    @staticmethod
    def convert_file(input_path: Path) -> Dict[str, Any]:
        """
        Convert a single file based on its extension.
        
        Args:
            input_path: Path to the input file
            
        Returns:
            Dictionary with conversion result
        """
        try:
            print(f"🔄 Converting file: {input_path}")
            file_ext = input_path.suffix.lower()
            print(f"📋 File extension: {file_ext}")
            
            if file_ext == '.ct':
                print("🔄 Starting CT → XLSX conversion")
                return WebConverter._convert_ct_to_xlsx(input_path)
            elif file_ext == '.xlsx':
                print("🔄 Starting XLSX → CT conversion")
                return WebConverter._convert_xlsx_to_ct(input_path)
            else:
                print(f"❌ Unsupported extension: {file_ext}")
                return {
                    'success': False,
                    'error': f'Unsupported file extension: {file_ext}',
                    'filename': input_path.name
                }
                
        except Exception as e:
            print(f"💥 Error converting {input_path}: {e}")
            logger.error(f"Error converting {input_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'filename': input_path.name
            }
    
    @staticmethod
    def _convert_ct_to_xlsx(input_path: Path) -> Dict[str, Any]:
        """Convert CT file to XLSX format."""
        try:
            print(f"📖 Reading CT file: {input_path}")
            
            # Read CT file
            ct_processor = CTProcessor(str(input_path), verbose=False)
            data = ct_processor.read()
            print(f"✅ CT read complete: {len(data[1]) if data and len(data) > 1 else 0} rows")
            
            if not data or not data[0]:
                print("❌ Invalid or empty CT file")
                raise ValueError("Invalid or empty CT file")
            
            # Generate smart output name
            output_name = WebConverter.get_smart_output_name(input_path, '.xlsx')
            output_path = OUTPUT_FOLDER / output_name
            print(f"📝 Writing XLSX to: {output_path}")
            # Write XLSX file
            xlsx_processor = XLSXProcessor(str(output_path), verbose=False)
            xlsx_processor.write(data)
            print(f"✅ XLSX written successfully")
            
            logger.info(f"Successfully converted CT to XLSX: {output_name}")
            
            result: Dict[str, Any] = {
                'success': True,
                'input_file': input_path.name,
                'output_file': output_name,
                'conversion_type': 'CT → XLSX',
                'file_size': output_path.stat().st_size,
                'download_url': f'/download/{output_name}'
            }
            print(f"🎯 CT conversion result: {result}")
            return result
            
        except Exception as e:
            print(f"💥 CT conversion error: {e}")
            logger.error(f"Error converting CT to XLSX: {e}")
            raise
    @staticmethod
    def _convert_xlsx_to_ct(input_path: Path) -> Dict[str, Any]:
        """Convert XLSX file to CT format."""
        try:
            print(f"📖 Reading XLSX file: {input_path}")
            
            # Read XLSX file
            xlsx_processor = XLSXProcessor(str(input_path), verbose=False)
            data = xlsx_processor.read()
            print(f"✅ XLSX read complete: {len(data[1]) if data and len(data) > 1 else 0} rows")
            
            if not data or not data[0]:
                print("❌ Invalid or empty XLSX file")
                raise ValueError("Invalid or empty XLSX file")
            
            # Generate smart output name
            output_name = WebConverter.get_smart_output_name(input_path, '.ct')
            output_path = OUTPUT_FOLDER / output_name
            print(f"📝 Writing CT to: {output_path}")
              # Write CT file
            ct_processor = CTProcessor(str(output_path), verbose=False)
            ct_processor.write(data)
            print(f"✅ CT written successfully")
            
            logger.info(f"Successfully converted XLSX to CT: {output_name}")
            
            result: Dict[str, Any] = {
                'success': True,
                'input_file': input_path.name,
                'output_file': output_name,
                'conversion_type': 'XLSX → CT',
                'file_size': output_path.stat().st_size,
                'download_url': f'/download/{output_name}'
            }
            print(f"🎯 XLSX conversion result: {result}")
            return result
            
        except Exception as e:
            print(f"💥 XLSX conversion error: {e}")
            logger.error(f"Error converting XLSX to CT: {e}")
            raise


@app.route('/')
def index():
    """Main page with drag & drop interface."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads and conversions."""
    try:
        print("🔄 Upload request received")
        print(f"📋 Request method: {request.method}")
        print(f"📋 Request content type: {request.content_type}")
        print(f"📋 Request form keys: {list(request.form.keys())}")
        print(f"📋 Request files keys: {list(request.files.keys())}")
          # Handle both 'files' and 'files[0]', 'files[1]', etc. keys
        files: List[FileStorage] = []
        if 'files' in request.files:
            files = request.files.getlist('files')
            print(f"📁 Found 'files' key with {len(files)} files")
        else:
            # Handle files[0], files[1], etc. format from Dropzone
            file_keys = [key for key in request.files.keys() if key.startswith('files[')]
            for key in sorted(file_keys):  # Sort to maintain order
                file_obj = request.files[key]
                files.append(file_obj)
            print(f"📁 Found {len(files)} files from indexed keys: {file_keys}")
        
        if not files:
            print("❌ No files found in request")
            return jsonify({'success': False, 'error': 'No files provided'})
        
        print(f"📁 Total files to process: {len(files)}")
        
        # Debug each file
        for i, file in enumerate(files):
            print(f"📄 File {i}: filename='{file.filename}', content_type='{file.content_type}'")
        
        if all(f.filename == '' for f in files):
            print("❌ No valid files selected")
            return jsonify({'success': False, 'error': 'No files selected'})
        
        results: List[Dict[str, Any]] = []
        
        for i, file in enumerate(files):
            print(f"📄 Processing file {i+1}/{len(files)}: {file.filename}")
            
            if file and file.filename and WebConverter.is_allowed_file(file.filename):
                print(f"✅ File {file.filename} is allowed")
                
                # Secure the filename
                filename = secure_filename(file.filename)
                print(f"🔒 Secured filename: {filename}")
                
                # Save uploaded file
                input_path = UPLOAD_FOLDER / filename
                print(f"💾 Saving to: {input_path}")
                file.save(str(input_path))
                print(f"✅ File saved successfully")
                
                # Convert the file
                print(f"🔄 Starting conversion...")
                result = WebConverter.convert_file(input_path)
                print(f"🎯 Conversion result: {result}")
                results.append(result)
                
                # Clean up uploaded file
                try:
                    input_path.unlink()
                    print(f"🗑️ Cleaned up uploaded file")
                except Exception as cleanup_error:
                    print(f"⚠️ Could not clean up file: {cleanup_error}")
                    pass
            else:
                print(f"❌ File {file.filename} is not allowed or invalid")
                results.append({
                    'success': False,
                    'error': 'Invalid file type',
                    'filename': file.filename or 'Unknown'
                })
        
        successful_count = sum(1 for r in results if r.get('success'))
        print(f"📊 Results: {successful_count}/{len(results)} successful conversions")
        
        response: Dict[str, Any] = {
            'success': True,
            'results': results,
            'total_files': len(results),
            'successful_conversions': successful_count
        }
        print(f"📤 Sending response: {response}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in upload_files: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/download/<filename>')
def download_file(filename: str):
    """Download converted files."""
    try:
        file_path = OUTPUT_FOLDER / secure_filename(filename)
        if file_path.exists():
            return send_file(str(file_path), as_attachment=True)
        else:
            flash('File not found', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {e}")
        flash('Error downloading file', 'error')
        return redirect(url_for('index'))


@app.route('/api/status')
def api_status():
    """API endpoint for application status."""
    return jsonify({
        'status': 'online',
        'version': '2.0.0',
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'timestamp': datetime.now().isoformat()
    })


@app.errorhandler(413)
def too_large(e: Exception):
    """Handle file too large errors."""
    return jsonify({'success': False, 'error': 'File too large (max 100MB)'}), 413


@app.errorhandler(500)
def internal_error(e: Exception):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {e}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("🚀 Starting RO2 Table Converter Web Interface...")
    print("📂 Upload folder:", UPLOAD_FOLDER.absolute())
    print("📁 Output folder:", OUTPUT_FOLDER.absolute())
    print("🌐 Open your browser to: http://localhost:8080")
    print("✨ Ready for file conversions!")
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
        use_reloader=True
    )
