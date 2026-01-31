// API Utility for Backend Communication
const API_BASE_URL = 'http://localhost:8000/api';

const api = {
    // User Authentication
    async register(username, password) {
        const response = await fetch(`${API_BASE_URL}/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        return response.json();
    },

    async login(username, password) {
        const response = await fetch(`${API_BASE_URL}/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        return response.json();
    },

    // User Data
    async getUser(userId) {
        const response = await fetch(`${API_BASE_URL}/user/`, {
            method: 'GET',
            headers: { 'user_id': userId }
        });
        return response.json();
    },

    // Questions
    async getQuestion(difficulty) {
        const response = await fetch(`${API_BASE_URL}/question/?difficulty=${difficulty}`);
        return response.json();
    },

    async checkAnswer(questionId, answer) {
        const response = await fetch(`${API_BASE_URL}/question/check/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question_id: questionId, answer: answer })
        });
        return response.json();
    },

    // Battle Results
    async submitBattleResult(userId, won, area) {
        const response = await fetch(`${API_BASE_URL}/battle/result/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, won: won, area: area })
        });
        return response.json();
    }
};
