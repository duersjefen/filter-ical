;; Final logic.clj: parsing, persistence, and filtering.
(ns ical-viewer.logic
  (:require [clojure.edn :as edn]
            [clojure.string :as str]
            [clj-http.client :as http])
  (:import (net.fortuna.ical4j.data CalendarBuilder)
           (net.fortuna.ical4j.model.component VEvent)
           (java.io InputStreamReader File)
           (java.time ZonedDateTime)))

(def data-file "data/entries.edn")

(defn ensure-data-dir! []
  (let [f (File. data-file)
        parent (.getParentFile f)]
    (when parent
      (when-not (.exists parent)
        (.mkdirs parent)))))

(defn read-entries []
  (ensure-data-dir!)
  (let [f (File. data-file)]
    (if (.exists f)
      (try
        (edn/read-string (slurp f))
        (catch Exception _ {}))
      {})))

(defn write-entries! [m]
  (ensure-data-dir!)
  (spit data-file (pr-str m)))

(defn save-entry! [name url]
  (let [entries (or (read-entries) {})]
    (write-entries! (assoc entries name url))))

(defn get-entry [name]
  (get (read-entries) name))

(defn fetch-and-parse
  "Fetch an .ics URL and return a seq of maps with keys :summary :description :location :dtstart :dtend.
  Returns nil on error or when url is blank."
  [url]
  (when (and url (not (str/blank? url)))
    (let [resp (http/get url {:as :stream :throw-exceptions false})]
      (when (= 200 (:status resp))
        (with-open [r (InputStreamReader. (:body resp))]
          (let [builder (CalendarBuilder.)
                cal (.build builder r)
                comps (seq (.getComponents cal "VEVENT"))]
            (map (fn [^VEvent ev]
                   {:summary (some-> (.getProperty ev "SUMMARY") .getValue)
                    :description (some-> (.getProperty ev "DESCRIPTION") .getValue)
                    :location (some-> (.getProperty ev "LOCATION") .getValue)
                    :dtstart (some-> (.getProperty ev "DTSTART") .getValue)
                    :dtend (some-> (.getProperty ev "DTEND") .getValue)})
                 comps)))))))

(defn event-in-year? [event year]
  (when (and event year)
    (let [dt (or (:dtstart event) (:dtend event))]
      (when dt
        (try
          (let [z (ZonedDateTime/parse dt)]
            (= (.getYear z) year))
          (catch Exception _ false))))))

(defn events-for-entry [url year]
  (let [events (seq (fetch-and-parse url))]
    (if year
      (filter #(event-in-year? % year) events)
      events)))

(defn entries-with-events
  "Return a vector of maps {:name :url :events} for all saved entries. If year is provided,
	events are filtered to that year."
  ([] (entries-with-events nil))
  ([year]
   (let [entries (read-entries)]
     (->> entries
          (map (fn [[name url]]
                 {:name name :url url :events (vec (events-for-entry url year))}))
          (vec)))))

(defn list-entries
  "Return a seq of maps {:name :url :count} for all entries. If year given, counts are year-filtered."
  ([] (list-entries nil))
  ([year]
   (let [entries (read-entries)]
     (map (fn [[name url]]
            {:name name :url url :count (count (events-for-entry url year))})
          entries))))

(comment
  (require '[ical-viewer.user :as user])
  (user/reset))

