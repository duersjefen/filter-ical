(ns ical-viewer.core
  (:require [reagent.core :as r]
            [reagent.dom :as rdom]
            [re-frame.core :as rf]
            [day8.re-frame.http-fx]  ; Register http-xhrio effect handler
            [ical-viewer.events]
            [ical-viewer.subs]
            [ical-viewer.views :as views]
            [ical-viewer.db :as db]))

(defn dev-setup []
  (when goog.DEBUG
    (enable-console-print!)
    (println "dev mode")))

(defn ^:dev/after-load mount-root []
  (rf/clear-subscription-cache!)
  (let [root-el (.getElementById js/document "app")]
    (when root-el
      (rdom/unmount-component-at-node root-el)
      (rdom/render [views/main-panel] root-el))))

(defn init! []
  (println "Initializing iCal Viewer ClojureScript app...")
  (rf/dispatch-sync [:initialize-db])
  ;; If user was logged in from localStorage, fetch their calendars
  (when @(rf/subscribe [:logged-in?])
    (rf/dispatch [:fetch-calendars]))
  (dev-setup)
  (mount-root))