(ns ical-viewer.views
  (:require [re-frame.core :as rf]
            [reagent.core :as r]))

;; -- Utility Functions --
(defn format-date-range [start end]
  (cond
    (and start end (= start end)) start
    (and start end) (str start " → " end)
    start start
    :else "Date not specified"))

;; -- Add New Calendar Form --
(defn add-calendar-form []
  [:div.form-section
   [:h2 "Add New Calendar"]
   [:form
    [:div.form-row
     [:label {:for "name"} "Calendar Name"]
     [:input {:id "name"
              :type "text" 
              :placeholder "My Work Calendar"
              :on-change #(rf/dispatch [:set-new-calendar-name (-> % .-target .-value)])}]]
    [:div.form-row
     [:label {:for "url"} "iCal URL"] 
     [:input {:id "url"
              :type "text"
              :placeholder "https://example.com/calendar.ics"
              :on-change #(rf/dispatch [:set-new-calendar-url (-> % .-target .-value)])}]]
    [:div.form-row
     [:button.btn.btn-primary
      {:type "button"
       :on-click #(rf/dispatch [:add-calendar])}
      "Add Calendar"]]]])

;; -- Calendar Management --
(defn calendar-card [calendar]
  (let [calendar-id (:id calendar)
        name (:name calendar)
        url (:url calendar)]
    [:div.calendar-card
     [:h3 name]
     [:p.calendar-url url]
     [:div.stats
      ;; TODO: Add event count stats
      ]
     [:div
      [:button.btn.btn-primary
       {:on-click #(rf/dispatch [:view-calendar calendar-id])}
       "📊 Filter Events"]
      [:button.btn.btn-danger
       {:on-click #(when (js/confirm "Delete this calendar and all its filters?")
                     (rf/dispatch [:delete-calendar calendar-id]))} 
       "🗑️ Delete"]]]))

(defn calendar-list []
  (let [calendars @(rf/subscribe [:calendars])]
    [:div
     [:h2 (str "Your Calendars (" (count calendars) ")")]
     (if (seq calendars)
       [:div.calendar-list
        (for [calendar calendars]
          ^{:key (:id calendar)}
          [calendar-card calendar])]
       [:div.empty-state
        [:p "No calendars yet. Add one using the form above."]])]))

;; -- Event Filtering Interface --
(defn event-type-filter []
  (let [grouped-events @(rf/subscribe [:grouped-events])
        selected-types @(rf/subscribe [:selected-event-types])]
    (when (seq grouped-events)
      [:div.filter-controls
       [:h4 "Filter by Event Type"]
       [:div.filter-actions
        (for [[event-type events] grouped-events]
          ^{:key event-type}
          [:label.filter-checkbox
           [:input {:type "checkbox"
                    :checked (contains? selected-types event-type)
                    :on-change #(rf/dispatch [:toggle-event-type event-type])}]
           [:span (str event-type " (" (count events) ")")]])]])))

(defn filter-actions []
  (let [selected-types @(rf/subscribe [:selected-event-types])
        has-selection? (seq selected-types)]
    [:div.filter-actions
     [:button.btn.btn-secondary
      {:on-click #(rf/dispatch [:clear-filters])}
      "Clear All"]
     (when has-selection?
       [:button.btn.btn-success
        {:on-click #(rf/dispatch [:save-filter])}
        "Save Filter"])]))

;; -- Event Display Table (Simplified) --
(defn events-table []
  (let [filtered-events @(rf/subscribe [:filtered-events])]
    (when (seq filtered-events)
      [:div.events-section
       [:div.filter-controls
        [:h4 "Events"]
        [event-type-filter]
        [filter-actions]]
       [:table.events-table
        [:thead
         [:tr
          [:th "Date"]
          [:th "Summary"] 
          [:th "Time"]]]
        [:tbody
         (doall
          (mapcat (fn [[event-type events]]
                    (concat 
                     [^{:key (str "header-" event-type)}
                      [:tr.group-header
                       [:td {:col-span 3} (str event-type " (" (count events) " events)")]]]
                     (map (fn [event]
                            ^{:key (:id event)}
                            [:tr.event-row
                             [:td (:start event)]
                             [:td (:summary event)]
                             [:td (str (:start event) " - " (:end event))]])
                          events)))
                  filtered-events))]]])))

;; -- Statistics Panel --
(defn statistics-panel []
  (let [stats @(rf/subscribe [:statistics])]
    [:div.form-section
     [:h4 "📊 Statistics"]
     [:div.stats
      [:div.stat
       [:div.stat-number (:total-events stats 0)]
       [:div.stat-label "Total Events"]]
      [:div.stat
       [:div.stat-number (:event-types stats 0)] 
       [:div.stat-label "Event Types"]]
      [:div.stat
       [:div.stat-number (:years-covered stats 0)]
       [:div.stat-label "Years Covered"]]]]))

;; -- Filter Management --
(defn saved-filters []
  (let [filters @(rf/subscribe [:filters])]
    (when (seq filters)
      [:div.form-section
       [:h4 "Saved Filters"]
       [:div.saved-filters
        (for [filter filters]
          ^{:key (:id filter)}
          [:div.filter-item
           [:span (:name filter)]
           [:div
            [:button.btn.btn-primary
             {:on-click #(rf/dispatch [:apply-filter (:id filter)])}
             "Apply"]
            [:button.btn.btn-danger
             {:on-click #(rf/dispatch [:delete-filter (:id filter)])}
             "Delete"]]])]])))

;; -- Main Application Views --
(defn home-view []
  [:div
   [:header.header
    [:h1 "🗓️ iCal Filter & Subscribe"]
    [:p.subtitle "Easily filter your iCal feeds and create custom subscriptions"]]
   
   [add-calendar-form]
   [calendar-list]])

(defn calendar-view []
  (let [selected-calendar @(rf/subscribe [:selected-calendar])
        loading? @(rf/subscribe [:loading?])]
    [:div
     [:header.header
      [:h1 (str "Filter: " (:name selected-calendar "Loading..."))]
      [:p.subtitle "Select event types to filter and create custom subscriptions"]
      [:div
       [:button.btn.btn-secondary
        {:on-click #(rf/dispatch [:navigate-home])}
        "← Back to Calendars"]]]
     
     (if loading?
       [:div.loading "Loading events..."]
       [:div
        [statistics-panel]
        [events-table]
        [saved-filters]])]))

;; -- Error Messages --
(defn error-message []
  (when-let [error @(rf/subscribe [:error])]
    [:div.error-message 
     [:strong "Error: "] error
     [:button.btn.btn-secondary
      {:on-click #(rf/dispatch [:clear-error])}
      "Dismiss"]]))

;; -- Loading Spinner --
(defn loading-spinner []
  [:div.loading
   [:h2 "Loading..."]
   [:p "Please wait while we load your data."]])

;; -- Main Panel (Router) --
(defn main-panel []
  (let [current-view @(rf/subscribe [:current-view])]
    [:div
     [error-message]
     
     (case current-view
       :home [home-view]
       :calendar [calendar-view]
       [home-view])]))