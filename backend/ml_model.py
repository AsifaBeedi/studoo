import sys
import json
import os
from datetime import datetime, timedelta

def generate_study_plan(input_data):
    try:
        # Generate a study plan based on input data
        plan = {}
        current_date = datetime.now()
        
        # For each subject, create study sessions
        for subject in input_data.get('subjects', []):
            weaknesses = input_data.get('weaknesses', {}).get(subject, {})
            exam_date = input_data.get('exams', {}).get(subject)
            
            # If there's an exam date, calculate days remaining
            days_until_exam = None
            if exam_date:
                try:
                    exam_date = datetime.strptime(exam_date, '%Y-%m-%d')
                    days_until_exam = (exam_date - current_date).days
                except ValueError as e:
                    sys.stdout.write(json.dumps({"error": f"Error parsing exam date: {str(e)}"}))
                    sys.stdout.flush()
                    sys.exit(1)
            
            # Create study sessions based on weaknesses and exam date
            sessions = []
            for topic, level in weaknesses.items():
                try:
                    level = int(level)
                    # More difficult topics need more time
                    duration = "2h" if level > 3 else "1h"
                    sessions.append({
                        "subject": subject,
                        "topic": topic,
                        "duration": duration
                    })
                except (ValueError, TypeError) as e:
                    sys.stdout.write(json.dumps({"error": f"Error processing weakness level: {str(e)}"}))
                    sys.stdout.flush()
                    sys.exit(1)
            
            # Add sessions to plan
            date_str = current_date.strftime("%Y-%m-%d")
            if date_str not in plan:
                plan[date_str] = []
            
            # Add sessions, avoiding duplicates
            for session in sessions:
                # Check if this session already exists
                existing_session = next((s for s in plan[date_str] if 
                    s['subject'] == session['subject'] and 
                    s['topic'] == session['topic']), None)
                
                if existing_session:
                    # Update the duration if it exists
                    existing_session['duration'] = session['duration']
                else:
                    # Add new session
                    plan[date_str].append(session)
            
            # If there's an exam, add review sessions closer to the exam date
            if days_until_exam and days_until_exam > 0:
                try:
                    review_date = exam_date - timedelta(days=2)
                    review_date_str = review_date.strftime("%Y-%m-%d")
                    if review_date_str not in plan:
                        plan[review_date_str] = []
                        
                    # Add review session if it doesn't exist
                    review_session = {"subject": subject, "topic": "Review", "duration": "3h"}
                    if not any(s['subject'] == subject and s['topic'] == "Review" for s in plan[review_date_str]):
                        plan[review_date_str].append(review_session)
                except Exception as e:
                    sys.stdout.write(json.dumps({"error": f"Error creating review session: {str(e)}"}))
                    sys.stdout.flush()
                    sys.exit(1)
            
        output = {
            "status": "success",
            "plan": plan
        }
        
        # Ensure we return valid JSON
        json_str = json.dumps(output)
        sys.stdout.write(json_str)
        sys.stdout.flush()
        sys.exit(0)
        
    except Exception as e:
        sys.stdout.write(json.dumps({"error": str(e)}))
        sys.stdout.flush()
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Get the input data from command line
        if len(sys.argv) != 2:
            sys.stdout.write(json.dumps({"error": "Invalid number of arguments"}))
            sys.stdout.flush()
            sys.exit(1)
            
        input_data = sys.argv[1]
        
        # Parse the input data
        try:
            data = json.loads(input_data)
        except json.JSONDecodeError as e:
            sys.stdout.write(json.dumps({"error": f"Invalid JSON input: {str(e)}"}))
            sys.stdout.flush()
            sys.exit(1)
            
        # Generate the plan
        result = generate_study_plan(data)
        
        # Ensure we return valid JSON
        try:
            json_str = json.dumps(result)
            sys.stdout.write(json_str)
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"error": f"Failed to generate JSON output: {str(e)}"}))
            sys.stdout.flush()
            sys.exit(1)
            
    except Exception as e:
        sys.stdout.write(json.dumps({"error": f"Internal error: {str(e)}"}))
        sys.stdout.flush()
        sys.exit(1)
