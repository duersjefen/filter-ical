(ns app.ics
  (:require [clojure.string :as str]))

(defn fetch-ics [url]
  (try
    (when (and url (not (str/blank? url)))
      (slurp url))
    (catch Exception e
      (println "Error fetching iCal:" (.getMessage e))
      "")))

(defn extract-vevents [ics-content]
  (if (str/blank? ics-content)
    []
    (let [pattern #"(?s)BEGIN:VEVENT.*?END:VEVENT"]
      (re-seq pattern ics-content))))

(defn extract-property [vevent property]
  (let [pattern (re-pattern (str "(?m)^" property ":(.*)$"))]
    (when-let [match (re-find pattern vevent)]
      (str/trim (second match)))))

(defn parse-vevent [vevent-text]
  {:uid (extract-property vevent-text "UID")
   :summary (extract-property vevent-text "SUMMARY")
   :dtstart (extract-property vevent-text "DTSTART")
   :dtend (extract-property vevent-text "DTEND")
   :description (extract-property vevent-text "DESCRIPTION")
   :location (extract-property vevent-text "LOCATION")
   :raw vevent-text})

(defn events-for-url [url]
  (try
    (let [ics-content (fetch-ics url)]
      (->> ics-content
           extract-vevents
           (map parse-vevent)
           (filter #(not (str/blank? (:uid %))))))
    (catch Exception e
      (println "Error parsing events:" (.getMessage e))
      [])))

(defn build-calendar [events]
  (let [header "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//iCal Viewer//EN\n"
        footer "END:VCALENDAR\n"
        event-data (str/join "\n" (map :raw events))]
    (str header event-data "\n" footer)))
