#!/usr/bin/env python
"""
Freelance Python Contributor Project Aurora
Generated for job: rok_1096434 on 2025-09-21 05:09:08
"""

from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# In-memory storage for submitted code snippets
code_snippets = []

@app.route('/submit_code', methods=['POST'])
def submit_code():
    """
    Endpoint to submit a code snippet for evaluation.
    
    Request JSON format:
    {
        "language": "python",
        "code": "print('Hello, World!')"
    }
    
    Returns:
        JSON response with submission status and message.
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate input
        if 'language' not in data or 'code' not in data:
            return jsonify({"status": "error", "message": "Missing 'language' or 'code' in request"}), 400
        
        language = data['language']
        code = data['code']
        
        # Store the code snippet
        code_snippets.append({"language": language, "code": code})
        
        logging.info(f"Code submitted: {language} - {code}")
        
        return jsonify({"status": "success", "message": "Code snippet submitted successfully!"}), 201

    except Exception as e:
        logging.error(f"Error submitting code: {str(e)}")
        return jsonify({"status": "error", "message": "An error occurred while submitting code."}), 500

@app.route('/get_snippets', methods=['GET'])
def get_snippets():
    """
    Endpoint to retrieve all submitted code snippets.
    
    Returns:
        JSON response with the list of submitted code snippets.
    """
    try:
        return jsonify({"status": "success", "snippets": code_snippets}), 200

    except Exception as e:
        logging.error(f"Error retrieving snippets: {str(e)}")
        return jsonify({"status": "error", "message": "An error occurred while retrieving snippets."}), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)