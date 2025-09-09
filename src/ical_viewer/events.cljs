(ns ical-viewer.events
  (:require [re-frame.core :as rf]
            [ajax.core :as ajax]
            [ical-viewer.db :as db]))

;; -- Initialize Database --
(rf/reg-event-db
 :initialize-db
 (fn [_ _]
   db/default-db))

;; -- Loading States --
(rf/reg-event-db
 :set-loading
 (fn [db [_ loading?]]
   (assoc db :loading? loading?)))

(rf/reg-event-db
 :set-error
 (fn [db [_ error]]
   (assoc db :error error :loading? false)))

;; -- Calendar Management --
(rf/reg-event-db
 :set-calendars
 (fn [db [_ calendars]]
   (assoc db :calendars calendars)))

(rf/reg-event-db
 :select-calendar
 (fn [db [_ calendar-id]]
   (assoc db :selected-calendar-id calendar-id)))

(rf/reg-event-fx
 :load-calendar-events
 (fn [{:keys [db]} [_ calendar-id]]
   {:db (assoc db :loading? true :error nil)
    :http-xhrio {:method :get
                 :uri (str "/api/calendar/" calendar-id "/events")
                 :response-format (ajax/json-response-format {:keywords? true})
                 :on-success [:events-loaded]
                 :on-failure [:api-error]}}))

(rf/reg-event-db
 :events-loaded
 (fn [db [_ events]]
   (let [grouped-events (group-by :summary events)
         statistics {:total-events (count events)
                     :event-types (count grouped-events)
                     :years-covered (count (into #{} (map #(-> % :start (subs 0 4)) events)))}]
     (assoc db 
            :events events
            :statistics statistics
            :loading? false))))

;; -- Filter Management --
(rf/reg-event-db
 :toggle-event-type
 (fn [db [_ event-type]]
   (let [selected-types (:selected-event-types db)]
     (assoc db :selected-event-types
            (if (contains? selected-types event-type)
              (disj selected-types event-type)
              (conj selected-types event-type))))))

(rf/reg-event-db
 :set-search-text
 (fn [db [_ search-text]]
   (assoc db :search-text search-text)))

(rf/reg-event-db
 :set-date-range
 (fn [db [_ date-from date-to]]
   (assoc db :date-from date-from :date-to date-to)))

(rf/reg-event-db
 :clear-filters
 (fn [db _]
   (assoc db 
          :selected-event-types #{}
          :search-text ""
          :date-from nil
          :date-to nil)))

;; -- View Management --
(rf/reg-event-db
 :set-view-mode
 (fn [db [_ view-mode]]
   (assoc db :view-mode view-mode)))

;; -- Error Handling --
(rf/reg-event-db
 :api-error
 (fn [db [_ error]]
   (assoc db :error (str "API Error: " (:status-text error)) :loading? false)))