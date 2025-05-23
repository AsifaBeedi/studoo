import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function PlanScreen() {
    const router = useRouter();
    const { plan } = router.query;
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (plan) {
            try {
                const parsedPlan = JSON.parse(plan);
                if (parsedPlan && parsedPlan.plan && parsedPlan.progress_stats) {
                    setIsLoading(false);
                } else {
                    setError('Invalid plan data format');
                }
            } catch (e) {
                setError('Failed to parse plan data');
            }
        } else {
            setError('No plan data available');
        }
    }, [plan]);

    if (isLoading) {
        return (
            <div className="container">
                <h1>📚 Study Planner</h1>
                <div className="loading">
                    <div className="spinner"></div>
                    <p>Loading your study plan...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container">
                <h1>📚 Study Planner</h1>
                <div className="alert alert-danger">
                    {error}
                </div>
                <button 
                    className="btn btn-primary"
                    onClick={() => router.back()}
                >
                    Go Back and Generate Plan
                </button>
            </div>
        );
    }

    const planData = JSON.parse(plan);

    // Calculate progress
    const totalSessions = planData.progress_stats?.total_sessions || 0;
    const completedSessions = planData.progress_stats?.completed_sessions || 0;
    const progressPercentage = Math.round((completedSessions / (totalSessions || 1)) * 100);

    return (
        <div className="container">
            <div className="header-section">
                <h1>📚 Study Plan for Today</h1>
                <h2>{new Date(planData.current_date).toLocaleDateString()}</h2>
                <div className="divider"></div>
            </div>

            {/* Progress Bar */}
            <div className="progress-section">
                <div className="progress-bar">
                    <div className="progress" style={{ width: `${progressPercentage}%` }}></div>
                </div>
                <span className="progress-text">{progressPercentage}% Completed</span>
            </div>

            {/* Display study sessions */}
            <div className="sessions-section">
                {Object.entries(planData.plan).map(([timeSlot, sessions]) => (
                    <div key={timeSlot} className="time-slot">
                        <h3>{timeSlot}</h3>
                        {sessions.map((session, index) => (
                            <div key={index} className="session-card">
                                <div className="session-details">
                                    <span className="subject">📘 Subject: {session.subject}</span>
                                    <span className="task">🔁 Task: {session.task}</span>
                                    <span className="duration">⏳ Duration: {session.duration} hours</span>
                                </div>
                                <div className="progress-section">
                                    <span className="progress-text">✅ Progress: {session.status}</span>
                                    <div className="feedback-buttons">
                                        <button onClick={() => handleFeedback(session, 'good')} className="feedback-btn good">
                                            👍
                                        </button>
                                        <button onClick={() => handleFeedback(session, 'bad')} className="feedback-btn bad">
                                            👎
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ))}
            </div>

            {/* Tips Section */}
            <div className="tips-section">
                <h3>Tips:</h3>
                {planData.tips.map((tip, index) => (
                    <p key={index} className="tip">{tip}</p>
                ))}
            </div>

            {/* Group by time slots */}
            {['Morning', 'Afternoon', 'Evening'].map(timeSlot => {
                const sessions = Object.values(planData.plan).flat()
                    .filter(session => session.time_slot === timeSlot);
                
                if (sessions.length === 0) return null;
                
                return (
                    <div key={timeSlot} className="time-slot">
                        <h2>
                            <i className="fas fa-clock"></i>
                            {timeSlot} Session
                        </h2>
                        {sessions.map((session, index) => (
                            <div key={index} className="session">
                                <div className="session-header">
                                    <span className="subject">📘 {session.subject}</span>
                                    <span className="task">🔁 {session.topic}</span>
                                    <span className="duration">⏳ {session.duration}</span>
                                </div>
                                <div className="progress-section">
                                    <span className="progress-text">
                                        {session.status === 'completed' ? '✅ Completed' :
                                         session.status === 'in_progress' ? '⏳ In Progress' :
                                         '❌ Not Started'}
                                    </span>
                                    <div className="feedback-buttons">
                                        <button 
                                            className="btn btn-success"
                                            onClick={() => handleFeedback(session, 'completed')}
                                        >
                                            👍
                                        </button>
                                        <button 
                                            className="btn btn-danger"
                                            onClick={() => handleFeedback(session, 'not_started')}
                                        >
                                            👎
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                );
            })}
        </div>
    );

    // Helper function to handle feedback
    const handleFeedback = async (session, status) => {
        try {
            const response = await fetch(`${API_URL}/api/update_session`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date: planData.current_date,
                    subject: session.subject,
                    topic: session.topic,
                    status: status
                }),
            });

            const result = await response.json();
            if (result.success) {
                // Update the plan data locally
                const updatedPlan = { ...planData };
                const sessions = updatedPlan.plan[planData.current_date];
                const sessionIndex = sessions.findIndex(s => 
                    s.subject === session.subject && 
                    s.topic === session.topic
                );
                if (sessionIndex !== -1) {
                    sessions[sessionIndex].status = status;
                    if (status === 'completed') {
                        updatedPlan.progress_stats.completed_sessions += 1;
                        updatedPlan.progress_stats.not_started_sessions -= 1;
                    }
                }
                router.push({
                    pathname: '/plan',
                    query: { plan: JSON.stringify(updatedPlan) }
                }, undefined, { shallow: true });
            }
        } catch (error) {
            console.error('Error updating session status:', error);
        }
    };
}