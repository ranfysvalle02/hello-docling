from flask import Flask, request, jsonify, render_template_string
from docling.document_converter import DocumentConverter
import io
import tempfile
import os

app = Flask(__name__)

# HTML template for the upload form with reset functionality and enhanced Markdown UX
HTML_TEMPLATE = '''
<!doctype html>
<html>
<head>
<style>
        body {
            font-family: Arial, sans-serif;
            background-color: #ffffff;
            color: #333;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }

        h2 {
            color: #444;
            text-align: center;
            margin-bottom: 20px;
        }

        #upload-form {
            width: 100%;
            max-width: 500px;
            padding: 20px;
            background-color: #f7f7f7;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        #upload-form input[type=file] {
            margin-bottom: 15px;
            padding: 5px;
            width: 100%;
        }

        #upload-form input[type=submit] {
            color: #fff;
            background-color: #007bff;
            padding: 10px 20px;
            cursor: pointer;
            border: none;
            border-radius: 5px;
            transition: background-color 0.3s ease;
            width: 100%;
        }

        #upload-form input[type=submit]:hover {
            background-color: #0056b3;
        }

        #result-container {
            width: 100%;
            max-width: 800px;
            margin-top: 30px;
            padding: 20px;
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        }

        #result {
            width: 100%;
            overflow-wrap: break-word;
        }

        #reset-button {
            margin-top: 20px;
            color: #fff;
            background-color: #dc3545;
            padding: 10px 20px;
            cursor: pointer;
            border: none;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }

        #reset-button:hover {
            background-color: #c82333;
        }

        pre {
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
    <!-- Include Marked.js for Markdown rendering -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
    <body>
        <img src="https://miro.medium.com/v2/resize:fit:1400/1*GqxSyaTgPykfixHqJ1vmKg.png" style="width: 50%; margin-bottom: 20px;">
        <h2>Upload File to Extract Markdown</h2>
        <form id="upload-form" enctype="multipart/form-data">
            <input type="file" name="file" accept="*" required>
            <input type="submit" value="Extract Markdown">
        </form>
        <div id="result-container" style="display: none;">
            <div id="result"></div>
            <button id="reset-button">Reset</button>
        </div>

        <script>
            document.getElementById('upload-form').onsubmit = function(e) {
                e.preventDefault();
                var formData = new FormData(this);
                fetch('/extract_markdown', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.markdown) {
                        // Render Markdown to HTML
                        var htmlContent = marked.parse(data.markdown);
                        document.getElementById('result').innerHTML = htmlContent;
                        document.getElementById('result-container').style.display = 'block';
                        // Scroll to the result
                        document.getElementById('result-container').scrollIntoView({ behavior: 'smooth' });
                    } else {
                        document.getElementById('result').innerText = data.error;
                        document.getElementById('result-container').style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('result').innerText = 'An unexpected error occurred.';
                    document.getElementById('result-container').style.display = 'block';
                });
            };

            document.getElementById('reset-button').onclick = function() {
                // Clear the result and hide the container
                document.getElementById('result').innerHTML = '';
                document.getElementById('result-container').style.display = 'none';
                // Reset the form
                document.getElementById('upload-form').reset();
            };
        </script>
    </body>
</html>
'''

@app.route('/', methods=['GET'])
def upload_form():
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract_markdown', methods=['POST'])
def extract_markdown():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file:
        try:
            # Save the uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name

            # Process the file using docling
            converter = DocumentConverter()
            result = converter.convert(temp_file_path)
            markdown_content = result.document.export_to_markdown()

            return jsonify({"markdown": markdown_content})
        except Exception as e:
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500
        finally:
            # Clean up the temporary file
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)

    return jsonify({"error": "Invalid file type."}), 400

if __name__ == '__main__':
    app.run(debug=True)
