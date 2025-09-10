(ns ical-viewer.components.filters
  (:require [re-frame.core :as rf]))

;; -- Filter Management Components --

(defn filter-item [filter]
  [:div.filter-item
   [:span (:name filter)]
   [:div
    [:button.btn.btn-primary
     {:on-click #(rf/dispatch [:apply-filter (:id filter)])}
     "Apply"]
    [:button.btn.btn-danger
     {:on-click #(rf/dispatch [:delete-filter (:id filter)])}
     "Delete"]]])

(defn saved-filters []
  (let [filters @(rf/subscribe [:filters])]
    (when (seq filters)
      [:div.form-section
       [:h4 "Saved Filters"]
       [:div.saved-filters
        (for [filter filters]
          ^{:key (:id filter)}
          [filter-item filter])]])))

(defn filter-summary []
  (let [selected-types @(rf/subscribe [:selected-event-types])
        filters @(rf/subscribe [:filters])]
    [:div.filter-summary
     (when (seq selected-types)
       [:p (str "Current filter: " (count selected-types) " event types selected")])
     (when (seq filters)
       [:p (str (count filters) " saved filters available")])]))

(defn quick-filters []
  (let [grouped-events @(rf/subscribe [:grouped-events])
        common-types (->> grouped-events
                         (sort-by (comp count second) >)
                         (take 5)
                         (map first))]
    (when (seq common-types)
      [:div.quick-filters
       [:h5 "Quick Filters"]
       [:div.quick-filter-buttons
        (for [event-type common-types]
          ^{:key event-type}
          [:button.btn.btn-outline
           {:on-click #(rf/dispatch [:set-quick-filter #{event-type}])}
           event-type])]])))

(defn filter-stats []
  (let [grouped-events @(rf/subscribe [:grouped-events])
        selected-types @(rf/subscribe [:selected-event-types])
        filtered-events @(rf/subscribe [:filtered-events])]
    [:div.filter-stats
     [:div.stat-row
      [:span "Total event types: " (count grouped-events)]
      [:span "Selected: " (count selected-types)]
      [:span "Filtered events: " (reduce + (map (comp count second) filtered-events))]]]))