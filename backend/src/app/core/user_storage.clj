(ns app.core.user-storage
  "User-scoped data storage abstraction.
   
   This namespace provides a functional abstraction over data storage that:
   1. Isolates users' data from each other
   2. Uses pure functions for easy testing
   3. Abstracts the underlying storage mechanism
   4. Follows functional programming principles
   
   All operations require a user-context (username) for data isolation."
  (:require [clojure.string :as str]
            [clojure.java.io :as io]
            [clojure.edn :as edn]))

;; ============================================================================
;; Storage Protocol - Easy to swap implementations later
;; ============================================================================

(defprotocol UserDataStore
  "Protocol for user-scoped data storage operations"
  (get-user-calendars [store username] 
    "Get all calendars for a specific user")
  (add-user-calendar! [store username name url] 
    "Add a calendar for a specific user")  
  (get-user-calendar [store username calendar-id]
    "Get a specific calendar for a user")
  (delete-user-calendar! [store username calendar-id]
    "Delete a calendar for a specific user")
  (get-user-filters [store username]
    "Get all filters for a specific user")
  (add-user-filter! [store username name calendar-id types]
    "Add a filter for a specific user")
  (delete-user-filter! [store username filter-id]
    "Delete a filter for a specific user")
  (get-user-filter [store username filter-id]
    "Get a specific filter for a user"))

;; ============================================================================
;; Data Transformation Functions - Pure Functions 
;; ============================================================================

(defn user-key
  "Generate a user-scoped key for data partitioning"
  [username resource-type]
  (str username ":" resource-type))

(defn add-user-context
  "Add user context to a data record" 
  [record username]
  (assoc record :user username))

(defn filter-by-user
  "Filter a collection to only include records for a specific user"
  [coll username]
  (filter #(= (:user %) username) coll))

(defn next-user-id
  "Get next available ID for a user's resources"
  [user-records]
  (if (empty? user-records)
    1
    (inc (apply max (map :id user-records)))))

;; ============================================================================
;; File-based Implementation 
;; ============================================================================

(defrecord FileUserStore [calendars-atom filters-atom calendars-file filters-file]
  UserDataStore
  
  (get-user-calendars [_ username]
    (filter-by-user @calendars-atom username))
    
  (add-user-calendar! [_ username name url]
    (let [user-calendars (get-user-calendars _ username)
          new-id (next-user-id user-calendars)
          new-calendar (-> {:id new-id
                           :name (str/trim name)  
                           :url (str/trim url)
                           :metadata {:created-at (System/currentTimeMillis)}}
                          (add-user-context username))]
      (swap! calendars-atom conj new-calendar)
      (spit calendars-file (pr-str @calendars-atom))
      new-calendar))
      
  (get-user-calendar [_ username calendar-id]
    (first (filter #(and (= (:user %) username) 
                        (= (:id %) calendar-id))
                  @calendars-atom)))
                  
  (delete-user-calendar! [_ username calendar-id]
    (let [removed-calendar (get-user-calendar _ username calendar-id)]
      (when removed-calendar
        (swap! calendars-atom 
               #(vec (remove (fn [cal] 
                              (and (= (:user cal) username)
                                   (= (:id cal) calendar-id))) %)))
        (spit calendars-file (pr-str @calendars-atom))
        removed-calendar)))
        
  (get-user-filters [_ username]
    (filter-by-user @filters-atom username))
    
  (add-user-filter! [_ username name calendar-id types]
    (let [user-filters (get-user-filters _ username)
          new-id (next-user-id user-filters)
          new-filter (-> {:id new-id
                         :name (str/trim name)
                         :calendar-id calendar-id
                         :types (vec types)
                         :metadata {:created-at (System/currentTimeMillis)}}
                        (add-user-context username))]
      (swap! filters-atom conj new-filter)
      (spit filters-file (pr-str @filters-atom)) 
      new-filter))
      
  (delete-user-filter! [_ username filter-id]
    (let [removed-filter (first (filter #(and (= (:user %) username)
                                              (= (:id %) filter-id))
                                       @filters-atom))]
      (when removed-filter
        (swap! filters-atom
               #(vec (remove (fn [filt]
                              (and (= (:user filt) username)
                                   (= (:id filt) filter-id))) %)))
        (spit filters-file (pr-str @filters-atom))
        removed-filter)))
        
  (get-user-filter [_ username filter-id] 
    (first (filter #(and (= (:user %) username)
                        (= (:id %) filter-id))
                  @filters-atom))))

;; ============================================================================
;; Factory Functions
;; ============================================================================

(defn create-file-store
  "Create a file-based user data store"
  [calendars-file filters-file]
  (let [ensure-file! (fn [file default-content]
                       (io/make-parents file)
                       (when-not (.exists (io/file file))
                         (spit file default-content)))
        
        load-data (fn [file]
                    (try
                      (let [content (slurp file)]
                        (if (str/blank? content)
                          []
                          (edn/read-string content)))
                      (catch Exception _ [])))]
    
    ; Ensure files exist
    (ensure-file! calendars-file "[]")
    (ensure-file! filters-file "[]")
    
    ; Create store with loaded data
    (->FileUserStore
      (atom (load-data calendars-file))
      (atom (load-data filters-file)) 
      calendars-file
      filters-file)))

;; ============================================================================
;; Default Store Instance 
;; ============================================================================

(def default-store
  "Default file-based store instance - can be easily swapped later"
  (create-file-store "data/user-calendars.edn" "data/user-filters.edn"))

;; ============================================================================
;; Public API Functions - These hide the store implementation
;; ============================================================================

(defn get-calendars-for-user
  "Get all calendars for a user (high-level API)"
  [username]
  (get-user-calendars default-store username))

(defn add-calendar-for-user!
  "Add a calendar for a user (high-level API)"
  [username name url]
  (add-user-calendar! default-store username name url))

(defn get-calendar-for-user
  "Get a specific calendar for a user (high-level API)"
  [username calendar-id]
  (get-user-calendar default-store username calendar-id))

(defn delete-calendar-for-user!
  "Delete a calendar for a user (high-level API)"
  [username calendar-id]
  (delete-user-calendar! default-store username calendar-id))

(defn get-filters-for-user
  "Get all filters for a user (high-level API)" 
  [username]
  (get-user-filters default-store username))

(defn add-filter-for-user!
  "Add a filter for a user (high-level API)"
  [username name calendar-id types]
  (add-user-filter! default-store username name calendar-id types))

(defn delete-filter-for-user!
  "Delete a filter for a user (high-level API)"
  [username filter-id]
  (delete-user-filter! default-store username filter-id))

(defn get-filter-for-user
  "Get a specific filter for a user (high-level API)"
  [username filter-id]
  (get-user-filter default-store username filter-id))