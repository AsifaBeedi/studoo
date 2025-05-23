from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import logging
import json
import sys
import os
import subprocess

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# --- Database Connection ---
def get_db():
    conn = sqlite3.connect('study_planner.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Database Initialization ---
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            subjects TEXT,
            weaknesses TEXT,
            exam_dates TEXT,
            generated_plan TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# --- API: Generate Study Plan ---
@app.route('/api/generate_plan', methods=['POST'])
def generate_plan():
    try:
        logger.info("Received request to generate plan")
        
        # Get raw data and parse JSON manually
        raw_data = request.get_data(as_text=True)
        logger.info(f"Raw request data: {raw_data}")
        
        if not raw_data:
            logger.error("No data received in request")
            return jsonify({
                "error": "No data received",
                "details": {
                    "raw_request": raw_data
                }
            }), 400
            
        try:
            data = json.loads(raw_data)
            logger.info(f"Parsed request data: {json.dumps(data)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return jsonify({
                "error": f"Invalid JSON: {str(e)}",
                "details": {
                    "raw_request": raw_data,
                    "error_type": str(type(e))
                }
            }), 400

        if not data or 'subjects' not in data:
            logger.error("Missing subjects in request")
            return jsonify({
                "error": "Missing subjects",
                "details": {
                    "received_data": data
                }
            }), 400

        try:
            import subprocess
            
            # Convert input data to JSON string
            input_data = json.dumps(data)
            logger.info(f"Sending data to ML model: {input_data}")
            
            # Call the ML model script
            try:
                # Get the full path to the Python interpreter
                python_path = sys.executable
                logger.info(f"Using Python interpreter: {python_path}")
                
                # Get the full path to the ML model script
                ml_model_path = os.path.join(os.path.dirname(__file__), 'ml_model.py')
                logger.info(f"ML model script path: {ml_model_path}")
                
                # Verify the script exists
                if not os.path.exists(ml_model_path):
                    logger.error(f"ML model script not found at: {ml_model_path}")
                    return jsonify({
                        "error": "ML model script not found",
                        "details": {
                            "path": ml_model_path
                        }
                    }), 500
                
                result = subprocess.run(
                    [python_path, ml_model_path, input_data],
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=os.path.dirname(__file__)  # Set current working directory
                )
                
                logger.info(f"ML model execution successful")
                logger.info(f"ML model stdout: {result.stdout}")
                logger.info(f"ML model stderr: {result.stderr}")
                logger.info(f"ML model return code: {result.returncode}")
                
                # Parse the model's output
                try:
                    plan = json.loads(result.stdout)
                    logger.info(f"Successfully parsed plan: {plan}")
                    
                    # Clean up the plan to remove duplicate entries
                    cleaned_plan = {}
                    for date, sessions in plan.get('plan', {}).items():
                        cleaned_sessions = []
                        seen_sessions = set()
                        
                        for session in sessions:
                            session_key = f"{session['subject']}:{session['topic']}"
                            if session_key not in seen_sessions:
                                seen_sessions.add(session_key)
                                cleaned_sessions.append(session)
                        
                        cleaned_plan[date] = cleaned_sessions
                    
                    plan['plan'] = cleaned_plan
                    logger.info(f"Cleaned plan: {plan}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing ML model response: {str(e)}")
                    logger.error(f"Raw response was: {result.stdout}")
                    return jsonify({
                        "error": f"Invalid response from ML model: {str(e)}",
                        "details": {
                            "raw_response": result.stdout,
                            "stderr": result.stderr,
                            "error_type": str(type(e))
                        }
                    }), 500
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"ML model execution failed with error: {str(e)}")
                logger.error(f"Return code: {e.returncode}")
                logger.error(f"Command output: {e.output}")
                logger.error(f"Command stderr: {e.stderr}")
                logger.error(f"Command args: {e.cmd}")
                return jsonify({
                    "error": f"ML model execution failed",
                    "details": {
                        "return_code": e.returncode,
                        "output": e.output,
                        "stderr": e.stderr,
                        "command": e.cmd
                    }
                }), 500
            except Exception as e:
                logger.error(f"Unexpected error running ML model: {str(e)}")
                logger.error(f"Error type: {str(type(e))}")
                return jsonify({
                    "error": f"Failed to execute ML model: {str(e)}",
                    "details": {
                        "error_type": str(type(e)),
                        "message": str(e)
                    }
                }), 500
            
            # Save to DB
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO study_plans (user_id, subjects, weaknesses, exam_dates, generated_plan)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data.get('user_id', 'anonymous'),
                json.dumps(data.get('subjects', [])),
                json.dumps(data.get('weaknesses', [])),
                json.dumps(data.get('exam_dates', [])),
                json.dumps(plan)
            ))
            conn.commit()
            conn.close()

            logger.info("Study plan generated and saved successfully")
            return jsonify(plan)
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return jsonify({
                "error": f"Internal server error: {str(e)}",
                "details": {
                    "error_type": str(type(e))
                }
            }), 500
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "details": {
                "error_type": str(type(e))
            }
        }), 500

# --- API: Get All Plans ---
@app.route('/api/plans', methods=['GET'])
def get_plans():
    logger.info("Received request to get all plans")
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM study_plans ORDER BY created_at DESC')
        plans = cursor.fetchall()
        conn.close()
        
        logger.debug(f"Found {len(plans)} plans in database")
        return jsonify([dict(plan) for plan in plans])
    except Exception as e:
        logger.error(f"Error fetching plans: {str(e)}")
        return jsonify({"error": str(e)}), 500

# --- Run Server ---
if __name__ == '__main__':
    logger.info("Starting study planner backend server")
    init_db()
    app.run(debug=True, port=5500, host='0.0.0.0')
