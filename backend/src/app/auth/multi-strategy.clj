(ns app.auth.multi-strategy
  (:require [app.auth.telegram :as telegram]
            [app.auth.magic-link :as magic-link]
            [app.auth.simple-token :as simple-token]))

(defn create-auth-selection-page []
  [:div.auth-selection
   [:div.header
    [:h1 "🗓️ Welcome to iCal Viewer"]
    [:p.subtitle "Choose your preferred way to access your calendars:"]]

   [:div.auth-options
    ;; Telegram option
    [:div.auth-option.recommended
     [:div.option-header
      [:h3 "📱 Telegram"]
      [:span.badge "Recommended"]]
     [:div.option-description
      [:p "Instant login through Telegram. No passwords, maximum security."]
      [:ul.benefits
       [:li "✅ Zero setup required"]
       [:li "✅ Works on mobile & desktop"]
       [:li "✅ Most secure option"]]]
     [:div.option-action
      (telegram/create-telegram-auth-component)]]

    ;; Magic Link option  
    [:div.auth-option
     [:div.option-header
      [:h3 "✨ Magic Link"]]
     [:div.option-description
      [:p "Login via email link. No passwords to remember."]
      [:ul.benefits
       [:li "✅ Works with any email"]
       [:li "✅ No app required"]
       [:li "✅ Secure & familiar"]]]
     [:div.option-action
      (magic-link/create-magic-link-component)]]

    ;; Simple Token option
    [:div.auth-option
     [:div.option-header
      [:h3 "🔑 Personal Token"]]
     [:div.option-description
      [:p "Generate a personal access token for immediate access."]
      [:ul.benefits
       [:li "✅ Instant access"]
       [:li "✅ Perfect for personal use"]
       [:li "✅ Bookmark-friendly URLs"]]]
     [:div.option-action
      (simple-token/create-simple-auth-component)]]]

   [:div.auth-footer
    [:h4 "🔒 Privacy & Security"]
    [:p "Your calendar data never leaves your server. All authentication methods are secure and respect your privacy."]
    [:details
     [:summary "Technical Details"]
     [:ul
      [:li "Telegram: Uses Telegram's Web App authentication with HMAC verification"]
      [:li "Magic Link: Time-limited tokens sent to your email"]
      [:li "Personal Token: UUID-based tokens stored securely"]
      [:li "All connections use HTTPS and tokens expire appropriately"]]]]])

;; Enhanced CSS for auth page
(defn auth-styles []
  [:style "
    .auth-selection { max-width: 900px; margin: 40px auto; padding: 20px; }
    .auth-options { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; margin: 30px 0; }
    
    .auth-option { 
      border: 2px solid #e9ecef; 
      border-radius: 12px; 
      padding: 25px; 
      background: white; 
      box-shadow: 0 4px 6px rgba(0,0,0,0.05);
      transition: all 0.3s ease;
    }
    .auth-option:hover { 
      transform: translateY(-2px); 
      box-shadow: 0 8px 15px rgba(0,0,0,0.1);
      border-color: #007bff;
    }
    
    .auth-option.recommended { 
      border-color: #28a745; 
      background: linear-gradient(135deg, #ffffff 0%, #f8fff9 100%);
    }
    .auth-option.recommended .option-header h3 { color: #28a745; }
    
    .option-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
    .option-header h3 { margin: 0; color: #495057; }
    
    .badge { 
      background: #28a745; 
      color: white; 
      padding: 4px 8px; 
      border-radius: 12px; 
      font-size: 0.75em; 
      font-weight: 500;
    }
    
    .option-description { margin: 15px 0; }
    .benefits { padding-left: 0; list-style: none; }
    .benefits li { 
      padding: 4px 0; 
      color: #28a745; 
      font-size: 0.9em;
    }
    
    .option-action { margin-top: 20px; padding-top: 20px; border-top: 1px solid #e9ecef; }
    
    .telegram-auth, .magic-link-auth, .simple-auth { text-align: center; }
    .telegram-auth h3, .magic-link-auth h3, .simple-auth h3 { 
      font-size: 1.1em; 
      margin-bottom: 15px; 
      color: #6c757d;
    }
    
    .token-box { 
      background: #f8f9fa; 
      border: 1px solid #dee2e6; 
      border-radius: 6px; 
      padding: 15px; 
      margin: 15px 0; 
      display: flex; 
      align-items: center; 
      gap: 10px;
    }
    .token-box code { 
      flex: 1; 
      background: none; 
      font-family: 'Monaco', monospace; 
      font-size: 0.9em;
    }
    
    .token-instructions { 
      font-size: 0.9em; 
      color: #6c757d; 
      text-align: left; 
      line-height: 1.4;
    }
    
    .status-message { 
      padding: 10px 15px; 
      border-radius: 6px; 
      margin: 15px 0; 
      font-weight: 500;
    }
    .status-message.info { background: #d1ecf1; color: #0c5460; border: 1px solid #b8daff; }
    .status-message.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .status-message.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    
    .auth-footer { 
      margin-top: 40px; 
      padding: 25px; 
      background: #f8f9fa; 
      border-radius: 8px; 
      text-align: center;
    }
    .auth-footer h4 { color: #495057; margin-bottom: 10px; }
    .auth-footer details { text-align: left; margin-top: 15px; }
    .auth-footer summary { cursor: pointer; font-weight: 500; color: #007bff; }
    .auth-footer ul { margin: 10px 0; }
    .auth-footer li { margin: 5px 0; font-size: 0.9em; color: #6c757d; }
  "])

;; Route handlers for different auth methods
(defn auth-routes []
  (compojure.core/routes
   (GET "/auth" []
     (app.server/layout "Choose Authentication"
                        (create-auth-selection-page)
                        (auth-styles)))

   (POST "/auth/telegram" {body :body}
     (let [auth-data (json/read-str (slurp body) :key-fn keyword)]
       (if (verify-telegram-auth auth-data (System/getenv "TELEGRAM_BOT_TOKEN"))
         {:status 200
          :headers {"Content-Type" "application/json"}
          :body (json/write-str {:success true
                                 :token (generate-session-token (:id (:user auth-data)))})}
         {:status 401 :body "Invalid authentication"})))

   (POST "/auth/magic-link" {params :params}
     (let [email (:email params)]
       (send-magic-link email (System/getenv "BASE_URL"))
       {:status 200
        :headers {"Content-Type" "application/json"}
        :body (json/write-str {:success true})}))

   (GET "/auth/verify/:token" [token]
     (if-let [login-info (get @pending-logins token)]
       (if (< (System/currentTimeMillis) (:expires-at login-info))
         (do
           (swap! pending-logins dissoc token)
           (let [user-token (generate-session-token (:email login-info))]
             (-> (response/redirect "/?verified=true")
                 (assoc-in [:cookies "auth-token"]
                           {:value user-token :max-age (* 60 60 24 30)}))))
         {:status 400 :body "Magic link expired"})
       {:status 404 :body "Invalid magic link"}))

   (POST "/auth/generate-token" []
     (let [token (generate-user-token)]
       {:status 200
        :headers {"Content-Type" "application/json"}
        :body (json/write-str {:token token})}))))