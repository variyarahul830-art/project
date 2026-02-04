import { Suspense } from 'react';
import SignupForm from '../components/SignupForm';
import styles from './page.module.css';

export const metadata = {
  title: 'Sign Up - Chatbot',
  description: 'Create a new account',
};

export default function SignupPage() {
  return (
    <div className={styles.container}>
      <Suspense fallback={<div>Loading...</div>}>
        <SignupForm />
      </Suspense>
    </div>
  );
}
