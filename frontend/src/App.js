import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

function App() {
  const [pods, setPods] = useState([]);
  const [spores, setSpores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('pods');
  const [generatePrompt, setGeneratePrompt] = useState('');
  const [generating, setGenerating] = useState(false);
  const [generatedPod, setGeneratedPod] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [podsRes, sporesRes] = await Promise.all([
        axios.get(`${API_URL}/api/pods`),
        axios.get(`${API_URL}/api/spores`)
      ]);
      setPods(podsRes.data);
      setSpores(sporesRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePod = async () => {
    if (!generatePrompt.trim()) {
      alert('Please enter a prompt');
      return;
    }

    try {
      setGenerating(true);
      const response = await axios.post(`${API_URL}/api/pods/generate`, {
        prompt: generatePrompt
      });
      setGeneratedPod(response.data.pod);
      setGeneratePrompt('');
      alert('PoD generated successfully! Check the generated PoD section.');
    } catch (error) {
      console.error('Error generating PoD:', error);
      alert('Error generating PoD: ' + (error.response?.data?.detail || error.message));
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🧭 Ontology Framework</h1>
        <p>Manage Plans of Day and Spore Registries</p>
      </header>

      <div className="container">
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'pods' ? 'active' : ''}`}
            onClick={() => setActiveTab('pods')}
          >
            Plans of Day ({pods.length})
          </button>
          <button
            className={`tab ${activeTab === 'spores' ? 'active' : ''}`}
            onClick={() => setActiveTab('spores')}
          >
            Spores ({spores.length})
          </button>
          <button
            className={`tab ${activeTab === 'generate' ? 'active' : ''}`}
            onClick={() => setActiveTab('generate')}
          >
            🤖 Generate PoD (AI)
          </button>
        </div>

        {loading ? (
          <div className="loading">Loading...</div>
        ) : (
          <>
            {activeTab === 'pods' && (
              <div className="content">
                <h2>Plans of Day</h2>
                {pods.length === 0 ? (
                  <p>No Plans of Day found.</p>
                ) : (
                  pods.map((pod) => (
                    <div key={pod.uri} className="card">
                      <h3>{pod.label}</h3>
                      <p className="date">Date: {pod.date}</p>
                      <p className="status">Status: {pod.status}</p>
                      
                      <div className="workflow-phases">
                        <h4>Workflow Phases:</h4>
                        {pod.workflowPhases.map((phase, idx) => (
                          <div key={idx} className="phase">
                            <strong>{phase.phaseOrder}. {phase.phaseName}:</strong>
                            <p>{phase.description}</p>
                            {phase.hasTime && (
                              <p className="time">⏰ {phase.hasTime}</p>
                            )}
                          </div>
                        ))}
                      </div>

                      {pod.references && pod.references.length > 0 && (
                        <div className="references">
                          <h4>References:</h4>
                          <ul>
                            {pod.references.map((ref, idx) => (
                              <li key={idx}>
                                <strong>{ref.referenceType}:</strong> {ref.referenceValue}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'spores' && (
              <div className="content">
                <h2>Spores</h2>
                {spores.length === 0 ? (
                  <p>No Spores found.</p>
                ) : (
                  spores.map((spore) => (
                    <div key={spore.uri} className="card">
                      <h3>{spore.label}</h3>
                      <p className="status">Status: {spore.status}</p>
                      <p>Created: {spore.createdAt}</p>
                      {spore.linksTo && (
                        <p>Links to: <a href={spore.linksTo}>{spore.linksTo}</a></p>
                      )}
                      <p>Derived from: <a href={spore.derivedFrom}>{spore.derivedFrom}</a></p>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'generate' && (
              <div className="content">
                <h2>Generate Plan of Day with AI</h2>
                <p className="info">
                  Use Google Gemini AI to generate a new Plan of Day based on your prompt.
                  The AI will create a structured PoD following the Plan-Do-Check-Act workflow.
                </p>
                
                <div className="generate-section">
                  <textarea
                    className="prompt-input"
                    placeholder="Describe what you want to plan for today. For example: 'I need to work on the Cloud Run hackathon submission, review infrastructure logs, and validate the deployment.'"
                    value={generatePrompt}
                    onChange={(e) => setGeneratePrompt(e.target.value)}
                    rows={6}
                  />
                  <button
                    className="generate-button"
                    onClick={handleGeneratePod}
                    disabled={generating}
                  >
                    {generating ? 'Generating...' : '🤖 Generate PoD'}
                  </button>
                </div>

                {generatedPod && (
                  <div className="card generated-pod">
                    <h3>Generated Plan of Day</h3>
                    <p className="date">Date: {generatedPod.date}</p>
                    <p className="label">{generatedPod.label}</p>
                    
                    <div className="workflow-phases">
                      <h4>Workflow Phases:</h4>
                      {generatedPod.phases.map((phase, idx) => (
                        <div key={idx} className="phase">
                          <strong>{phase.phaseOrder}. {phase.phaseName}:</strong>
                          <p>{phase.description}</p>
                          {phase.hasTime && (
                            <p className="time">⏰ {phase.hasTime}</p>
                          )}
                        </div>
                      ))}
                    </div>

                    {generatedPod.references && generatedPod.references.length > 0 && (
                      <div className="references">
                        <h4>References:</h4>
                        <ul>
                          {generatedPod.references.map((ref, idx) => (
                            <li key={idx}>
                              <strong>{ref.referenceType}:</strong> {ref.referenceValue}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>

      <footer>
        <p>Powered by Google Cloud Run & Gemini AI | Ontology Framework v1.0.0</p>
      </footer>
    </div>
  );
}

export default App;





