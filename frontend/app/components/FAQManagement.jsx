'use client';

import { useState, useEffect } from 'react';
import styles from './FAQManagement.module.css';
import * as hasura from '../services/hasura';

export default function FAQManagement() {
  const [faqs, setFaqs] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [filter, setFilter] = useState('');
  const [formData, setFormData] = useState({
    question: '',
    answer: '',
    category: ''
  });

  // Fetch all FAQs on component mount
  useEffect(() => {
    fetchFAQs();
    fetchCategories();
  }, []);

  // Re-fetch FAQs when filter changes
  useEffect(() => {
    fetchFAQs();
  }, [filter]);

  const fetchFAQs = async () => {
    setLoading(true);
    try {
      const data = await hasura.getFAQs(filter || null);
      setFaqs(data.faqs || []);
    } catch (error) {
      console.error('Error fetching FAQs:', error);
      alert('Error fetching FAQs: ' + error.message);
    }
    setLoading(false);
  };

  const fetchCategories = async () => {
    try {
      const data = await hasura.getFAQCategories();
      const uniqueCategories = data.faqs
        .map(faq => faq.category)
        .filter(cat => cat && cat.trim())
        .filter((cat, idx, arr) => arr.indexOf(cat) === idx);
      setCategories(uniqueCategories);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!formData.question.trim() || !formData.answer.trim()) {
      alert('Question and answer are required');
      return;
    }

    setLoading(true);

    try {
      if (editingId) {
        await hasura.updateFAQ(
          editingId,
          formData.question.trim(),
          formData.answer.trim(),
          formData.category.trim() || null
        );
      } else {
        await hasura.createFAQ(
          formData.question.trim(),
          formData.answer.trim(),
          formData.category.trim() || null
        );
      }

      await fetchFAQs();
      await fetchCategories();
      setFormData({ question: '', answer: '', category: '' });
      setEditingId(null);
      setShowForm(false);
      alert('FAQ saved successfully!');
    } catch (error) {
      console.error('Error saving FAQ:', error);
      // Check for duplicate question error
      if (error.message.includes('duplicate') || error.message.includes('unique')) {
        alert('❌ This question already exists! Please use a different question.');
      } else {
        alert('Error saving FAQ: ' + error.message);
      }
    }
    setLoading(false);
  };

  const handleEdit = (faq) => {
    setFormData({
      question: faq.question,
      answer: faq.answer,
      category: faq.category || ''
    });
    setEditingId(faq.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this FAQ?')) return;

    try {
      await hasura.deleteFAQ(id);
      await fetchFAQs();
      await fetchCategories();
      alert('FAQ deleted successfully!');
    } catch (error) {
      console.error('Error deleting FAQ:', error);
      alert('Error deleting FAQ: ' + error.message);
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingId(null);
    setFormData({ question: '', answer: '', category: '' });
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>📚 FAQ Management</h2>
        <button 
          className={styles.addBtn}
          onClick={() => setShowForm(true)}
          disabled={loading}
        >
          ➕ Add FAQ
        </button>
      </div>

      {/* Filter Section */}
      <div className={styles.filterSection}>
        <label>Filter by Category:</label>
        <select 
          value={filter} 
          onChange={(e) => {
            const selectedCategory = e.target.value;
            setFilter(selectedCategory);
            // fetchFAQs will be called by useEffect when filter changes
          }}
          className={styles.categorySelect}
        >
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {/* Add/Edit Form */}
      {showForm && (
        <div className={styles.formContainer}>
          <h3>{editingId ? 'Edit FAQ' : 'Add New FAQ'}</h3>
          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.formGroup}>
              <label>Question *</label>
              <input
                type="text"
                value={formData.question}
                onChange={(e) => setFormData({ ...formData, question: e.target.value })}
                placeholder="Enter FAQ question"
                required
                className={styles.input}
              />
            </div>

            <div className={styles.formGroup}>
              <label>Answer *</label>
              <textarea
                value={formData.answer}
                onChange={(e) => setFormData({ ...formData, answer: e.target.value })}
                placeholder="Enter FAQ answer"
                required
                rows={6}
                className={styles.textarea}
              />
            </div>

            <div className={styles.formGroup}>
              <label>Category</label>
              <input
                type="text"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="e.g., General, Technical, etc."
                className={styles.input}
                list="categoryList"
              />
              <datalist id="categoryList">
                {categories.map((cat) => (
                  <option key={cat} value={cat} />
                ))}
              </datalist>
            </div>

            <div className={styles.buttonGroup}>
              <button type="submit" className={styles.submitBtn} disabled={loading}>
                {loading ? 'Saving...' : 'Save FAQ'}
              </button>
              <button 
                type="button" 
                className={styles.cancelBtn} 
                onClick={handleCancel}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* FAQs List */}
      <div className={styles.faqsList}>
        <h3>Total FAQs: {faqs.length}</h3>
        {loading ? (
          <p>Loading FAQs...</p>
        ) : faqs.length === 0 ? (
          <p className={styles.noData}>No FAQs found. {!filter && 'Add one to get started!'}</p>
        ) : (
          faqs.map((faq) => (
            <div key={faq.id} className={styles.faqItem}>
              <div className={styles.faqContent}>
                <div className={styles.faqHeader}>
                  <h4>{faq.question}</h4>
                  {faq.category && (
                    <span className={styles.category}>{faq.category}</span>
                  )}
                </div>
                <p>{faq.answer}</p>
                <small className={styles.timestamp}>
                  Updated: {new Date(faq.updated_at).toLocaleDateString()}
                </small>
              </div>
              <div className={styles.actions}>
                <button 
                  className={styles.editBtn}
                  onClick={() => handleEdit(faq)}
                  title="Edit"
                >
                  ✏️
                </button>
                <button 
                  className={styles.deleteBtn}
                  onClick={() => handleDelete(faq.id)}
                  title="Delete"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
