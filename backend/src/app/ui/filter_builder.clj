;; === SMART FILTER BUILDER COMPONENTS ===
;; Interactive filtering interface with visual event type selection

(ns app.ui.filter-builder
  (:require [hiccup.form :refer [check-box]]
            [app.core.types :refer [event-start event-end]]
            [app.core.filtering :refer [group-by-summary]]
            [app.ics :refer [format-date-range]]))

;; === SMART FILTER BUILDER ===

(defn event-type-selector
  "Visual event type selector with counts and previews"
  [grouped-events & [selected]]
  [:div.event-type-selector
   [:h4 "📅 Select Event Types"]
   [:div.type-grid
    (for [[summary events] (sort-by (comp count second) > grouped-events)]
      (let [is-selected (contains? (set selected) summary)]
        [:div.type-card {:class (when is-selected "selected")}
         [:label.type-label
          (check-box "selected-summaries" summary is-selected)
          [:div.type-info
           [:strong.type-name summary]
           [:span.type-count (count events) " events"]]]]))]])

(defn smart-filter-builder
  "Complete smart filter builder interface"
  [events _calendar-id & [selected-summaries]]
  [:div.smart-filter-builder
   [:div.filter-section
    (event-type-selector (group-by-summary events) selected-summaries)]])

;; === FILTER MANAGEMENT ===

(defn filter-card
  "Enhanced filter display card"
  [filter calendar-name]
  [:div.filter-card
   [:div.filter-header
    [:h4.filter-name (:name filter)]
    [:span.filter-calendar "for " calendar-name]]
   [:div.filter-actions
    [:a.btn.btn-primary {:href (str "/view/" (:calendar-id filter) "?filter=" (:id filter))} 
     "📊 Apply"]
    [:a.btn.btn-success {:href (str "/filter/info/" (:id filter))} 
     "🔗 Subscribe"]]])