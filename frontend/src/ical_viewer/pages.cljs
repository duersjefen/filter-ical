(ns ical-viewer.pages
  (:require [re-frame.core :as rf]
            [ical-viewer.components.calendar :as calendar]
            [ical-viewer.components.events :as events]
            [ical-viewer.components.filters :as filters]
            [ical-viewer.components.common :as common]
            [ical-viewer.components.auth :as auth]))

;; -- Application Pages --

(defn login-page []
  [:div
   [common/page-header
    "🗓️ iCal Filter & Subscribe"
    "Please log in to access your calendars"]

   [auth/login-form]])

(defn home-page []
  [:div
   [common/page-header
    "🗓️ iCal Filter & Subscribe"
    "Easily filter your iCal feeds and create custom subscriptions"
    [auth/user-info]]

   [calendar/add-calendar-form]
   [calendar/calendar-list]])

(defn calendar-detail-page []
  (let [selected-calendar @(rf/subscribe [:selected-calendar])
        loading? @(rf/subscribe [:loading?])]
    [:div
     [:div.page-header-with-user
      [auth/user-info]]

     [common/page-header
      (str "Filter: " (:name selected-calendar "Loading..."))
      "Select event types to filter and create custom subscriptions"
      [common/back-button "Back to Calendars" #(rf/dispatch [:navigate-home])]]

     (if loading?
       [common/loading-state "Loading events..."]
       [:div
        [calendar/calendar-stats]
        [events/events-table]
        [filters/saved-filters]])]))

(defn not-found-page []
  [common/empty-state
   "Page Not Found"
   "The page you're looking for doesn't exist."])