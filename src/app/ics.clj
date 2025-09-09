(ns app.ics
  (:require [clojure.string :as str]
            [app.core.types :refer [make-event event-uid event-summary event-start event-end]]
            [app.core.sync :refer [smart-fetch-calendar]]))

(defn fetch-ics [url]
  "Fetch iCal with smart caching"
  (try
    (when (and url (not (str/blank? url)))
      (smart-fetch-calendar url))
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
  (make-event (extract-property vevent-text "UID")
             (extract-property vevent-text "SUMMARY")
             (extract-property vevent-text "DTSTART")
             (extract-property vevent-text "DTEND")
             (extract-property vevent-text "LOCATION")
             (extract-property vevent-text "DESCRIPTION")
             vevent-text))

(defn events-for-url [url]
  (try
    (let [ics-content (fetch-ics url)]
      (->> ics-content
           extract-vevents
           (map parse-vevent)
           (filter #(not (str/blank? (event-uid %))))))
    (catch Exception e
      (println "Error parsing events:" (.getMessage e))
      [])))

(defn build-calendar [events]
  (let [header "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//iCal Viewer//EN\n"
        footer "END:VCALENDAR\n"
        event-data (str/join "\n" (map :raw events))]
    (str header event-data "\n" footer)))
