(ns ical-viewer.components.common
  (:require [re-frame.core :as rf]))

;; -- Common UI Components --

(defn error-message []
  (when-let [error @(rf/subscribe [:error])]
    [:div.error-message 
     [:strong "Error: "] error
     [:button.btn.btn-secondary
      {:on-click #(rf/dispatch [:clear-error])}
      "Dismiss"]]))

(defn loading-spinner []
  [:div.loading
   [:h2 "Loading..."]
   [:p "Please wait while we load your data."]])

(defn loading-state [text]
  [:div.loading text])

(defn empty-state [title description]
  [:div.empty-state
   [:h3 title]
   [:p description]])

(defn page-header [title subtitle & actions]
  [:header.header
   [:h1 title]
   (when subtitle
     [:p.subtitle subtitle])
   (when (seq actions)
     [:div.header-actions
      actions])])

(defn back-button [text on-click]
  [:button.btn.btn-secondary
   {:on-click on-click}
   (str "← " text)])

(defn section-card [title & content]
  [:div.form-section
   (when title [:h4 title])
   content])

(defn button-group [& buttons]
  [:div.button-group
   buttons])

(defn stat-display [number label]
  [:div.stat
   [:div.stat-number number]
   [:div.stat-label label]])

(defn stats-panel [stats-map]
  [:div.stats
   (for [[label value] stats-map]
     ^{:key label}
     [stat-display value label])])

(defn form-row [label input]
  [:div.form-row
   (when label [:label label])
   input])

(defn card [& content]
  [:div.card content])

(defn badge [text type]
  [:span {:class (str "badge badge-" type)} text])