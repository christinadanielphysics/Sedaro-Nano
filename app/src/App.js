import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';

const App = () => {
  // Store plot data in state.
  const [plotData, setPlotData] = useState([]);

  useEffect(() => {
    // fetch plot data when the component mounts

    async function fetchData() {
      console.log('calling fetchdata...');

      try {
        // 'data.json' should be populated from a run of sim.py
        const response = await fetch('data.json');
        const data = await response.json();
        const updatedPlotData = {};

        data.forEach(([t0, t1, frame]) => {
          for (let [agentId, { x, y }] of Object.entries(frame)) {
            updatedPlotData[agentId] = updatedPlotData[agentId] || { x: [], y: [] };
            updatedPlotData[agentId].x.push(x);
            updatedPlotData[agentId].y.push(y);
          }
        });

        setPlotData(Object.entries(updatedPlotData).map(([agentId, data], index) => ({
          ...data, 
          mode: index === 2 ? 'lines+markers' : 'markers',  
          type: 'scatter',
          name: ["Mirror A","Mirror B","Light"][index],  
          marker: index === 2 ? {color: 'goldenrod'} : {},  
          line: index === 2 ? {color: 'goldenrod'} : {}   
        })));

        console.log('plotData:', Object.values(updatedPlotData));
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    }

    fetchData();
  }, []);

  return (
    <div>
      <Plot
        style={{ position: 'fixed', width: '100%', height: '100%', left: 0, top: 0 }}
        data={plotData}
        layout={{
          title: 'Light Between Translating Mirrors',
          xaxis: {
            title: 'position coordinate x',  
          },
          yaxis: {
            title: 'time coordinate t', 
          }
        }}
      />
    </div>
  );
};

export default App;
