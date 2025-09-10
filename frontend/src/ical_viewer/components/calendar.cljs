(ns ical-viewer.components.calendar
  (:require [re-frame.core :as rf]))

;; -- Calendar Management Components --

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

(defn calendar-stats []
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