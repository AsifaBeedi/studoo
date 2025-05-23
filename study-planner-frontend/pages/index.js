import { useState } from 'react';
import { useRouter } from 'next/router';
import { API_URL } from '../config/api';

export default function InputScreen() {
    // State for user inputs
    const [subjects, setSubjects] = useState([]);
    const [newSubject, setNewSubject] = useState('');
    const [weaknesses, setWeaknesses] = useState({}); // Format: {"Maths": {"Algebra": 3, "Calculus": 5}}
    const [exams, setExams] = useState({}); // Format: {"Maths": "2023-11-15"}
    const [typingTimeout, setTypingTimeout] = useState(null);

    // Debounced function for weakness input
    const handleWeaknessInput = (subject, topic) => {
        // Clear any existing timeout
        if (typingTimeout) {
            clearTimeout(typingTimeout);
        }
        
        // Set new timeout
        setTypingTimeout(setTimeout(() => {
            // Only create weakness entry if topic is not empty
            if (topic.trim()) {
                const level = weaknesses[subject]?.[topic] || 1;
                setWeaknesses(prev => ({
                    ...prev,
                    [subject]: { ...prev[subject] || {}, [topic]: level }
                }));
            }
        }, 500)); // 500ms delay
    };
    const router = useRouter();

    // Add a subject
    const addSubject = () => {
        if (newSubject.trim()) {
            setSubjects([...subjects, newSubject.trim()]);
            setNewSubject('');
        }
    };

    // Cleanup function to remove duplicate entries
    const cleanupWeaknesses = (weaknesses) => {
        const cleanedWeaknesses = {};
        
        // For each subject
        Object.entries(weaknesses).forEach(([subject, topics]) => {
            // For each topic, keep only the last value
            const cleanedTopics = {};
            Object.entries(topics).forEach(([topic, level]) => {
                cleanedTopics[topic.trim()] = level;
            });
            cleanedWeaknesses[subject] = cleanedTopics;
        });
        
        return cleanedWeaknesses;
    };

    // Submit to backend
    const generatePlan = async () => {
        try {
            // Clean up the weaknesses before sending
            const cleanedWeaknesses = cleanupWeaknesses(weaknesses);
            
            const response = await fetch(`${API_URL}/api/generate_plan`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ subjects, cleanedWeaknesses, exams }),
            });

            const result = await response.json();
            
            if (result.error) {
                alert(result.error);
                return;
            }

            // Format the plan data for display
            const formattedPlan = {
                current_date: new Date().toISOString().split('T')[0],
                plan: result.plan,
                progress_stats: {
                    total_sessions: Object.values(result.plan).reduce((acc, sessions) => 
                        acc + sessions.length, 0
                    ),
                    completed_sessions: 0,
                    in_progress_sessions: 0,
                    not_started_sessions: Object.values(result.plan).reduce((acc, sessions) => 
                        acc + sessions.length, 0
                    )
                },
                tips: [
                    "Stay focused and take a 5-min break every 30 mins!",
                    "You've got this! Keep pushing forward.",
                    "Remember to review your notes after each session."
                ]
            };

            // Navigate to output screen with the plan
            router.push({
                pathname: '/plan',
                query: { plan: JSON.stringify(formattedPlan) },
            });
        } catch (error) {
            console.error('Error generating plan:', error);
            alert('Failed to generate study plan. Please try again.');
        }
    };

    return (
        <div>
            <h1>📚 Study Planner</h1>
            {/* Subjects Input */}
            <div>
                <input
                    value={newSubject}
                    onChange={(e) => setNewSubject(e.target.value)}
                    placeholder="Add subject (e.g., Maths)"
                />
                <button onClick={addSubject}>+</button>
            </div>
            {/* Weaknesses (for each subject) */}
            {subjects.map((subject) => (
                <div key={subject}>
                    <h3>{subject}</h3>
                    <div>
                        <input
                            placeholder="Weak area (e.g., Algebra)"
                            onChange={(e) => {
                                const topic = e.target.value.trim();
                                handleWeaknessInput(subject, topic);
                            }}
                        />
                        <input
                            type="number"
                            min="1"
                            max="5"
                            onChange={(e) => {
                                const topicInput = e.target.previousElementSibling;
                                const topic = topicInput.value.trim();
                                const level = parseInt(e.target.value, 10) || 1;
                                setWeaknesses(prev => ({
                                    ...prev,
                                    [subject]: { ...prev[subject] || {}, [topic]: level }
                                }));
                            }}
                        />
                    </div>
                    {/* Add rating sliders here */}
                </div>
            ))}
            {/* Exam Dates */}
            {subjects.map((subject) => (
                <div key={subject}>
                    <h3>Exam Date for {subject}</h3>
                    <input
                        type="date"
                        onChange={(e) => setExams({ ...exams, [subject]: e.target.value })}
                    />
                </div>
            ))}
            <button onClick={generatePlan}>Generate Plan</button>
        </div>
    );
}
