;; === ENHANCED UI COMPONENTS ===
;; Modern interface components with smart filtering

(ns app.ui.components
  (:require [hiccup.page :refer [html5]]
            [hiccup.form :refer [form-to label text-field submit-button hidden-field check-box]]
            [app.core.types :refer [calendar-id calendar-name calendar-url event-start event-end]]
            [app.core.filtering :refer [group-by-summary group-by-year]]
            [app.ics :refer [format-date-range]]))

;; === SMART FILTER BUILDER ===

(defn event-type-selector [grouped-events & [selected]]
  "Visual event type selector with counts and previews"
  [:div.event-type-selector
   [:h4 "📅 Select Event Types"]
   [:div.type-grid
    (for [[summary events] (sort-by (comp count second) > grouped-events)]
      (let [is-selected (contains? (set selected) summary)
            sample-events (take 2 events)]
        [:div.type-card {:class (when is-selected "selected")}
         [:label.type-label
          (check-box "selected-summaries" summary is-selected)
          [:div.type-info
           [:strong.type-name summary]
           [:span.type-count (count events) " events"]
           [:div.type-preview
            (for [event sample-events]
              [:small.sample-date (format-date-range (event-start event) (event-end event))])]]]]))]])

(defn smart-filter-builder [events calendar-id & [selected-summaries]]
  "Complete smart filter builder interface"
  [:div.smart-filter-builder
   [:div.filter-section
    (event-type-selector (group-by-summary events) selected-summaries)]])

;; === ENHANCED EVENT VIEWS ===

(defn event-statistics [events grouped-events]
  "Detailed statistics panel"
  (let [by-year (group-by-year events)
        total-events (count events)
        event-types (count grouped-events)
        years (sort (keys by-year))]
    [:div.event-stats
     [:h4 "📊 Statistics"]
     [:div.stats-grid
      [:div.stat-card
       [:div.stat-number total-events]
       [:div.stat-label "Total Events"]]
      [:div.stat-card
       [:div.stat-number event-types]
       [:div.stat-label "Event Types"]]
      [:div.stat-card
       [:div.stat-number (count years)]
       [:div.stat-label "Years Covered"]]]]))

(defn event-list-view [grouped-events & [view-mode]]
  "Multiple view modes for events"
  (case (or view-mode "table")
    "table"
    [:table.events-table
     [:thead
      [:tr [:th "Event Type"] [:th "Count"] [:th "Sample Dates"]]]
     [:tbody
      (for [[summary events] (sort-by first grouped-events)]
        [:tr
         [:td [:strong summary]]
         [:td (count events)]
         [:td (->> events
                  (take 3)
                  (map #(format-date-range (event-start %) (event-end %)))
                  (clojure.string/join ", "))]])]]
    
    "cards"
    [:div.event-cards
     (for [[summary events] (sort-by (comp count second) > grouped-events)]
       [:div.event-card
        [:h5 summary]
        [:div.event-count (count events) " events"]
        [:div.event-samples
         (for [event (take 3 events)]
           [:div.sample-event
            [:span.event-date (format-date-range (event-start event) (event-end event))]
            (when (:location event)
              [:span.event-location (:location event)])])]])]
    
    "compact"
    [:div.event-compact
     (for [[summary events] grouped-events]
       [:div.compact-row
        [:span.event-name summary]
        [:span.event-count (count events)]])]))

;; === FILTER MANAGEMENT ===

(defn filter-card [filter calendar-name]
  "Enhanced filter display card"
  [:div.filter-card
   [:div.filter-header
    [:h4.filter-name (:name filter)]
    [:span.filter-calendar "for " calendar-name]]
   
   [:div.filter-details
    [:div.filter-types
     [:strong "Event Types:"]
     [:div.type-tags
      (for [summary (take 5 (:selected-summaries filter))]
        [:span.type-tag summary])
      (when (> (count (:selected-summaries filter)) 5)
        [:span.type-tag.more "+" (- (count (:selected-summaries filter)) 5) " more"])]]]
   
   [:div.filter-actions
    [:a.btn.btn-primary {:href (str "/view/" (:calendar-id filter) "?filter=" (:id filter))} 
     "📊 Apply"]
    [:a.btn.btn-success {:href (str "/filter/info/" (:id filter))} 
     "🔗 Subscribe"]
    [:form {:method "POST" :action (str "/filter/delete/" (:id filter)) :style "display: inline;"}
     [:input.btn.btn-danger {:type "submit" :value "🗑️" 
                            :onclick "return confirm('Delete this filter?')"}]]]])

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
  ")