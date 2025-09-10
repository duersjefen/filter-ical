(ns ical-viewer.components.events
  (:require [re-frame.core :as rf]))

;; -- Event Filtering Components --

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

;; -- Event Display Components --

(defn event-row [event]
  [:tr.event-row
   [:td (:start event)]
   [:td (:summary event)]
   [:td (str (:start event) " - " (:end event))]])

(defn event-group-header [event-type events]
  [:tr.group-header
   [:td {:col-span 3} (str event-type " (" (count events) " events)")]])

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
                      [event-group-header event-type events]]
                     (map (fn [event]
                            ^{:key (:id event)}
                            [event-row event])
                          events)))
                  filtered-events))]]])))

(defn events-summary []
  (let [filtered-events @(rf/subscribe [:filtered-events])
        total-events (reduce + (map (comp count second) filtered-events))]
    [:div.events-summary
     [:p (str "Showing " total-events " events across " (count filtered-events) " categories")]]))