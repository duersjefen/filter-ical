(ns app.server-test
  (:require [clojure.test :refer [deftest is testing]]
            [app.server :as server]
            [app.storage :as storage]
            [ring.mock.request :as mock]
            [cheshire.core :as json]))

;; Test the API endpoints of our clean backend

(defn parse-json-response
  "Parse JSON response body if it's a string, otherwise return as-is"
  [response]
  (let [body (:body response)]
    (if (string? body)
      (json/parse-string body true)
      body)))

(deftest health-endpoint-test
  (testing "Health endpoint returns healthy status"
    (let [request (mock/request :get "/health")
          response (server/app request)]
      (is (= 200 (:status response)))
      (is (= "application/json" (get-in response [:headers "Content-Type"])))
      (let [body (json/parse-string (:body response) true)]
        (is (= "healthy" (:status body)))
        (is (= "ical-viewer" (:service body)))))))

(deftest root-redirect-test
  (testing "Root redirects to /app"
    (let [request (mock/request :get "/")
          response (server/app request)]
      (is (= 302 (:status response)))
      (is (= "/app" (get-in response [:headers "Location"]))))))

(deftest api-calendars-test
  (testing "GET /api/calendars returns calendar list"
    (let [request (mock/request :get "/api/calendars")
          response (server/app request)
          body (parse-json-response response)]
      (is (= 200 (:status response)))
      (is (contains? body :calendars))))

  (testing "POST /api/calendars creates new calendar"
    (let [calendar-data {:name "Test Calendar" :url "https://example.com/cal.ics"}
          request (-> (mock/request :post "/api/calendars")
                     (mock/content-type "application/json")
                     (mock/body (json/generate-string calendar-data)))
          response (server/app request)
          body (parse-json-response response)]
      (is (= 201 (:status response)))
      (is (contains? body :message))
      (is (contains? body :id))))

  (testing "POST /api/calendars validates required fields"
    (let [invalid-data {:name ""}
          request (-> (mock/request :post "/api/calendars")
                     (mock/content-type "application/json")
                     (mock/body (json/generate-string invalid-data)))
          response (server/app request)
          body (parse-json-response response)]
      (is (= 400 (:status response)))
      (is (contains? body :error)))))

(deftest api-filters-test
  (testing "GET /api/filters returns filter list"
    (let [request (mock/request :get "/api/filters")
          response (server/app request)
          body (parse-json-response response)]
      (is (= 200 (:status response)))
      (is (contains? body :filters))))

  (testing "POST /api/filters creates new filter"
    ;; First create a calendar to filter
    (let [calendar (storage/add-entry! "Test Cal" "https://example.com/test.ics")
          filter-data {:calendar-id (:id calendar)
                       :name "Test Filter"
                       :types ["Meeting" "Event"]}
          request (-> (mock/request :post "/api/filters")
                     (mock/content-type "application/json")
                     (mock/body (json/generate-string filter-data)))
          response (server/app request)
          body (parse-json-response response)]
      (is (= 201 (:status response)))
      (is (contains? body :message))
      (is (contains? body :id))))

  (testing "POST /api/filters validates required fields"
    (let [invalid-data {:name "Missing calendar-id"}
          request (-> (mock/request :post "/api/filters")
                     (mock/content-type "application/json")
                     (mock/body (json/generate-string invalid-data)))
          response (server/app request)
          body (parse-json-response response)]
      (is (= 400 (:status response)))
      (is (contains? body :error)))))

(deftest filter-events-function-test
  (testing "filter-events-by-summaries filters correctly"
    (let [events [{:summary "Meeting" :uid "1"}
                  {:summary "Meeting" :uid "2"}  
                  {:summary "Lunch" :uid "3"}
                  {:summary "Workshop" :uid "4"}]
          selected-summaries ["Meeting" "Lunch"]
          filtered (server/filter-events-by-summaries events selected-summaries)]
      (is (= 3 (count filtered)))
      (is (every? #(contains? #{"Meeting" "Lunch"} (:summary %)) filtered))))

  (testing "filter-events-by-summaries returns empty when no summaries selected"
    (let [events [{:summary "Meeting" :uid "1"}]
          filtered (server/filter-events-by-summaries events [])]
      (is (empty? filtered)))))

;; Comprehensive API test coverage complete

(deftest not-found-test
  (testing "Unknown routes return 404"
    (let [request (mock/request :get "/nonexistent")
          response (server/app request)]
      (is (= 404 (:status response))))))