(ns app.auth.simple-token)

(defn generate-user-token []
  "Generate a simple but secure user token"
  (str "ical_" (UUID/randomUUID)))

(defn create-simple-auth-component []
  [:div.simple-auth
   [:h3 "🔑 Quick Setup"]
   [:p "Get instant access with a personal token:"]
   [:button.btn.btn-primary
    {:onclick "generatePersonalToken()"}
    "🎯 Generate My Token"]

   [:div#token-display {:style "display: none;"}
    [:h4 "Your Personal Token:"]
    [:div.token-box
     [:code#user-token]
     [:button.btn.btn-sm {:onclick "copyToken()"} "📋 Copy"]]
    [:p.token-instructions
     "Save this token - you'll need it to access your calendars. "
     [:br] "Add ?token=YOUR_TOKEN to any URL or set it in preferences."]]

   [:script "
     function generatePersonalToken() {
       fetch('/auth/generate-token', { method: 'POST' })
         .then(response => response.json())
         .then(data => {
           document.getElementById('user-token').textContent = data.token;
           document.getElementById('token-display').style.display = 'block';
           localStorage.setItem('ical-token', data.token);
         });
     }
     
     function copyToken() {
       const token = document.getElementById('user-token').textContent;
       navigator.clipboard.writeText(token);
       alert('Token copied to clipboard!');
     }
   "]])