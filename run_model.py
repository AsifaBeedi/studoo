import pickle
import os

def load_model():
    model_path = 'model/study_planner_model.pkl'
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        return None
    
    try:
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        return model
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None

def generate_study_plan(input_data):
    # Parse input data
    subjects = input_data.get('subjects', [])
    weaknesses = input_data.get('weaknesses', {})
    exams = input_data.get('exams', {})

    # Generate study plan
    plan = {}
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Define time slots
    time_slots = {
        'Morning': ('08:00', '12:00'),
        'Afternoon': ('13:00', '17:00'),
        'Evening': ('18:00', '20:00')
    }
    
    # Add study sessions with time slots
    for subject in subjects:
        if subject in weaknesses:
            for topic, level in weaknesses[subject].items():
                duration = '2h' if level > 3 else '1h'
                time_slot = 'Morning' if len(plan.get(current_date, [])) < 2 else 'Afternoon'
                plan.setdefault(current_date, []).append({
                    'subject': subject,
                    'topic': topic,
                    'duration': duration,
                    'progress': 'not_started',
                    'time_slot': time_slot,
                    'status': 'not_started'
                })
    
    # Add review sessions for subjects with exams
    for subject, exam_date in exams.items():
        exam_date = datetime.strptime(exam_date, '%Y-%m-%d')
        days_until_exam = (exam_date - datetime.now()).days
        
        if days_until_exam <= 3:
            review_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
            time_slot = 'Afternoon' if len(plan.get(review_date, [])) < 2 else 'Evening'
            plan.setdefault(review_date, []).append({
                'subject': subject,
                'topic': 'Review',
                'duration': '3h',
                'progress': 'not_started',
                'time_slot': time_slot,
                'status': 'not_started'
            })
    
    # Add progress tracking and tips
    progress_stats = {
        'total_sessions': sum(len(sessions) for sessions in plan.values()),
        'completed_sessions': 0,
        'in_progress_sessions': 0,
        'not_started_sessions': sum(len(sessions) for sessions in plan.values())
    }
    
    tips = [
        "Stay focused and take a 5-min break every 30 mins!",
        "You've got this! Keep pushing forward.",
        "Remember to review your notes after each session."
    ]
    
    # Convert to JSON
    return json.dumps({
        'plan': plan,
        'current_date': current_date,
        'progress_stats': progress_stats,
        'tips': tips
    })

def main():
    print("Study Planner Model")
    print("-" * 30)
    
    model = load_model()
    if model:
        print("\nModel loaded successfully!")
        print("\nModel Information:")
        print(f"Type: {type(model)}")
        print("\nThis is a pre-trained study planner model.")
        print("To use it, you'll need to provide appropriate input data.")
        print("Please check the documentation or source code to understand the required input format.")
        
        # Check if the model has any attributes that might help us understand it better
        if hasattr(model, '__dict__'):
            print("\nModel Attributes:")
            for attr in dir(model):
                if not attr.startswith('_'):
                    try:
                        value = getattr(model, attr)
                        print(f"{attr}: {value}")
                    except:
                        continue
        
        # Generate study plan
        input_data = {
            'subjects': ['Math', 'Science', 'English'],
            'weaknesses': {
                'Math': {'Algebra': 4, 'Geometry': 3},
                'Science': {'Biology': 2, 'Chemistry': 4}
            },
            'exams': {
                'Math': '2023-03-15',
                'Science': '2023-03-17'
            }
        }
        study_plan = generate_study_plan(input_data)
        print("\nStudy Plan:")
        print(study_plan)
    else:
        print("\nFailed to load the model. Make sure the model file exists in the correct location.")
        print("If you continue to have issues, consider:")
        print("1. Checking if the model file is corrupted")
        print("2. Verifying the Python version used to create the model")
        print("3. Ensuring all required dependencies are installed")

if __name__ == "__main__":
    main()
