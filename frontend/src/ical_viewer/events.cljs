(ns ical-viewer.events
  (:require [re-frame.core :as rf]
            [ajax.core :as ajax]
            [clojure.string :as str]
            [ical-viewer.db :as db]))

;; -- Initialize Database --
(rf/reg-event-db
 :initialize-db
 (fn [_ _]
   db/default-db))

;; -- User Management Events --
(rf/reg-event-db
 :set-login-username
 (fn [db [_ username]]
   (assoc-in db [:login-form :username] username)))

(rf/reg-event-fx
 :login
 (fn [{:keys [db]} _]
   (let [username (get-in db [:login-form :username])]
     (if (not-empty (str/trim username))
       {:db (-> db
                (assoc-in [:user :username] (str/trim username))
                (assoc-in [:user :logged-in?] true)
                (assoc :current-view :home)
                (dissoc :login-form))
        :dispatch [:fetch-calendars]}
       {:db (assoc db :error "Please enter a username")}))))

(rf/reg-event-fx
 :logout
 (fn [{:keys [db]} _]
   {:db (assoc db
               :current-view :login
               :user {:username nil :logged-in? false}
               :calendars []
               :filters []
               :events []
               :login-form {:username ""})}))

;; -- Navigation Events --
(rf/reg-event-db
 :set-current-view
 (fn [db [_ view]]
   (assoc db :current-view view)))

(rf/reg-event-fx
 :navigate-home
 (fn [{:keys [db]} _]
   {:db (assoc db :current-view :home :selected-calendar nil :events [])
    :dispatch [:fetch-calendars]}))

(rf/reg-event-fx
 :view-calendar
 (fn [{:keys [db]} [_ calendar-id]]
   (let [calendar (first (filter #(= (:id %) calendar-id) (:calendars db)))]
     {:db (assoc db 
                 :current-view :calendar
                 :selected-calendar calendar
                 :selected-calendar-id calendar-id
                 :loading? true)
      :dispatch [:load-calendar-events calendar-id]})))

;; -- Loading States --
(rf/reg-event-db
 :set-loading
 (fn [db [_ loading?]]
   (assoc db :loading? loading?)))

(rf/reg-event-db
 :set-error
 (fn [db [_ error]]
   (assoc db :error error :loading? false)))

(rf/reg-event-db
 :clear-error
 (fn [db _]
   (dissoc db :error)))

;; -- Calendar Management --
(rf/reg-event-db
 :set-new-calendar-name
 (fn [db [_ name]]
   (assoc-in db [:new-calendar :name] name)))

(rf/reg-event-db
 :set-new-calendar-url
 (fn [db [_ url]]
   (assoc-in db [:new-calendar :url] url)))

(rf/reg-event-fx
 :add-calendar
 (fn [{:keys [db]} _]
   (let [name (get-in db [:new-calendar :name])
         url (get-in db [:new-calendar :url])]
     (if (and (not-empty name) (not-empty url))
       {:db (assoc db :loading? true :error nil)
        :http-xhrio {:method :post
                     :uri "/api/calendars"
                     :params {:name name :url url}
                     :format (ajax/json-request-format)
                     :response-format (ajax/json-response-format {:keywords? true})
                     :on-success [:calendar-added]
                     :on-failure [:api-error]}}
       {:db (assoc db :error "Please provide both calendar name and URL")}))))

(rf/reg-event-fx
 :calendar-added
 (fn [{:keys [db]} [_ response]]
   {:db (-> db
            (assoc :loading? false)
            (dissoc :new-calendar))
    :dispatch [:fetch-calendars]}))

(rf/reg-event-fx
 :delete-calendar
 (fn [{:keys [db]} [_ calendar-id]]
   {:db (assoc db :loading? true :error nil)
    :http-xhrio {:method :delete
                 :uri (str "/api/calendars/" calendar-id)
                 :response-format (ajax/json-response-format {:keywords? true})
                 :on-success [:calendar-deleted]
                 :on-failure [:api-error]}}))

(rf/reg-event-fx
 :calendar-deleted
 (fn [{:keys [db]} [_ response]]
   {:db (assoc db :loading? false)
    :dispatch [:fetch-calendars]}))

;; -- API Calls --
(rf/reg-event-fx
 :fetch-calendars
 (fn [{:keys [db]} _]
   {:db (assoc db :loading? true :error nil)
    :http-xhrio {:method :get
                 :uri "/api/calendars"
                 :response-format (ajax/json-response-format {:keywords? true})
                 :on-success [:calendars-loaded]
                 :on-failure [:api-error]}}))

(rf/reg-event-db
 :calendars-loaded
 (fn [db [_ response]]
   (let [calendars (:calendars response)]
     (assoc db 
            :calendars calendars
            :loading? false))))

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
 (fn [db [_ response]]
   (let [events (:events response)
         grouped-events (group-by :summary events)
         statistics {:total-events (count events)
                     :event-types (count grouped-events)
                     :years-covered (count (into #{} (map #(-> % :start (subs 0 4)) events)))}]
     (assoc db 
            :events events
            :grouped-events grouped-events
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
 :clear-filters
 (fn [db _]
   (assoc db :selected-event-types #{})))

(rf/reg-event-db
 :set-quick-filter
 (fn [db [_ selected-types]]
   (assoc db :selected-event-types (set selected-types))))

(rf/reg-event-fx
 :save-filter
 (fn [{:keys [db]} _]
   (let [selected-types (:selected-event-types db)
         calendar-id (:selected-calendar-id db)
         filter-name (str "Filter " (count selected-types) " types")]
     {:db (assoc db :loading? true)
      :http-xhrio {:method :post
                   :uri "/api/filters"
                   :params {:calendar-id calendar-id
                            :name filter-name
                            :types (vec selected-types)}
                   :format (ajax/json-request-format)
                   :response-format (ajax/json-response-format {:keywords? true})
                   :on-success [:filter-saved]
                   :on-failure [:api-error]}})))

(rf/reg-event-fx
 :filter-saved
 (fn [{:keys [db]} [_ response]]
   {:db (assoc db :loading? false)
    :dispatch [:fetch-filters]}))

(rf/reg-event-fx
 :fetch-filters
 (fn [{:keys [db]} _]
   {:http-xhrio {:method :get
                 :uri "/api/filters"
                 :response-format (ajax/json-response-format {:keywords? true})
                 :on-success [:filters-loaded]
                 :on-failure [:api-error]}}))

(rf/reg-event-db
 :filters-loaded
 (fn [db [_ response]]
   (assoc db :filters (:filters response))))

(rf/reg-event-fx
 :delete-filter
 (fn [{:keys [db]} [_ filter-id]]
   {:http-xhrio {:method :delete
                 :uri (str "/api/filters/" filter-id)
                 :response-format (ajax/json-response-format {:keywords? true})
                 :on-success [:filter-deleted]
                 :on-failure [:api-error]}}))

(rf/reg-event-fx
 :filter-deleted
 (fn [{:keys [db]} [_ response]]
   {:dispatch [:fetch-filters]}))

(rf/reg-event-db
 :apply-filter
 (fn [db [_ filter-id]]
   (let [filter (first (filter #(= (:id %) filter-id) (:filters db)))]
     (assoc db :selected-event-types (set (:types filter))))))

;; -- Error Handling --
(rf/reg-event-db
 :api-error
 (fn [db [_ error]]
   (let [error-msg (or (-> error :response :message)
                       (:status-text error)
                       "An error occurred")]
     (assoc db :error error-msg :loading? false))))

;; -- View Mode --
(rf/reg-event-db
 :set-view-mode
 (fn [db [_ view-mode]]
   (assoc db :view-mode view-mode)))