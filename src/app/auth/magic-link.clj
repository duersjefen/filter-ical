(ns app.auth.magic-link
  (:require [postal.core :as postal]
            [clojure.string :as str])
  (:import [java.util UUID]))

(def pending-logins (atom {}))

(defn generate-magic-link [email]
  (let [token (str (UUID/randomUUID))
        expires-at (+ (System/currentTimeMillis) (* 1000 60 15))] ; 15 minutes
    (swap! pending-logins assoc token {:email email :expires-at expires-at})
    token))

(defn send-magic-link [email base-url]
  (let [token (generate-magic-link email)
        magic-url (str base-url "/auth/verify/" token)]
    (postal/send-message
     {:host "smtp.gmail.com" ; Configure your SMTP
      :user "your-app@gmail.com"
      :pass "your-app-password"
      :ssl true}
     {:from "iCal Viewer <your-app@gmail.com>"
      :to email
      :subject "🗓️ Your iCal Viewer Login Link"
      :body (str "Click here to log in: " magic-url
                 "\n\nThis link expires in 15 minutes.")})))

(defn create-magic-link-component []
  [:div.magic-link-auth
   [:h3 "✨ Login with Magic Link"]
   [:form {:onsubmit "sendMagicLink(event)"}
    [:div.form-group
     [:input {:type "email" :id "email" :placeholder "your@email.com" :required true}]]
    [:button {:type "submit" :class "btn btn-primary"} "📧 Send Magic Link"]]

   [:div#magic-link-status.status-message {:style "display: none;"}]

   [:script "
     async function sendMagicLink(e) {
       e.preventDefault();
       const email = document.getElementById('email').value;
       const status = document.getElementById('magic-link-status');
       
       status.style.display = 'block';
       status.textContent = 'Sending magic link...';
       status.className = 'status-message info';
       
       try {
         const response = await fetch('/auth/magic-link', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({ email: email })
         });
         
         if (response.ok) {
           status.textContent = '✅ Magic link sent! Check your email.';
           status.className = 'status-message success';
         } else {
           throw new Error('Failed to send magic link');
         }
       } catch (error) {
         status.textContent = '❌ Failed to send magic link. Please try again.';
         status.className = 'status-message error';
       }
     }
   "]])

(defn email-configured? []
  "Check if email configuration is available"
  ;; For now, just return true - in production would check SMTP settings
  true)

(defn create-email-form []
  "Create email form component"
  (create-magic-link-component))

(defn validate-magic-link [token]
  "Validate magic link token"
  (let [login-data (get @pending-logins token)]
    (when (and login-data 
               (< (System/currentTimeMillis) (:expires-at login-data)))
      ;; Valid token - remove it and return user data
      (swap! pending-logins dissoc token)
      {:user-id (str "email:" (:email login-data))
       :name (:email login-data)
       :platform "email"
       :auth-time (System/currentTimeMillis)})))

(defn magic-link-routes []
  "Return magic link routes"
  [
   {:method :post
    :path "/auth/magic-link/send"
    :handler (fn [request]
               ;; This would send the magic link
               {:status 200
                :headers {"Content-Type" "application/json"}
                :body "{\"success\": true}"})}])