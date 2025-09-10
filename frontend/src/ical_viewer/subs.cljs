(ns ical-viewer.subs
  (:require [re-frame.core :as rf]
            [clojure.string :as str]))

;; -- Basic Data Subscriptions --
(rf/reg-sub
 :events
 (fn [db _]
   (:events db)))

(rf/reg-sub
 :calendars
 (fn [db _]
   (:calendars db)))

(rf/reg-sub
 :selected-calendar-id
 (fn [db _]
   (:selected-calendar-id db)))

(rf/reg-sub
 :statistics
 (fn [db _]
   (:statistics db)))

;; -- Filter Subscriptions --
(rf/reg-sub
 :selected-event-types
 (fn [db _]
   (:selected-event-types db)))

(rf/reg-sub
 :search-text
 (fn [db _]
   (:search-text db)))

(rf/reg-sub
 :date-range
 (fn [db _]
   [(:date-from db) (:date-to db)]))

;; -- View Subscriptions --
(rf/reg-sub
 :current-view
 (fn [db _]
   (:current-view db)))

(rf/reg-sub
 :selected-calendar
 (fn [db _]
   (:selected-calendar db)))

(rf/reg-sub
 :filters
 (fn [db _]
   (:filters db)))

(rf/reg-sub
 :view-mode
 (fn [db _]
   (:view-mode db)))

(rf/reg-sub
 :loading?
 (fn [db _]
   (:loading? db)))

(rf/reg-sub
 :error
 (fn [db _]
   (:error db)))

;; -- Computed Subscriptions --
(rf/reg-sub
 :grouped-events
 :<- [:events]
 (fn [events _]
   (group-by :summary events)))

(rf/reg-sub
 :filtered-events
 :<- [:grouped-events]
 :<- [:selected-event-types]
 :<- [:search-text]
 (fn [[grouped-events selected-types search-text] _]
   (let [search-lower (str/lower-case (or search-text ""))
         filtered-groups (if (empty? selected-types)
                          grouped-events
                          (select-keys grouped-events selected-types))]
     (if (empty? search-text)
       filtered-groups
       (into {} (filter (fn [[summary _]]
                         (str/includes? 
                          (str/lower-case summary) 
                          search-lower))
                       filtered-groups))))))