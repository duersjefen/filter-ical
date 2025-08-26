(ns app.storage
  (:require [clojure.java.io :as io]
            [clojure.edn :as edn]
            [clojure.string :as str]))

(def data-file "data/entries.edn")

(defn ensure-file! []
  (io/make-parents data-file)
  (when-not (.exists (io/file data-file))
    (spit data-file "[]")))

(ensure-file!)

(defonce entries
  (let [content (try
                  (slurp data-file)
                  (catch Exception _ "[]"))]
    (atom (if (str/blank? content)
            []
            (edn/read-string content)))))

(defn save! []
  (spit data-file (pr-str @entries)))

(defn next-id []
  (inc (apply max (cons 0 (map :id @entries)))))

(defn add-entry! [name url]
  (let [entry {:id (next-id)
               :name (str/trim name)
               :url (str/trim url)}]
    (swap! entries conj entry)
    (save!)
    entry))

(defn delete-entry! [id]
  (let [id (if (string? id) (Integer/parseInt id) id)]
    (swap! entries #(vec (remove (fn [e] (= (:id e) id)) %)))
    (save!)))

(defn get-entry [id]
  (let [id (if (string? id) (Integer/parseInt id) id)]
    (first (filter #(= (:id %) id) @entries))))

(defn all-entries []
  @entries)
