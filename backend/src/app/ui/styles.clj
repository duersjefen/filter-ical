;; === UI STYLES AND JAVASCRIPT ===
;; CSS styles and JavaScript functions for interactive components

(ns app.ui.styles)

;; === ENHANCED STYLES ===

(def enhanced-styles
  "
  /* Smart Filter Builder */
  .smart-filter-builder { margin: 20px 0; }
  
  /* Search and Filter Controls */
  .search-filter-controls { 
    background: white; border: 1px solid #dee2e6; border-radius: 8px; 
    padding: 20px; margin-bottom: 20px; 
  }
  .search-controls { display: flex; flex-direction: column; gap: 15px; }
  .search-input-group { display: flex; gap: 10px; align-items: center; }
  .search-input-group input[type='text'] { 
    flex: 1; padding: 8px 12px; border: 1px solid #ced4da; 
    border-radius: 4px; font-size: 14px; 
  }
  .date-filters { display: flex; gap: 15px; flex-wrap: wrap; }
  .date-input-group { display: flex; align-items: center; gap: 8px; }
  .date-input-group label { font-weight: 500; min-width: 40px; }
  .date-input-group input[type='date'] { 
    padding: 6px 8px; border: 1px solid #ced4da; border-radius: 4px; 
  }
  .quick-filters { display: flex; gap: 8px; flex-wrap: wrap; }
  .btn-outline { 
    background: white; border: 1px solid #007bff; color: #007bff;
    padding: 6px 12px; border-radius: 4px; font-size: 12px;
  }
  .btn-outline:hover { background: #007bff; color: white; }
  
  .event-type-selector .type-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 10px; }
  .type-card { border: 2px solid #dee2e6; border-radius: 8px; padding: 15px; cursor: pointer; transition: all 0.2s; }
  .type-card:hover { border-color: #007bff; background: #f8f9ff; }
  .type-card.selected { border-color: #28a745; background: #f0fff4; }
  
  .type-label { cursor: pointer; display: block; }
  .type-info { margin-left: 25px; }
  .type-name { display: block; margin-bottom: 5px; }
  .type-count { color: #6c757d; font-size: 0.9em; }
  .type-preview { margin-top: 8px; }
  .sample-date { display: block; color: #6c757d; font-size: 0.8em; }
  
  /* Event Views */
  .event-stats { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; }
  .stat-card { text-align: center; background: white; padding: 15px; border-radius: 6px; }
  .stat-card .stat-number { font-size: 1.8em; font-weight: bold; color: #007bff; }
  .stat-card .stat-label { font-size: 0.9em; color: #6c757d; margin-top: 5px; }
  
  /* Event Cards */
  .event-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }
  .event-card { background: white; border: 1px solid #dee2e6; padding: 20px; border-radius: 8px; }
  .event-card h5 { margin-top: 0; color: #495057; }
  .event-count { color: #007bff; font-weight: bold; margin-bottom: 15px; }
  .sample-event { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #f1f1f1; }
  .event-date { font-weight: 500; }
  .event-location { color: #6c757d; font-size: 0.9em; }
  
  /* Filter Cards */
  .filter-card { 
    background: white; border: 1px solid #dee2e6; border-radius: 8px; 
    padding: 20px; margin-bottom: 15px; transition: box-shadow 0.2s;
  }
  .filter-card:hover { box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
  .filter-header { margin-bottom: 15px; }
  .filter-name { margin: 0; color: #495057; }
  .filter-calendar { color: #6c757d; font-size: 0.9em; }
  .type-tags { display: flex; gap: 5px; flex-wrap: wrap; margin-top: 5px; }
  .type-tag { 
    background: #e9ecef; color: #495057; padding: 4px 8px; border-radius: 12px; 
    font-size: 0.8em; white-space: nowrap;
  }
  .type-tag.more { background: #007bff; color: white; }
  .filter-actions { margin-top: 15px; display: flex; gap: 10px; }
  
  /* View Mode Buttons */
  .view-modes { margin: 20px 0; }
  .view-mode-buttons { display: flex; gap: 10px; margin-bottom: 20px; }
  .event-view { margin-top: 15px; }
  
  /* Enhanced Action Panel */
  .action-panel { 
    background: white; border: 1px solid #dee2e6; border-radius: 8px; 
    padding: 25px; margin: 30px 0; 
  }
  .action-panel h4 { margin-top: 0; color: #495057; }
  .action-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  .action-card { 
    border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; 
    display: flex; align-items: flex-start; gap: 15px; 
    transition: all 0.2s; 
  }
  .action-card:hover { border-color: #007bff; background: #f8f9ff; }
  .action-icon { 
    font-size: 2em; min-width: 50px; text-align: center; 
    background: #f8f9fa; padding: 10px; border-radius: 50%; 
  }
  .action-content { flex: 1; }
  .action-content h5 { margin: 0 0 8px 0; color: #495057; }
  .action-content p { margin: 0 0 15px 0; color: #6c757d; font-size: 0.9em; }
  .input-group { display: flex; gap: 10px; align-items: center; }
  .filter-name-input { 
    flex: 1; padding: 8px 12px; border: 1px solid #ced4da; 
    border-radius: 4px; font-size: 14px; 
  }
  
  /* Button Styles */
  .btn { 
    padding: 8px 16px; border: none; border-radius: 4px; 
    font-size: 14px; cursor: pointer; transition: all 0.2s;
  }
  .btn-primary { background: #007bff; color: white; }
  .btn-primary:hover { background: #0056b3; }
  .btn-success { background: #28a745; color: white; }
  .btn-success:hover { background: #1e7e34; }
  .btn-danger { background: #dc3545; color: white; }
  .btn-danger:hover { background: #c82333; }
  ")

;; === JAVASCRIPT HELPERS ===

(def filter-javascript
  "
  // Advanced filtering functions
  function filterEvents() {
    const searchText = document.getElementById('search-text').value.toLowerCase();
    const dateFrom = document.getElementById('date-from').value;
    const dateTo = document.getElementById('date-to').value;
    
    // Filter type cards
    document.querySelectorAll('.type-card').forEach(card => {
      const summary = card.querySelector('.type-name').textContent.toLowerCase();
      const dates = card.querySelector('.type-preview').textContent;
      
      let showCard = true;
      
      // Text search
      if (searchText && !summary.includes(searchText)) {
        showCard = false;
      }
      
      // Date filtering (simplified for now)
      // TODO: Implement proper date range filtering
      
      card.style.display = showCard ? 'block' : 'none';
    });
    
    // Filter table rows
    document.querySelectorAll('.events-table tbody tr').forEach(row => {
      const summary = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
      let showRow = true;
      
      if (searchText && !summary.includes(searchText)) {
        showRow = false;
      }
      
      row.style.display = showRow ? '' : 'none';
    });
  }
  
  function clearSearch() {
    document.getElementById('search-text').value = '';
    document.getElementById('date-from').value = '';
    document.getElementById('date-to').value = '';
    filterEvents();
  }
  
  function filterThisMonth() {
    const now = new Date();
    const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
    const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    
    document.getElementById('date-from').value = firstDay.toISOString().split('T')[0];
    document.getElementById('date-to').value = lastDay.toISOString().split('T')[0];
    filterEvents();
  }
  
  function filterThisYear() {
    const now = new Date();
    document.getElementById('date-from').value = now.getFullYear() + '-01-01';
    document.getElementById('date-to').value = now.getFullYear() + '-12-31';
    filterEvents();
  }
  
  function filterUpcoming() {
    const now = new Date();
    const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, now.getDate());
    
    document.getElementById('date-from').value = now.toISOString().split('T')[0];
    document.getElementById('date-to').value = nextMonth.toISOString().split('T')[0];
    filterEvents();
  }
  
  function clearFilters() {
    clearSearch();
    document.querySelectorAll('.type-card, .events-table tbody tr').forEach(el => {
      el.style.display = el.classList.contains('type-card') ? 'block' : '';
    });
  }
  
  function selectMeetings() {
    document.querySelectorAll('input[name=\"selected-summaries\"]').forEach(cb => {
      const row = cb.closest('.type-card') || cb.closest('tr');
      const summaryEl = row ? (row.querySelector('.type-name') || row.querySelector('td:nth-child(2)')) : null;
      if (summaryEl) {
        const summary = summaryEl.textContent.toLowerCase();
        cb.checked = summary.includes('meeting') || summary.includes('call') || summary.includes('sync');
      }
    });
  }
  
  function selectWorkEvents() {
    document.querySelectorAll('input[name=\"selected-summaries\"]').forEach(cb => {
      const row = cb.closest('.type-card') || cb.closest('tr');
      const summaryEl = row ? (row.querySelector('.type-name') || row.querySelector('td:nth-child(2)')) : null;
      if (summaryEl) {
        const summary = summaryEl.textContent.toLowerCase();
        cb.checked = summary.includes('work') || summary.includes('project') || summary.includes('standup');
      }
    });
  }
  
  function showView(viewMode) {
    // Update active button
    document.querySelectorAll('.view-mode-buttons .btn').forEach(btn => {
      btn.classList.remove('active');
    });
    document.getElementById('btn-' + viewMode).classList.add('active');
    
    // Show/hide views (this would be enhanced with proper view switching)
    console.log('Switching to view mode:', viewMode);
  }
  
  function saveFilter() {
    const filterName = document.getElementById('filter-name-input').value;
    const selectedSummaries = Array.from(document.querySelectorAll('input[name=\"selected-summaries\"]:checked')).map(cb => cb.value);
    
    if (selectedSummaries.length === 0) {
      alert('Please select at least one event type to filter');
      return;
    }
    
    // Submit form with selected summaries and filter name
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/filter/save';
    
    selectedSummaries.forEach(summary => {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'selected-summaries';
      input.value = summary;
      form.appendChild(input);
    });
    
    if (filterName) {
      const nameInput = document.createElement('input');
      nameInput.type = 'hidden';
      nameInput.name = 'filter-name';
      nameInput.value = filterName;
      form.appendChild(nameInput);
    }
    
    document.body.appendChild(form);
    form.submit();
  }
  
  function createSubscription() {
    const subscriptionName = document.getElementById('subscription-name-input').value;
    const selectedSummaries = Array.from(document.querySelectorAll('input[name=\"selected-summaries\"]:checked')).map(cb => cb.value);
    
    if (selectedSummaries.length === 0) {
      alert('Please select at least one event type to filter');
      return;
    }
    
    if (!subscriptionName) {
      alert('Please enter a subscription name');
      return;
    }
    
    // Create subscription and redirect to info page
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/filter/create-subscription';
    
    selectedSummaries.forEach(summary => {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'selected-summaries';
      input.value = summary;
      form.appendChild(input);
    });
    
    const nameInput = document.createElement('input');
    nameInput.type = 'hidden';
    nameInput.name = 'subscription-name';
    nameInput.value = subscriptionName;
    form.appendChild(nameInput);
    
    document.body.appendChild(form);
    form.submit();
  }
  ")