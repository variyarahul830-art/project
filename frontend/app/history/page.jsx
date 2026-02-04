'use client';

import { useAuth } from '@/app/components/../context/AuthContext';
import ChatHistory from '@/app/components/ChatHistory';

export default function HistoryPage() {
  const { user } = useAuth();
  
  // Key forces component to remount when user changes
  return <ChatHistory key={user?.user_id || 'no-user'} />;
}
