(ns ical-viewer.views
  (:require [re-frame.core :as rf]
            [reagent.core :as r]
            [clojure.string :as str]))

;; -- Utility Functions --
(defn format-date-range [start end]
  (cond
    (and start end (= start end)) start
    (and start end) (str start " → " end)
    start start
    :else "Date not specified"))

;; -- Statistics Component --
(defn statistics-panel []
  (let [stats @(rf/subscribe [:statistics])]
    [:div.form-section
     [:h4 "📊 Statistics"]
     [:div.stats
      [:div.stat
       [:div.stat-number (:total-events stats)]
       [:div.stat-label "Total Events"]]
      [:div.stat
       [:div.stat-number (:event-types stats)]
       [:div.stat-label "Event Types"]]
      [:div.stat
       [:div.stat-number (:years-covered stats)]
       [:div.stat-label "Years Covered"]]]]))

;; -- Calendar Selector --
(defn calendar-selector []
  (let [calendars @(rf/subscribe [:calendars])
        selected-calendar-id @(rf/subscribe [:selected-calendar-id])]
    [:div.calendar-selector
     [:h4 "📅 Select Calendar"]
     (if (seq calendars)
       [:div.calendar-list
        (for [calendar calendars]
          (let [calendar-id (:id calendar)
                is-selected? (= calendar-id selected-calendar-id)]
            ^{:key calendar-id}
            [:div.calendar-item
             {:class (when is-selected? "selected")}
             [:h5 (:name calendar)]
             [:p.calendar-url (:url calendar)]
             [:div.filter-actions
              [:button.btn 
               {:class (if is-selected? "btn-secondary" "btn-primary")
                :onClick #(do
                           (rf/dispatch [:select-calendar calendar-id])
                           (rf/dispatch [:load-calendar-events calendar-id]))}
               (if is-selected? "✅ Selected" "📊 Load Events")]]]))]
       [:div.empty-state
        [:p "No calendars found. Add calendars using the backend interface."]])]))

;; -- Filter Controls --
(defn search-controls []
  (let [search-text @(rf/subscribe [:search-text])
        [date-from date-to] @(rf/subscribe [:date-range])]
    [:div.search-filter-controls
     [:div.search-controls
      [:div.search-input-group
       [:input {:type "text"
                :placeholder "Search event types..."
                :value search-text
                :on-change #(rf/dispatch [:set-search-text (-> % .-target .-value)])}]
       [:button.btn.btn-outline {:on-click #(rf/dispatch [:set-search-text ""])} "Clear"]]
      
      [:div.date-filters
       [:div.date-input-group
        [:label "From:"]
        [:input {:type "date"
                 :value (or date-from "")
                 :on-change #(rf/dispatch [:set-date-range (-> % .-target .-value) date-to])}]]
       [:div.date-input-group
        [:label "To:"]
        [:input {:type "date"
                 :value (or date-to "")
                 :on-change #(rf/dispatch [:set-date-range date-from (-> % .-target .-value)])}]]]
      
      [:div.quick-filters
       [:button.btn.btn-outline {:on-click #(rf/dispatch [:clear-filters])} "Clear All"]]]]))

;; -- Event Type Selector --
(defn event-type-selector []
  (let [grouped-events @(rf/subscribe [:grouped-events])
        selected-types @(rf/subscribe [:selected-event-types])
        sorted-groups (sort-by (comp count second) > grouped-events)]
    [:div.event-type-selector
     [:h4 "📅 Select Event Types"]
     [:div.type-grid
      (for [[summary events] sorted-groups]
        (let [is-selected (contains? selected-types summary)]
          ^{:key summary}
          [:div.type-card {:class (when is-selected "selected")}
           [:label.type-label
            [:input {:type "checkbox"
                     :checked is-selected
                     :on-change #(rf/dispatch [:toggle-event-type summary])}]
            [:div.type-info
             [:strong.type-name summary]
             [:span.type-count (count events) " events"]
             [:div.type-preview
              (for [event (take 2 events)]
                ^{:key (:uid event)}
                [:small.sample-date (format-date-range (:start event) (:end event))])]]]]))]]))

;; -- View Mode Selector --
(defn view-mode-selector []
  (let [view-mode @(rf/subscribe [:view-mode])]
    [:div.view-modes
     [:div.view-mode-buttons
      [:button.btn {:class (when (= view-mode "table") "active")
                    :on-click #(rf/dispatch [:set-view-mode "table"])} 
       "📋 Table View"]
      [:button.btn {:class (when (= view-mode "cards") "active")
                    :on-click #(rf/dispatch [:set-view-mode "cards"])} 
       "🃏 Card View"]
      [:button.btn {:class (when (= view-mode "compact") "active")
                    :on-click #(rf/dispatch [:set-view-mode "compact"])} 
       "📝 Compact View"]]]))

;; -- Event Display --
(defn events-table [grouped-events]
  [:table.events-table
   [:thead
    [:tr [:th "Event Type"] [:th "Count"] [:th "Sample Dates"]]]
   [:tbody
    (for [[summary events] (sort-by first grouped-events)]
      ^{:key summary}
      [:tr
       [:td [:strong summary]]
       [:td (count events)]
       [:td (->> events
                (take 3)
                (map #(format-date-range (:start %) (:end %)))
                (str/join ", "))]])]])

(defn events-cards [grouped-events]
  [:div.event-cards
   (for [[summary events] (sort-by (comp count second) > grouped-events)]
     ^{:key summary}
     [:div.event-card
      [:h5 summary]
      [:div.event-count (count events) " events"]
      [:div.event-samples
       (for [event (take 3 events)]
         ^{:key (:uid event)}
         [:div.sample-event
          [:span.event-date (format-date-range (:start event) (:end event))]
          (when (:location event)
            [:span.event-location (:location event)])])]])])

(defn events-compact [grouped-events]
  [:div.event-compact
   (for [[summary events] grouped-events]
     ^{:key summary}
     [:div.compact-row
      [:span.event-name summary]
      [:span.event-count (count events)]])])

(defn event-display []
  (let [view-mode @(rf/subscribe [:view-mode])
        filtered-events @(rf/subscribe [:filtered-events])]
    [:div.event-view
     (case view-mode
       "table" [events-table filtered-events]
       "cards" [events-cards filtered-events]
       "compact" [events-compact filtered-events])]))

;; -- Loading and Error States --
(defn loading-spinner []
  [:div.loading-spinner
   [:div.spinner]
   [:p "Loading events..."]])

(defn error-message []
  (let [error @(rf/subscribe [:error])]
    (when error
      [:div.error-message
       [:h4 "⚠️ Error"]
       [:p error]
       [:button.btn.btn-primary {:on-click #(rf/dispatch [:set-error nil])} 
        "Dismiss"]])))

;; -- Action Panel --
(defn action-panel []
  (let [selected-types @(rf/subscribe [:selected-event-types])]
    [:div.action-panel
     [:h4 "📥 Save & Subscribe"]
     [:div.action-cards
      [:div.action-card
       [:div.action-icon "💾"]
       [:div.action-content
        [:h5 "Save Filtered Events"]
        [:p "Download selected events as an iCal file"]
        [:div.input-group
         [:input.filter-name-input {:type "text" :placeholder "Filter name (optional)"}]
         [:button.btn.btn-primary {:disabled (empty? selected-types)} "Save & Download"]]]]
      
      [:div.action-card
       [:div.action-icon "🔗"]
       [:div.action-content
        [:h5 "Create Subscription"]
        [:p "Generate a live subscription URL"]
        [:div.input-group
         [:input.filter-name-input {:type "text" :placeholder "Subscription name"}]
         [:button.btn.btn-success {:disabled (empty? selected-types)} "Create Subscription"]]]]]]))

;; -- Main Panel --
(defn main-panel []
  (let [loading? @(rf/subscribe [:loading?])]
    [:div
     [:header.header
      [:h1 "🗓️ iCal Filter & Subscribe"]
      [:p.subtitle "Easily filter your iCal feeds and create custom subscriptions"]]
     
     [error-message]
     
     (if loading?
       [loading-spinner]
       [:div.app-content
        [calendar-selector]
        [search-controls]
        [statistics-panel]
        [event-type-selector]
        [view-mode-selector]
        [event-display]
        [action-panel]])]))

;; Development helper
(defn debug-panel []
  (when goog.DEBUG
    (let [db @(rf/subscribe [:db])]
      [:div.debug-panel
       [:h4 "Debug Info"]
       [:pre (with-out-str (cljs.pprint/pprint db))]])))

;; Mock data loader for development
(defn load-mock-data []
  (rf/dispatch [:events-loaded 
                [{:uid "1" :summary "Team Standup" :start "2024-01-15" :end "2024-01-15"}
                 {:uid "2" :summary "Project Review" :start "2024-01-16" :end "2024-01-16"}
                 {:uid "3" :summary "Team Standup" :start "2024-01-17" :end "2024-01-17"}
                 {:uid "4" :summary "Client Meeting" :start "2024-01-18" :end "2024-01-18"}
                 {:uid "5" :summary "Sprint Planning" :start "2024-01-19" :end "2024-01-19"}]]))

;; Initialize with mock data in development
(when goog.DEBUG
  (js/setTimeout load-mock-data 1000))