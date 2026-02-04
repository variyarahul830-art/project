import { Suspense } from 'react';
import LoginForm from '../components/LoginForm';
import styles from './page.module.css';

export const metadata = {
  title: 'Login - Chatbot',
  description: 'Login to your account',
};

export default function LoginPage() {
  return (
    <div className={styles.container}>
      <Suspense fallback={<div>Loading...</div>}>
        <LoginForm />
      </Suspense>
    </div>
  );
}
