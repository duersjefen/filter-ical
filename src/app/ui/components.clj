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
              [:small.sample-date (or (:dtstart event) "No date")])]]]]))])

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
  ")

;; === JAVASCRIPT HELPERS ===

(def filter-javascript
  "
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