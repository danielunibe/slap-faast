import React from 'react';
import { User, MessageSquare } from 'lucide-react';

const UserProfile: React.FC = () => {
  return (
    <div className="flex items-center space-x-4 text-white z-50">
      <div className="text-right">
        <div className="text-xl font-semibold leading-none drop-shadow-md">Notwen</div>
        <div className="flex items-center justify-end space-x-3 text-sm mt-1 text-gray-200">
          <div className="flex items-center drop-shadow-sm">
            <span className="font-bold mr-1">6</span>
            <User size={14} />
          </div>
          <div className="flex items-center drop-shadow-sm">
            <span className="font-bold mr-1">1</span>
            <MessageSquare size={14} />
          </div>
        </div>
      </div>
      <div className="w-12 h-12 bg-gray-300 rounded overflow-hidden border-2 border-white shadow-md">
          <img src="https://picsum.photos/seed/user/100/100" alt="Avatar" className="w-full h-full object-cover" />
      </div>
    </div>
  );
};

export default UserProfile;