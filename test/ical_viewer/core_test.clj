(ns ical-viewer.core-test
  (:require [clojure.test :refer [deftest is testing]]
            [ring.mock.request :as mock]
            [ical-viewer.core :refer [app]]))

(deftest test-api-entries
  (testing "GET /api/entries"
    (let [response (app (mock/request :get "/api/entries"))]
      (is (= 200 (:status response)))
      (is (some? (:body response)))
      (is (re-find #"https://ics.calendarlabs.com/41/d1cafc5d/Christian_Holidays.ics" (:body response))))))