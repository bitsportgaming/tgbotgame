import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import TaskComponent from './TaskComponent';
import WinLossPage from './WinLossPage';
import AdminTaskComponent from './AdminTaskComponent'; // Import AdminTaskComponent

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<TaskComponent />} />
                <Route path="/game-result" element={<WinLossPage />} />
                <Route path="/admin" element={<AdminTaskComponent />} /> {/* Add route for admin side */}
            </Routes>
        </Router>
    );
}

export default App;
