;; === ENHANCED UI COMPONENTS ===
(ns app.ui.components
  (:require [hiccup.core :refer [html]]
            [hiccup.form :refer [form-to text-field check-box select-options]]
            [app.core.filtering :as filtering]))

;; Smart Filter Builder UI
(defn filter-builder-ui [calendar-id events]
  (let [summaries (distinct (map :summary events))
        years (distinct (map #(subs (or (:dtstart %) "0000") 0 4) events))
        locations (distinct (remove empty? (map :location events)))
        grouped-by-summary (group-by :summary events)
        summary-counts (map (fn [[k v]] [k (count v)]) grouped-by-summary)]

    [:div.filter-builder
     [:h3 "🎯 Smart Filter Builder"]

     ;; Visual event type selector with counts
     [:div.event-type-selector
      [:h4 "Select Event Types"]
      [:div.event-chips
       (for [[summary count] (sort-by second > summary-counts)]
         [:label.event-chip
          (check-box {:class "event-type-checkbox"} "selected-summaries" summary)
          [:span.chip-content
           [:span.chip-name summary]
           [:span.chip-count count " events"]]])]]

     ;; Year selector with visual timeline
     [:div.year-selector
      [:h4 "Filter by Year"]
      [:div.year-timeline
       (for [year (sort years)]
         (let [year-events (count (filter #(.startsWith (or (:dtstart %) "") year) events))]
           [:label.year-chip
            [:input {:type "radio" :name "filter-year" :value year}]
            [:span.year-content
             [:span.year-label year]
             [:span.year-count year-events " events"]
             [:div.year-bar {:style (str "width: " (* 100 (/ year-events (count events))) "%")}]]]))]]

     ;; Quick filter presets
     [:div.quick-filters
      [:h4 "Quick Filters"]
      [:div.preset-buttons
       [:button.preset-btn {:onclick "selectFrequentEvents()"} "📊 Most Frequent"]
       [:button.preset-btn {:onclick "selectCurrentYear()"} "📅 This Year"]
       [:button.preset-btn {:onclick "selectMeetings()"} "👥 Meetings Only"]
       [:button.preset-btn {:onclick "selectWorkEvents()"} "💼 Work Events"]]]

     ;; Advanced options (collapsible)
     [:details.advanced-options
      [:summary "⚙️ Advanced Options"]
      [:div.advanced-controls
       [:label "Sort Results:"
        (html
         [:select {:name "sort-option"}
          [:option {:value "date"} "By Date"]
          [:option {:value "frequency"} "By Frequency"]
          [:option {:value "name"} "Alphabetically"]])]

       [:label "Group By:"
        (html
         [:select {:name "group-option"}
          [:option {:value "none"} "No Grouping"]
          [:option {:value "year"} "By Year"]
          [:option {:value "month"} "By Month"]
          [:option {:value "type"} "By Event Type"]])]

       [:label "Location Filter:"
        (text-field {:placeholder "Enter location pattern"} "location-filter")]]]]))

;; Modern Calendar View (alternative to table)
(defn calendar-grid-view [events grouped-events]
  [:div.calendar-views
   [:div.view-switcher
    [:button.view-btn.active {:onclick "showTableView()"} "📋 List View"]
    [:button.view-btn {:onclick "showGridView()"} "🗓️ Calendar View"]
    [:button.view-btn {:onclick "showStatsView()"} "📊 Statistics"]]

   ;; Table view (existing)
   [:div#table-view.view-panel.active
    (events-table-component grouped-events)]

   ;; Grid view (new)
   [:div#grid-view.view-panel
    [:div.events-grid
     (for [[summary events] grouped-events]
       [:div.event-type-card
        [:div.card-header
         (check-box "selected-summaries" summary)
         [:h4 summary]
         [:span.event-count (count events) " events"]]
        [:div.card-body
         [:div.event-preview
          (for [event (take 3 events)]
            [:div.event-item
             [:span.event-date (:dtstart event)]
             [:span.event-location (:location event)]])]
         (when (> (count events) 3)
           [:div.more-events "+" (- (count events) 3) " more events"])]])]]

   ;; Statistics view (new)
   [:div#stats-view.view-panel
    (statistics-component events grouped-events)]])

;; Statistics Component
(defn statistics-component [events grouped-events]
  [:div.statistics-panel
   [:div.stats-grid
    [:div.stat-card
     [:h3 "📅 Event Distribution"]
     [:div.year-distribution
      (let [by-year (group-by #(subs (or (:dtstart %) "0000") 0 4) events)]
        (for [[year year-events] (sort-by first by-year)]
          [:div.year-stat
           [:span.year-label year]
           [:div.year-bar
            [:div.year-fill {:style (str "width: " (* 100 (/ (count year-events) (count events))) "%")}]]
           [:span.year-count (count year-events)]]))]]

    [:div.stat-card
     [:h3 "🏆 Top Event Types"]
     [:div.top-events
      (for [[summary events] (take 5 (sort-by (comp count second) > grouped-events))]
        [:div.top-event-item
         [:span.event-name summary]
         [:span.event-count (count events) " events"]
         [:div.popularity-bar
          [:div.popularity-fill {:style (str "width: " (* 100 (/ (count events) (count (first (vals grouped-events))))) "%")}]]])]]

    [:div.stat-card
     [:h3 "📍 Locations"]
     [:div.location-stats
      (let [locations (frequencies (remove empty? (map :location events)))]
        (for [[location count] (take 5 (sort-by second > locations))]
          [:div.location-item
           [:span.location-name location]
           [:span.location-count count " events"]]))]]]])

;; Enhanced Filter Management
(defn saved-filters-panel [filters calendar-id]
  [:div.saved-filters-panel
   [:div.filters-header
    [:h3 "📁 Saved Filters (" (count filters) ")"]
    [:button.btn.btn-sm {:onclick "createFilterFromCurrent()"} "💾 Save Current Filter"]]

   (if (seq filters)
     [:div.filters-list
      (for [filter filters]
        [:div.filter-card
         [:div.filter-info
          [:h4 (:name filter)]
          [:p.filter-details
           (count (:selected-summaries filter)) " event types • "
           [:time (java.util.Date. (:created-at filter))]]
          [:div.filter-preview
           (for [summary (take 3 (:selected-summaries filter))]
             [:span.summary-tag summary])
           (when (> (count (:selected-summaries filter)) 3)
             [:span.more-summaries "+" (- (count (:selected-summaries filter)) 3) " more"])]]

         [:div.filter-actions
          [:button.btn.btn-sm.btn-primary {:onclick (str "applyFilter(" (:id filter) ")")}
           "✅ Apply"]
          [:button.btn.btn-sm.btn-success {:onclick (str "subscribeToFilter(" (:id filter) ")")}
           "🔗 Subscribe"]
          [:button.btn.btn-sm.btn-secondary {:onclick (str "duplicateFilter(" (:id filter) ")")}
           "📋 Duplicate"]
          [:button.btn.btn-sm.btn-danger {:onclick (str "deleteFilter(" (:id filter) ")")}
           "🗑️ Delete"]]])]

     [:div.empty-filters
      [:p "No saved filters yet."]
      [:p "Create filters to quickly access your preferred event selections."]])])

;; Enhanced JavaScript for interactivity
(defn enhanced-filter-js []
  [:script "
    // Smart filter functions
    function selectFrequentEvents() {
      const eventCounts = {};
      document.querySelectorAll('.event-chip').forEach(chip => {
        const name = chip.querySelector('.chip-name').textContent;
        const count = parseInt(chip.querySelector('.chip-count').textContent);
        eventCounts[name] = count;
      });
      
      const avgCount = Object.values(eventCounts).reduce((a,b) => a+b, 0) / Object.keys(eventCounts).length;
      
      document.querySelectorAll('.event-type-checkbox').forEach(cb => {
        const chipName = cb.closest('.event-chip').querySelector('.chip-name').textContent;
        cb.checked = eventCounts[chipName] >= avgCount;
      });
    }
    
    function selectCurrentYear() {
      const currentYear = new Date().getFullYear().toString();
      document.querySelectorAll('input[name=\"filter-year\"]').forEach(radio => {
        radio.checked = radio.value === currentYear;
      });
    }
    
    function selectMeetings() {
      document.querySelectorAll('.event-type-checkbox').forEach(cb => {
        const name = cb.closest('.event-chip').querySelector('.chip-name').textContent.toLowerCase();
        cb.checked = name.includes('meeting') || name.includes('call') || name.includes('standup');
      });
    }
    
    function selectWorkEvents() {
      document.querySelectorAll('.event-type-checkbox').forEach(cb => {
        const name = cb.closest('.event-chip').querySelector('.chip-name').textContent.toLowerCase();
        cb.checked = !name.includes('personal') && !name.includes('private') && !name.includes('birthday');
      });
    }
    
    // View switching
    function showTableView() { switchView('table-view'); }
    function showGridView() { switchView('grid-view'); }
    function showStatsView() { switchView('stats-view'); }
    
    function switchView(activeView) {
      document.querySelectorAll('.view-panel').forEach(panel => panel.classList.remove('active'));
      document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));
      document.getElementById(activeView).classList.add('active');
      event.target.classList.add('active');
    }
    
    // Filter management
    function createFilterFromCurrent() {
      const selectedSummaries = Array.from(document.querySelectorAll('input[name=\"selected-summaries\"]:checked')).map(cb => cb.value);
      const filterName = prompt('Name for this filter:');
      
      if (filterName && selectedSummaries.length > 0) {
        // Save filter via API
        saveCurrentFilter(filterName, selectedSummaries);
      }
    }
    
    function applyFilter(filterId) {
      window.location.href = window.location.pathname + '?filter=' + filterId;
    }
    
    // Real-time filter preview
    document.addEventListener('change', function(e) {
      if (e.target.classList.contains('event-type-checkbox')) {
        updateFilterPreview();
      }
    });
    
    function updateFilterPreview() {
      const selected = document.querySelectorAll('input[name=\"selected-summaries\"]:checked');
      const totalEvents = Array.from(selected).reduce((sum, cb) => {
        const count = parseInt(cb.closest('.event-chip').querySelector('.chip-count').textContent);
        return sum + count;
      }, 0);
      
      document.getElementById('filter-preview-count').textContent = totalEvents + ' events selected';
    }
  "])

;; Updated CSS for modern UI
(defn enhanced-styles []
  [:style "
    /* Enhanced Filter Builder Styles */
    .filter-builder { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 20px 0; }
    
    .event-chips { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; margin: 15px 0; }
    .event-chip { display: flex; align-items: center; background: #f8f9fa; border: 2px solid #e9ecef; border-radius: 8px; padding: 10px; cursor: pointer; transition: all 0.2s; }
    .event-chip:hover { background: #e9ecef; transform: translateY(-1px); }
    .event-chip input:checked + .chip-content { background: #007bff; color: white; border-radius: 4px; padding: 4px 8px; }
    .chip-name { font-weight: 500; }
    .chip-count { font-size: 0.85em; color: #6c757d; margin-left: 8px; }
    
    .year-timeline { display: flex; gap: 8px; flex-wrap: wrap; margin: 15px 0; }
    .year-chip { display: flex; align-items: center; background: #f8f9fa; border: 2px solid #e9ecef; border-radius: 6px; padding: 8px 12px; cursor: pointer; }
    .year-chip input:checked + .year-content { background: #28a745; color: white; border-radius: 4px; padding: 4px 8px; }
    .year-bar { height: 4px; background: #007bff; margin-top: 4px; border-radius: 2px; }
    
    .preset-buttons { display: flex; gap: 10px; flex-wrap: wrap; margin: 15px 0; }
    .preset-btn { padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9em; }
    .preset-btn:hover { background: #5a6268; transform: translateY(-1px); }
    
    /* Calendar Views */
    .calendar-views { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .view-switcher { display: flex; gap: 5px; margin-bottom: 20px; border-bottom: 2px solid #e9ecef; }
    .view-btn { padding: 10px 16px; background: none; border: none; cursor: pointer; border-bottom: 3px solid transparent; }
    .view-btn.active { border-bottom-color: #007bff; color: #007bff; font-weight: 500; }
    
    .view-panel { display: none; }
    .view-panel.active { display: block; }
    
    .events-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }
    .event-type-card { border: 1px solid #e9ecef; border-radius: 8px; overflow: hidden; }
    .card-header { background: #f8f9fa; padding: 15px; display: flex; align-items: center; gap: 10px; }
    .card-body { padding: 15px; }
    .event-preview { space-y: 8px; }
    .event-item { display: flex; justify-content: space-between; padding: 4px 0; font-size: 0.9em; }
    .more-events { color: #6c757d; font-style: italic; margin-top: 8px; }
    
    /* Statistics */
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
    .stat-card { border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; }
    .year-distribution, .top-events, .location-stats { space-y: 10px; }
    .year-stat, .top-event-item, .location-item { display: flex; align-items: center; gap: 10px; }
    .year-bar, .popularity-bar { flex: 1; height: 8px; background: #e9ecef; border-radius: 4px; overflow: hidden; }
    .year-fill, .popularity-fill { height: 100%; background: linear-gradient(90deg, #007bff, #28a745); }
    
    /* Saved Filters */
    .saved-filters-panel { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 20px 0; }
    .filters-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .filter-card { border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; margin: 10px 0; display: flex; justify-content: space-between; align-items: center; }
    .filter-card:hover { box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .filter-info h4 { margin: 0 0 5px 0; }
    .filter-details { font-size: 0.9em; color: #6c757d; margin: 5px 0; }
    .filter-preview { margin-top: 8px; }
    .summary-tag { display: inline-block; background: #e9ecef; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; margin: 2px; }
    .more-summaries { color: #6c757d; font-size: 0.8em; }
    .filter-actions { display: flex; gap: 5px; }
  "])