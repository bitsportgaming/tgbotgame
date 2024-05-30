import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AdminTaskComponent.css';

const AdminTaskComponent = () => {
    const [tasks, setTasks] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [name, setName] = useState('');
    const [link, setLink] = useState('');
    const [points, setPoints] = useState('');
    const [expiryDate, setExpiryDate] = useState('');

    useEffect(() => {
        fetchTasks();
    }, []);

    const fetchTasks = async () => {
        try {
            const response = await axios.get('https://task.pooldegens.meme/api/get_tasks');
            setTasks(response.data);
        } catch (error) {
            console.error('Error fetching tasks:', error);
        }
    };

    const handleDelete = async (taskId) => {
        try {
            await axios.delete(`https://task.pooldegens.meme/api/delete_task/${taskId}`);
            fetchTasks();
        } catch (error) {
            console.error('Error deleting task:', error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('https://task.pooldegens.meme/api/add_task', {
                name,
                link,
                points,
                expiry_date: expiryDate
            });
            alert(response.data.message);
            fetchTasks();
            setShowForm(false);
        } catch (error) {
            console.error('Error adding task:', error);
            alert('Failed to add task');
        }
    };

    return (
        <div className="admin-container">
            <h2>Admin Task Management</h2>
            <button onClick={() => setShowForm(!showForm)}>{showForm ? 'Close Form' : 'Create Task'}</button>
            {showForm && (
                <form onSubmit={handleSubmit} className="task-form">
                    <div>
                        <label>Task Name:</label>
                        <input type="text" value={name} onChange={(e) => setName(e.target.value)} required />
                    </div>
                    <div>
                        <label>Task Link:</label>
                        <input type="text" value={link} onChange={(e) => setLink(e.target.value)} required />
                    </div>
                    <div>
                        <label>Task Points:</label>
                        <input type="number" value={points} onChange={(e) => setPoints(e.target.value)} required />
                    </div>
                    <div>
                        <label>Expiry Date:</label>
                        <input type="date" value={expiryDate} onChange={(e) => setExpiryDate(e.target.value)} required />
                    </div>
                    <button type="submit">Add Task</button>
                </form>
            )}
            <ul className="task-list">
                {tasks.map(task => (
                    <li key={task._id} className="task-item">
                        <span>{task.name}</span>
                        <button onClick={() => handleDelete(task._id)}>Delete</button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default AdminTaskComponent;
