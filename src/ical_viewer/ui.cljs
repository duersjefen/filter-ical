 (ns ical-viewer.ui
  (:require [goog.dom :as gdom]
            [cljs.reader :as reader]
            [clojure.string :as str]))


(defn format-row [{:keys [summary dtstart dtend location]}]
  (str "<tr>"
       "<td>" (or summary "") "</td>"
       "<td>" (or dtstart "") "</td>"
       "<td>" (or dtend "") "</td>"
       "<td>" (or location "") "</td>"
       "</tr>"))


(defn render-events [events]
  (if (and events (seq events))
    (let [rows (->> events (map format-row) (apply str))
          table (str "<table border=1><thead><tr><th>Summary</th><th>Start</th><th>End</th><th>Location</th></tr></thead><tbody>" rows "</tbody></table>")]
      table)
    "<p>No events found.</p>"))


(defn mount [html]
  (set! (.-innerHTML (gdom/getElement "app")) html))


(defn api-base
  "Return API base URL. If running under shadow-cljs dev server (port 8700),
   point to the backend at localhost:3000 so fetches go to the real server."
  []
  (let [port (.-port js/location)]
    (if (= port "8700")
      "http://localhost:3000"
      "")))


(defn fetch-first-events []
  (let [base (api-base)
        url  (str base "/api/entries/first")]
    (-> (js/fetch url)
        (.then (fn [res]
                 (if (.-ok res)
                   (.text res)
                   (.then (.-text res) (fn [body] (throw (js/Error. (str "HTTP " (.-status res) " - " body))))))))
        (.then (fn [txt]
                 (let [edn (reader/read-string txt)]
                   (mount (render-events edn)))))
        (.catch (fn [err]
                  (mount (str "<p>Error loading events: " (.-message err) "</p>")))))))


;; clj-kondo:ignore
(defn init []
  (fetch-first-events))
