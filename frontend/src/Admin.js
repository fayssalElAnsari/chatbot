// src/pages/Admin.js
import React, { useState } from 'react';
import * as Slider from '@radix-ui/react-slider';
import * as Label from '@radix-ui/react-label';
import * as Form from '@radix-ui/react-form';
import './styles.css';

const Admin = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [page, setPage] = useState('settings');

  const toggleSidebar = () => {
    setCollapsed(!collapsed);
  };

  const renderContent = () => {
    switch (page) {
      case 'documents':
        return <Documents />;
      case 'settings':
      default:
        return (
          <div style={{ display: 'flex', padding: '0 20px', flexWrap: 'wrap', gap: 15, alignItems: 'center' }}>
            <Form.Root className='FormRoot'>
              <Form.Field className="FormField" name="temperature">
                <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
                  <Form.Label className="FormLabel">Temperature</Form.Label>
                  <Form.Message className="FormMessage" match="valueMissing">
                    Default temperature
                  </Form.Message>
                </div>
              </Form.Field>
              <Form.Submit asChild>
                <button className="Button" style={{ marginTop: 10 }}>
                  Update Settings
                </button>
              </Form.Submit>
            </Form.Root>
            <form>
              <Label.Root className="LabelRoot" htmlFor="temperature_slider">
                Temperature
              </Label.Root>
              <Slider.Root id='temperature_slider' className="SliderRoot" defaultValue={[1]} max={2} step={0.01} min={0}>
                <Slider.Track className="SliderTrack">
                  <Slider.Range className="SliderRange" />
                </Slider.Track>
                <Slider.Thumb className="SliderThumb" aria-label="Temperature" />
              </Slider.Root>
            </form>
          </div>
        );
    }
  };

  return (
    <div className="admin-container">
      <div className="top-bar">
        <button onClick={toggleSidebar} className="sidebar-toggle">
          {collapsed ? 'Expand' : 'Collapse'}
        </button>
        <div className="user-info">User Info</div>
      </div>
      <div className="main-content">
        <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
          <ul>
            <li onClick={() => setPage('settings')}>Settings</li>
            <li onClick={() => setPage('documents')}>Documents</li>
          </ul>
        </div>
        <div className="content">
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

const Documents = () => {
  const data = [
    { sourceType: 'PDF', name: 'Document 1', ingestionDate: '2024-07-25', status: 'Completed' },
    // Add more data here
  ];

  return (
    <div className="documents-page">
      <button className="add-document-btn">Add New Document</button>
      <table className="documents-table">
        <thead>
          <tr>
            <th>Source Type</th>
            <th>Name</th>
            <th>Ingestion Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index}>
              <td>{row.sourceType}</td>
              <td>{row.name}</td>
              <td>{row.ingestionDate}</td>
              <td>{row.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Admin;
