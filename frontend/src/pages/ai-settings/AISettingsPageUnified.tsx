import React from 'react';
import UserCommandCenter from '../../components/UserCommandCenter';

export const AISettingsPageUnified: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <UserCommandCenter defaultTab="ai-config" />
    </div>
  );
};

export default AISettingsPageUnified;