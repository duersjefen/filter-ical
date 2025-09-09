;; === EVENT DISPLAY COMPONENTS ===
;; Multiple view modes and statistics for events

(ns app.ui.event-display
  (:require [app.core.types :refer [event-start event-end]]
            [app.core.filtering :refer [group-by-year]]
            [app.ics :refer [format-date-range]]
            [clojure.string :as str]))

;; === ENHANCED EVENT VIEWS ===

(defn event-statistics
  "Detailed statistics panel"
  [events grouped-events]
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

(defn event-list-view
  "Multiple view modes for events"
  [grouped-events & [view-mode]]
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
                  (str/join ", "))]])]]
    
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

(defn view-mode-selector
  "Buttons to switch between different view modes"
  []
  [:div.view-modes
   [:div.view-mode-buttons
    [:button.btn {:onclick "showView('table')" :id "btn-table"} "📋 Table View"]
    [:button.btn {:onclick "showView('cards')" :id "btn-cards"} "🃏 Card View"] 
    [:button.btn {:onclick "showView('compact')" :id "btn-compact"} "📝 Compact View"]]
   [:div.event-view {:id "event-display"}
    "<!-- Events will be displayed here -->"]])

(defn action-panel
  "Enhanced action panel for save/download functionality"
  [calendar-id]
  [:div.action-panel
   [:h4 "📥 Save & Subscribe"]
   [:div.action-cards
    [:div.action-card
     [:div.action-icon "💾"]
     [:div.action-content
      [:h5 "Save Filtered Events"]
      [:p "Download selected events as an iCal file for import into your calendar app"]
      [:div.input-group
       [:input.filter-name-input {:type "text" :name "filter-name" 
                                  :placeholder "Enter filter name (optional)" 
                                  :id "filter-name-input"}]
       [:button.btn.btn-primary {:onclick "saveFilter()"} "Save & Download"]]]]
    
    [:div.action-card
     [:div.action-icon "🔗"]
     [:div.action-content
      [:h5 "Create Subscription"]
      [:p "Generate a live subscription URL that updates automatically with new events"]
      [:div.input-group
       [:input.filter-name-input {:type "text" :name "subscription-name" 
                                  :placeholder "Enter subscription name" 
                                  :id "subscription-name-input"}]
       [:button.btn.btn-success {:onclick "createSubscription()"} "Create Subscription"]]]]]])