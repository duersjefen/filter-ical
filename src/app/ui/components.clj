;; === ENHANCED UI COMPONENTS ===
;; Modern interface components with smart filtering

(ns app.ui.components
  (:require [hiccup.page :refer [html5]]
            [hiccup.form :refer [form-to label text-field submit-button hidden-field check-box]]
            [app.core.types :refer [calendar-id calendar-name calendar-url]]
            [app.core.filtering :refer [group-by-summary group-by-year]]))

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
              [:small.sample-date (or (:dtstart event) "No date")])]]]))]])

(defn year-timeline-selector [events & [selected-year]]
  "Interactive year timeline with event distribution"
  (let [by-year (group-by-year events)
        years (sort (keys by-year))]
    [:div.year-timeline
     [:h4 "📊 Filter by Year"]
     [:div.year-buttons
      (for [year years]
        [:button.year-btn
         {:class (when (= year selected-year) "selected")
          :onclick (str "filterByYear('" year "')")}
         [:span.year-label year]
         [:span.year-count (count (get by-year year)) " events"]])]]))

(defn quick-filter-presets [events calendar-id]
  "Pre-defined filter combinations for common use cases"
  (let [grouped (group-by-summary events)
        meeting-types (filter #(re-find #"(?i)(meeting|call|sync)" (first %)) grouped)
        work-types (filter #(re-find #"(?i)(work|project|standup)" (first %)) grouped)]
    [:div.quick-presets
     [:h4 "⚡ Quick Filters"]
     [:div.preset-buttons
      (when (seq meeting-types)
        [:button.preset-btn
         {:onclick "selectMeetings()"}
         "🤝 All Meetings (" (reduce + (map (comp count second) meeting-types)) ")"])
      (when (seq work-types)
        [:button.preset-btn
         {:onclick "selectWorkEvents()"}
         "💼 Work Events (" (reduce + (map (comp count second) work-types)) ")"])
      [:button.preset-btn
       {:onclick "selectRecent()"}
       "🕒 Recent (Last 30 days)"]
      [:button.preset-btn
       {:onclick "selectUpcoming()"}
       "📅 Upcoming"]]]))

(defn smart-filter-builder [events calendar-id & [selected-summaries]]
  "Complete smart filter builder interface"
  [:div.smart-filter-builder
   [:div.filter-section
    (event-type-selector (group-by-summary events) selected-summaries)]
   [:div.filter-section
    (year-timeline-selector events)]
   [:div.filter-section
    (quick-filter-presets events calendar-id)]])

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
       [:div.stat-label "Years Covered"]]
      [:div.stat-card
       [:div.stat-number (int (/ total-events (max 1 event-types)))]
       [:div.stat-label "Avg per Type"]]]
     
     (when (> (count years) 1)
       [:div.year-breakdown
        [:h5 "Events by Year"]
        [:div.year-bars
         (for [year years]
           [:div.year-bar
            [:div.bar-label year]
            [:div.bar-fill 
             {:style (str "width: " 
                         (* 100 (/ (count (get by-year year)) total-events)) "%")}]
            [:div.bar-count (count (get by-year year))]])]])]))

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
                  (map #(or (:dtstart %) "No date"))
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
            [:span.event-date (or (:dtstart event) "No date")]
            (when (:location event)
              [:span.event-location (:location event)])])]])]
    
    "compact"
    [:div.event-compact
     (for [[summary events] grouped-events]
       [:div.compact-row
        [:span.event-name summary]
        [:span.event-count (count events)]])]))

;; === ADVANCED FILTER MANAGEMENT ===

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
        [:span.type-tag.more "+" (- (count (:selected-summaries filter)) 5) " more"])]]
    
    [:div.filter-meta
     [:small "Created: " (when (:created-at filter)
                           (.format (java.text.SimpleDateFormat. "MMM dd, yyyy")
                                   (java.util.Date. (:created-at filter))))]]]
   
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
  .smart-filter-builder { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
  
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
  
  /* Year Timeline */
  .year-timeline { margin: 20px 0; }
  .year-buttons { display: flex; gap: 10px; flex-wrap: wrap; }
  .year-btn { 
    border: 2px solid #dee2e6; background: white; padding: 10px 15px; 
    border-radius: 8px; cursor: pointer; text-align: center; transition: all 0.2s;
  }
  .year-btn:hover { border-color: #007bff; background: #f8f9ff; }
  .year-btn.selected { border-color: #28a745; background: #f0fff4; }
  .year-label { display: block; font-weight: bold; }
  .year-count { display: block; font-size: 0.8em; color: #6c757d; }
  
  /* Quick Presets */
  .preset-buttons { display: flex; gap: 10px; flex-wrap: wrap; }
  .preset-btn { 
    background: #17a2b8; color: white; border: none; padding: 10px 15px; 
    border-radius: 6px; cursor: pointer; transition: background 0.2s;
  }
  .preset-btn:hover { background: #138496; }
  
  /* Event Views */
  .event-stats { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; }
  .stat-card { text-align: center; background: white; padding: 15px; border-radius: 6px; }
  .stat-card .stat-number { font-size: 1.8em; font-weight: bold; color: #007bff; }
  .stat-card .stat-label { font-size: 0.9em; color: #6c757d; margin-top: 5px; }
  
  .year-breakdown { margin-top: 20px; }
  .year-bars { display: flex; flex-direction: column; gap: 8px; }
  .year-bar { display: flex; align-items: center; gap: 10px; }
  .bar-label { min-width: 50px; font-weight: bold; }
  .bar-fill { 
    height: 20px; background: #007bff; border-radius: 3px; 
    min-width: 2px; display: flex; align-items: center; justify-content: center;
    color: white; font-size: 0.8em; font-weight: bold;
  }
  .bar-count { min-width: 30px; font-size: 0.9em; color: #6c757d; }
  
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
  .filter-meta { margin-top: 15px; padding-top: 15px; border-top: 1px solid #f1f1f1; }
  .filter-actions { margin-top: 15px; display: flex; gap: 10px; }
  ")

;; === JAVASCRIPT HELPERS ===

(def filter-javascript
  "
  function filterByYear(year) {
    // Clear all checkboxes first
    document.querySelectorAll('input[name=\"selected-summaries\"]').forEach(cb => cb.checked = false);
    
    // This would need to be enhanced to actually filter by year
    // For now, just show an alert
    alert('Year filter: ' + year + ' (Implementation needed)');
  }
  
  function selectMeetings() {
    document.querySelectorAll('input[name=\"selected-summaries\"]').forEach(cb => {
      const row = cb.closest('.type-card') || cb.closest('tr');
      const summaryEl = row.querySelector('.type-name') || row.querySelector('td:nth-child(2)');
      if (summaryEl) {
        const summary = summaryEl.textContent.toLowerCase();
        cb.checked = summary.includes('meeting') || summary.includes('call') || summary.includes('sync');
      }
    });
  }
  
  function selectWorkEvents() {
    document.querySelectorAll('input[name=\"selected-summaries\"]').forEach(cb => {
      const row = cb.closest('.type-card') || cb.closest('tr');
      const summaryEl = row.querySelector('.type-name') || row.querySelector('td:nth-child(2)');
      if (summaryEl) {
        const summary = summaryEl.textContent.toLowerCase();
        cb.checked = summary.includes('work') || summary.includes('project') || summary.includes('standup');
      }
    });
  }
  
  function selectRecent() {
    // This would need actual date filtering logic
    alert('Recent events filter (Implementation needed)');
  }
  
  function selectUpcoming() {
    // This would need actual date filtering logic  
    alert('Upcoming events filter (Implementation needed)');
  }
  ")