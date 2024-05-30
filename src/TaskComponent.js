import React, { useState, useEffect } from 'react';
import axios from 'axios';
import useTelegram from './useTelegram';
import './TaskComponent.css';

const TaskComponent = () => {
    const [taskList, setTaskList] = useState([]);
    const [allTasksCompleted, setAllTasksCompleted] = useState(false);
    const [username, setUsername] = useState(null);
    const tg = useTelegram();

    useEffect(() => {
        if (tg) {
            tg.ready();
            const user = tg.initDataUnsafe.user;
            setUsername(user.username);
            console.log('Username:', user.username);
        }
    }, [tg]);

    useEffect(() => {
        const fetchTasks = async () => {
            try {
                const response = await axios.get(`https://task.pooldegens.meme/api/get_tasks?username=${username}`);
                if (Array.isArray(response.data)) {
                    const tasks = response.data.map(task => ({
                        id: task._id,
                        description: task.name,
                        actionUrl: task.link,
                        points: task.points,
                        completed: false
                    }));
                    setTaskList(tasks);
                } else {
                    setTaskList([]);
                    console.error('API response is not an array:', response.data);
                }
            } catch (error) {
                console.error('Error fetching tasks:', error);
            }
        };

        if (username) {
            fetchTasks();
        }
    }, [username]);

    useEffect(() => {
        updatePlayButtonState();
    }, [taskList]);

    const handleTaskClick = (task) => {
        window.open(task.actionUrl, '_blank');
        setTimeout(() => {
            const updatedTasks = taskList.map(t => t.id === task.id ? { ...t, completed: true } : t);
            setTaskList(updatedTasks);
            saveTaskProgress(task.id, true);
        }, 7000);
    };

    const updatePlayButtonState = () => {
        const allCompleted = taskList.every(task => task.completed);
        setAllTasksCompleted(allCompleted);
    };

    const handlePlayButtonClick = () => {
        const gameUrl = `https://ball.pooldegens.meme/rolla/index.html?username=${username}`;
        const iframe = document.getElementById('gameIframe');
        iframe.src = gameUrl;
        iframe.style.display = 'block';
        iframe.style.position = 'fixed';
        iframe.style.top = '0';
        iframe.style.left = '0';
        iframe.style.width = '100vw';
        iframe.style.height = '100vh';
        iframe.style.zIndex = '9999';
        iframe.style.border = 'none';
        iframe.style.borderRadius = '0';

        document.querySelector('.header').classList.add('hidden');
        document.getElementById('tasks').classList.add('hidden');
        document.getElementById('playGameButton').classList.add('hidden');
    };

    const saveTaskProgress = async (taskId, completed) => {
        const response = await fetch('https://task.pooldegens.meme/api/complete_task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username: username, task_id: taskId }),
        });
        const data = await response.json();
        console.log(data);
    };

    return (
        <div className="container">
            <div className="header">
                <img src="https://i.imgur.com/QXyAnK1.png" alt="Pool Degen Banner" />
                <h1 style={{color: 'white'}}>Complete These Tasks to Start Playing</h1>
                {username && <h2 style={{color: 'white'}}>Welcome, {username}!</h2>}
            </div>
            {taskList.length > 0 ? (
                <ul id="tasks" className="tasks">
                    {taskList.map(task => (
                        <li key={task.id} className={`task ${task.completed ? 'completed' : ''}`} onClick={() => handleTaskClick(task)}>
                            <label style={{color: 'white'}}>{task.description}</label>
                            <span className="task-points">+{task.points}</span>
                            <div className={`icon ${task.completed ? 'check' : ''}`}></div>
                        </li>
                    ))}
                </ul>
            ) : (
                <div className="no-tasks">
                    <h2>No Tasks Available</h2>
                    <p>There are currently no tasks to complete. Why not head back to the game and farm some more $POOLD?</p>
                </div>
            )}
            <button id="playGameButton" disabled={!allTasksCompleted} onClick={handlePlayButtonClick}>Play Game</button>
            <iframe
                id="gameIframe"
                title="Game"
                style={{
                    display: 'none',
                    width: '100vw',
                    height: '100vh',
                    border: 'none',
                    borderRadius: '0',
                    marginTop: '0',
                    position: 'fixed',
                    top: '0',
                    left: '0',
                    zIndex: '9999'
                }}
            ></iframe>
        </div>
    );
};

export default TaskComponent;
