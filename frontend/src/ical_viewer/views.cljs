(ns ical-viewer.views
  (:require [re-frame.core :as rf]
            [ical-viewer.pages :as pages]
            [ical-viewer.components.common :as common]))

;; -- Main Application Router --
(defn main-panel []
  (let [current-view @(rf/subscribe [:current-view])
        logged-in? @(rf/subscribe [:logged-in?])]
    [:div
     [common/error-message]
     
     (case current-view
       :login [pages/login-page]
       :home (if logged-in? [pages/home-page] [pages/login-page])
       :calendar (if logged-in? [pages/calendar-detail-page] [pages/login-page])
       [pages/not-found-page])]))