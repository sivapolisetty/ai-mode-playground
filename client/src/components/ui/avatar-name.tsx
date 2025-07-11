import React from 'react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

interface AvatarNameProps {
  name: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const AvatarName: React.FC<AvatarNameProps> = ({ name, size = 'md', className }) => {
  // Get initials from name
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  const sizeClasses = {
    sm: 'h-8 w-8 text-xs',
    md: 'h-12 w-12 text-lg',
    lg: 'h-16 w-16 text-xl'
  };

  return (
    <Avatar className={`${sizeClasses[size]} ${className || ''} bg-primary-100 text-primary-700`}>
      <AvatarFallback className="font-semibold">
        {getInitials(name)}
      </AvatarFallback>
    </Avatar>
  );
};

export default AvatarName;
