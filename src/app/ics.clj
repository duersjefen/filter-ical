(ns app.ics
  (:require [clojure.string :as str]
            [app.core.types :refer [make-event event-uid event-summary event-start event-end]]
            [app.core.sync :refer [smart-fetch-calendar]])
  (:import [java.time LocalDate LocalDateTime ZonedDateTime]
           [java.time.format DateTimeFormatter DateTimeParseException]))

;; Date formatting utilities
(def ical-date-formatter (DateTimeFormatter/ofPattern "yyyyMMdd"))
(def ical-datetime-formatter (DateTimeFormatter/ofPattern "yyyyMMdd'T'HHmmss"))
(def display-date-formatter (DateTimeFormatter/ofPattern "MMM d, yyyy"))
(def display-datetime-formatter (DateTimeFormatter/ofPattern "MMM d, yyyy 'at' h:mm a"))

(defn parse-ical-date [date-str]
  "Parse iCal date string (YYYYMMDD or YYYYMMDDTHHMMSS) into LocalDate/LocalDateTime"
  (when (and date-str (not (str/blank? date-str)))
    (try
      (cond
        ;; Date only format: 20240106
        (= 8 (count date-str))
        (LocalDate/parse date-str ical-date-formatter)
        
        ;; DateTime format: 20240106T120000
        (and (> (count date-str) 8) (.contains date-str "T"))
        (LocalDateTime/parse date-str ical-datetime-formatter)
        
        :else nil)
      (catch DateTimeParseException e
        (println "Error parsing date:" date-str (.getMessage e))
        nil))))

(defn format-date-for-display [parsed-date]
  "Format parsed date for user-friendly display"
  (when parsed-date
    (cond
      (instance? LocalDate parsed-date)
      (.format parsed-date display-date-formatter)
      
      (instance? LocalDateTime parsed-date)
      (.format parsed-date display-datetime-formatter)
      
      :else (str parsed-date))))

(defn format-date-range [start-date end-date]
  "Format date range for display, handling single-day and multi-day events"
  (let [start-parsed (parse-ical-date start-date)
        end-parsed (parse-ical-date end-date)]
    (cond
      ;; Both dates available
      (and start-parsed end-parsed)
      (if (= start-parsed end-parsed)
        (format-date-for-display start-parsed)
        (str (format-date-for-display start-parsed) " → " (format-date-for-display end-parsed)))
      
      ;; Only start date
      start-parsed
      (format-date-for-display start-parsed)
      
      ;; Only end date
      end-parsed  
      (str "until " (format-date-for-display end-parsed))
      
      ;; No valid dates
      :else
      "Date not specified")))

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
  "Extract property from vevent, handling parameters like VALUE=DATE"
  (let [pattern (re-pattern (str "(?m)^" property "(?:;[^:]*)?:(.*)$"))]
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
