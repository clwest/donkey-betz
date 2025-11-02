#!/usr/bin/env python
"""
Frontend + UX Designer
Generated for job: rok_1119908 on 2025-09-21 05:07:03
"""

import React, { useState } from 'react';
import Header from './Header';
import UserInput from './UserInput';
import OutputDisplay from './OutputDisplay';
import '../styles/App.css';

/**
 * Main App component that manages the state and renders other components.
 */
const App = () => {
    const [userInput, setUserInput] = useState('');
    const [output, setOutput] = useState('');
    const [error, setError] = useState(null);

    /**
     * Handles the submission of user input.
     * @param {string} input - The input from the user.
     */
    const handleInputSubmit = async (input) => {
        try {
            // Simulate an API call to process input
            const response = await mockApiCall(input);
            setOutput(response);
            setError(null);
        } catch (err) {
            setError('An error occurred while processing your input.');
            console.error(err);
        }
    };

    // Mock API call function
    const mockApiCall = (input) => {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (input) {
                    resolve(`Processed output for: ${input}`);
                } else {
                    reject(new Error('Invalid input'));
                }
            }, 1000);
        });
    };

    return (
        <div className="App">
            <Header />
            <UserInput onSubmit={handleInputSubmit} />
            {error && <div className="error">{error}</div>}
            <OutputDisplay output={output} />
        </div>
    );
};

export default App;