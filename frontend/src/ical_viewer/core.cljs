(ns ical-viewer.core
  (:require [reagent.core :as r]
            [reagent.dom :as rdom]
            [re-frame.core :as rf]
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
  (rf/dispatch [:fetch-calendars])  ; Load calendars on app start
  (dev-setup)
  (mount-root))