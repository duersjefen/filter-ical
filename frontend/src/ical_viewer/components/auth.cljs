(ns ical-viewer.components.auth
  (:require [re-frame.core :as rf]))

;; -- Authentication Components --

(defn login-form []
  (let [username @(rf/subscribe [:login-form])
        loading? @(rf/subscribe [:loading?])]
    [:div.login-form
     [:div.form-section
      [:h2 "👋 Welcome to iCal Viewer"]
      [:p.subtitle "Enter your username to access your calendars and filters"]
      
      [:form {:on-submit (fn [e]
                           (.preventDefault e)
                           (rf/dispatch [:login]))}
       [:div.form-row
        [:label {:for "username"} "Username"]
        [:input {:id "username"
                 :type "text"
                 :placeholder "Enter your username"
                 :value (:username username)
                 :disabled loading?
                 :on-change #(rf/dispatch [:set-login-username (-> % .-target .-value)])
                 :auto-focus true}]]
       
       [:div.form-row
        [:button.btn.btn-primary
         {:type "submit"
          :disabled (or loading? (empty? (:username username)))}
         (if loading? "Logging in..." "Login")]]]]]))

(defn user-info []
  (let [username @(rf/subscribe [:username])]
    [:div.user-info
     [:span (str "👤 " username)]
     [:button.btn.btn-outline
      {:on-click #(rf/dispatch [:logout])}
      "Logout"]]))

(defn login-required [content]
  (let [logged-in? @(rf/subscribe [:logged-in?])]
    (if logged-in?
      content
      [login-form])))

(defn user-header []
  (let [logged-in? @(rf/subscribe [:logged-in?])]
    (when logged-in?
      [:div.user-header
       [user-info]])))