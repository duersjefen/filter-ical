;; Minimal, clean iCal viewer baseline

(ns app.ical-viewer
  (:gen-class)
  (:require [compojure.core :refer [defroutes GET POST]]
            [compojure.route :as route]
            [ring.adapter.jetty :refer [run-jetty]]
            [ring.middleware.params :refer [wrap-params]]
            [ring.util.response :as response]
            [hiccup.page :refer [html5]]
            [hiccup.form :refer [form-to label text-field submit-button hidden-field check-box]]
            [clojure.java.io :as io]
            [clojure.edn :as edn]
            [clojure.string :as str]))

;; storage
(def data-file "data/entries.edn")

(defn ensure-file! []
  (io/make-parents data-file)
  (when (not (.exists (io/file data-file)))
    (spit data-file "[]")))

(ensure-file!)

;; Minimal, clean iCal viewer baseline

(ns app.ical-viewer
  (:gen-class)
  (:require [compojure.core :refer [defroutes GET POST]]
            [compojure.route :as route]
            [ring.adapter.jetty :refer [run-jetty]]
            [ring.middleware.params :refer [wrap-params]]
            [ring.util.response :as response]
            [hiccup.page :refer [html5]]
            [hiccup.form :refer [form-to label text-field submit-button hidden-field check-box]]
            [clojure.java.io :as io]
            [clojure.edn :as edn]
            [clojure.string :as str]))

;; storage
(def data-file "data/entries.edn")

(defn ensure-file! []
  (io/make-parents data-file)
  (when (not (.exists (io/file data-file)))
    (spit data-file "[]")))

(ensure-file!)

(defonce entries
  (let [s (try (slurp data-file) (catch Exception _ ""))]
    (atom (if (str/blank? s) [] (edn/read-string s)))))

(defn save! []
  (spit data-file (pr-str @entries)))

(defn next-id []
  (inc (apply max (cons 0 (map :id @entries)))))

(defn add-entry! [name url]
  (let [e {:id (next-id) :name (str/trim name) :url (str/trim url)}]
    (swap! entries conj e)
    (save!)
    e))

(defn delete-entry! [id]
  (let [id (if (string? id) (Integer/parseInt id) id)]
    (swap! entries #(vec (remove (fn [e] (= (:id e) id)) %)))
    (save!)))

;; fetching/parsing (naive)
(defn fetch-ics [url]
  (try
    (when (and url (not (str/blank? url)))
      (slurp url))
    (catch Exception _ "")))

(defn extract-vevents [ics]
  (if (str/blank? ics)
    []
    (let [re #"(?s)BEGIN:VEVENT.*?END:VEVENT"]
      (mapv identity (re-seq re ics)))))

(defn prop-from [vevent prop]
  (let [re (re-pattern (str "(?m)^" (java.util.regex.Pattern/quote prop) ":(.*)$"))]
    (some-> (re-find re vevent) second str/trim)))

(defn parse-vevent [vevent]
  {:uid     (prop-from vevent "UID")
   :summary (prop-from vevent "SUMMARY")
   ;; Minimal, clean iCal viewer baseline

   (ns app.ical-viewer
     (:gen-class)
     (:require [compojure.core :refer [defroutes GET POST]]
               [compojure.route :as route]
               [ring.adapter.jetty :refer [run-jetty]]
               [ring.middleware.params :refer [wrap-params]]
               [ring.util.response :as response]
               [hiccup.page :refer [html5]]
               [hiccup.form :refer [form-to label text-field submit-button hidden-field check-box]]
               [clojure.java.io :as io]
               [clojure.edn :as edn]
               [clojure.string :as str]))

   ;; storage
   (def data-file "data/entries.edn")

   (defn ensure-file! []
     (io/make-parents data-file)
     (when (not (.exists (io/file data-file)))
       (spit data-file "[]")))

   (ensure-file!)

   (defonce entries
     (let [s (try (slurp data-file) (catch Exception _ ""))]
       (atom (if (str/blank? s) [] (edn/read-string s)))))

   (defn save! []
     (spit data-file (pr-str @entries)))

   (defn next-id []
     (inc (apply max (cons 0 (map :id @entries)))))

   (defn add-entry! [name url]
     (let [e {:id (next-id) :name (str/trim name) :url (str/trim url)}]
       (swap! entries conj e)
       (save!)
       e))

   (defn delete-entry! [id]
     (let [id (if (string? id) (Integer/parseInt id) id)]
       (swap! entries #(vec (remove (fn [e] (= (:id e) id)) %)))
       (save!)))

   ;; fetching/parsing (naive)
   (defn fetch-ics [url]
     (try
       (when (and url (not (str/blank? url)))
         (slurp url))
       (catch Exception _ "")))

   (defn extract-vevents [ics]
     (if (str/blank? ics)
       []
       (let [re #"(?s)BEGIN:VEVENT.*?END:VEVENT"]
         (mapv identity (re-seq re ics)))))

   (defn prop-from [vevent prop]
     (let [re (re-pattern (str "(?m)^" (java.util.regex.Pattern/quote prop) ":(.*)$"))]
       (some-> (re-find re vevent) second str/trim)))

   (defn parse-vevent [vevent]
     {:uid     (prop-from vevent "UID")
      :summary (prop-from vevent "SUMMARY")
      :dtstart (prop-from vevent "DTSTART")
      :dtend   (prop-from vevent "DTEND")
      :raw     vevent})

   (defn events-for-entry [entry]
     (let [ics (fetch-ics (:url entry))]
       (->> (extract-vevents ics)
            (mapv parse-vevent))))

   (defn build-calendar [events]
     (let [hdr "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//simple//EN\n"
           ftr "END:VCALENDAR\n"]
       (apply str hdr (map :raw events) ftr)))

   (defn layout [title & body]
     (html5
      [:head
       [:meta {:charset "utf-8"}]
       [:meta {:name "viewport" :content "width=device-width,initial-scale=1"}]
       [:title (or title "iCal Viewer")]
       [:style "body{font-family:Segoe UI,Arial,sans-serif;padding:12px}"]]
      [:body body]))

   (defn home-page []
     (layout "iCal Viewer"
             [:h1 "iCal Viewer"]
             [:h2 "Saved calendars"]
             (if (seq @entries)
               [:ul
                (for [{:keys [id name]} @entries]
                  [:li [:strong name] " — " [:a {:href (str "/view/" id)} "view"] " "
                   (form-to [:post (str "/delete/" id)] (submit-button "Delete"))])]
               [:p "No calendars yet."])

             [:hr]
             [:h3 "Add calendar"]
             (form-to [:post "/add"]
                      (label "name" "Name: ") (text-field "name") [:br]
                      (label "url" "iCal URL: ") (text-field {:size 80} "url") [:br]
                      (submit-button "Add"))))

   (defn view-page [entry events]
     (layout (str "View: " (:name entry))
             [:p [:a {:href "/"} "\u2190 Back"]]
             [:h2 (:name entry)]
             [:p [:small (:url entry)]]
             (if (seq events)
               (let [rows (for [{:keys [uid summary dtstart dtend]} events]
                            [:tr
                             [:td (check-box "selected" uid)]
                             [:td (or summary "")] [:td (or dtstart "")] [:td (or dtend "")]])]
                 (form-to [:post "/generate"]
                          (hidden-field "entry-id" (:id entry))
                          [:table
                           [:thead [:tr [:th "Select"] [:th "Summary"] [:th "Start"] [:th "End"]]]
                           [:tbody (vec rows)]]
                          (submit-button "Generate .ics")))
               [:p "No events found."]))

     (defroutes routes
       (GET "/" [] (home-page))

       (POST "/add" {params :params}
         (let [name (get params "name") url (get params "url")]
           (when (and (not (str/blank? name)) (not (str/blank? url)))
             (add-entry! name url))
           (response/redirect "/")))

       (POST "/delete/:id" [id]
         (delete-entry! id)
         (response/redirect "/"))

       (GET "/view/:id" [id]
         (if-let [e (some #(when (= (:id %) (Integer/parseInt id)) %) @entries)]
           (view-page e (events-for-entry e))
           (response/redirect "/")))

       (POST "/generate" {params :params}
         (let [entry-id (get params "entry-id")
               sel (get params "selected")
               selected (cond
                          (nil? sel) []
                          (string? sel) [sel]
                          :else (vec sel))
               entry (some #(when (= (:id %) (Integer/parseInt entry-id)) %) @entries)
               events (if entry (events-for-entry entry) [])
               chosen (filterv (fn [e] (some #(= (:uid e) %) selected)) events)]
           (if (seq chosen)
             {:status 200
              :headers {"Content-Type" "text/calendar"
                        "Content-Disposition" (str "attachment; filename=filtered-" (:id entry) ".ics")}
              :body (build-calendar chosen)}
             (response/redirect (str "/view/" entry-id)))))

       (route/not-found "Not Found"))

     (def app (-> routes wrap-params))

     (defn -main [& _]
       (let [p 3000]
         (println "Starting server on port" p)
         (run-jetty #'app {:port p :join? false})))
