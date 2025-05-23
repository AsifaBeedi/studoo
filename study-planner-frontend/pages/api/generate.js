export default function handler(req, res) {
 // Receive inputs from frontend
 const { subjects, weaknesses, exams } = req.body;
 // TODO: Call your ML model here (Python backend)
 // For now, return mock data
 const mockPlan = {
 "plan": "Mock data - replace with ML output"
 };
 res.status(200).json(mockPlan);
}