// ==UserScript==
// @name        UserPredictor
// @namespace   appliednlp.bitbucket.org
// @include     http://scifi.stackexchange.com/questions/ask
// @version     1
// @require     http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js
// @require     https://cdnjs.cloudflare.com/ajax/libs/underscore.js/1.8.3/underscore-min.js
// @grant       GM_xmlhttpRequest
// @grant       GM_addStyle
// ==/UserScript==

GM_addStyle("#scroller {position: relative !important;} #how-to-format {display: none !important;}");

var userPredTemplate = _.template([
  "<div class='module newuser'>",
  "  <h4>Suggested Users</h4>",
  //"  <ul>",
  "    <% _.each(users, function(user) { %>",
  "        <div style='clear: both; margin-top: 12px;'>",
  "            <div style='float: left;margin-right: 10px;'>",
  "                <a href='/users/<%= user.id %>/<%= user.displayname %>'>",
  "                    <div>",
  "                        <img width='32' height='32' src='<%= user.profileimageurl || 'http://www.gravatar.com/avatar?f=y&s=32&d=identicon&r=PG' %>'></img>",
  "                    </div>",
  "                </a>",
  "            </div>",
  "            <div>",
  "                <a href='/users/<%= user.id %>/<%= user.displayname %>'><%= user.displayname %></a><br/>",
  "                <span dir='ltr' title='reputation score'><%= user.reputation %></span>",
  "            </div>",  
  "        </div>",
  "    <% }); %>",
  //"  </ul>",
  "</div>"  
].join("\n"));

var simQuestionTemplate = _.template([
  "<div class='module newuser'>",
  "  <h4>Similar Questions</h4>",
  "  <ul>",
  "    <% _.each(questions, function(question) { %>",
  "        <li><a href='/questions/<%= question[0] %>'><%= question[1] %></a></li>",
  "    <% }); %>",
  "  </ul>",
  "</div>"  
].join("\n"));

var userPredDisplay;
var simQuestionDisplay;

$("#scroller").prepend("<span id='user-pred-container'></span><span id='simq-container'></span>");

function showPredictions(response) {
  data = JSON.parse(response.responseText);
  if(userPredDisplay) {
    userPredDisplay.remove();
  }
  userPredDisplay = $(userPredTemplate(data));
  $("#user-pred-container").prepend(userPredDisplay);
}

function showSimilarQuestions(response) {
  data = JSON.parse(response.responseText);
  if(simQuestionDisplay) {
    simQuestionDisplay.remove();
  }
  simQuestionDisplay = $(simQuestionTemplate(data));
  $("#simq-container").prepend(simQuestionDisplay);
}

$("#wmd-input").keypress(_.debounce(function() {
  var tags = $(".post-tag").map(function() {
    return $(this).text();
  }).get().join(",");
  console.log(tags);
  GM_xmlhttpRequest({
    url: "http://127.0.0.1:5000/predictUsers",
    method: "POST",
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    data: $.param({
      "tags": tags,
      "document": $("#wmd-preview").html()
    }),
    onload: function(response) {
      console.log("got response 1");
      showPredictions(response);
      lastRequest1 = null;
    }
  });
  
  GM_xmlhttpRequest({
    url: "http://127.0.0.1:5000/findSimilarQuestions",
    method: "POST",
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    data: $.param({
      "document": $("#wmd-preview").html()
    }),
    onload: function(response) {
      console.log("got response 2");
      showSimilarQuestions(response);
      lastRequest2 = null;
    }
  });
  console.dir(lastRequest2);
}, 1000));
