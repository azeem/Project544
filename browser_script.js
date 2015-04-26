// ==UserScript==
// @name        UserPredictor
// @namespace   appliednlp.bitbucket.org
// @include     http://scifi.stackexchange.com/questions/ask
// @version     1
// @require     http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js
// @require     https://cdnjs.cloudflare.com/ajax/libs/underscore.js/1.8.3/underscore-min.js
// @grant       GM_xmlhttpRequest
// ==/UserScript==

var userPredTemplate = _.template([
  "<div class='module'>",
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
  "<div class='module'>",
  "  <h4>Similar Questions/h4>",
  "  <ul>",
  "    <% _.each(questions, function(question) { %>",
  "        <li><%= question %></li>",
  "    <% }); %>",
  "  </ul>",
  "</div>"  
].join("\n"));


var lastRequest1;
var lastRequest2;
var userPredDisplay;
var simQuestionDisplay;

function showPredictions(response) {
  data = JSON.parse(response.responseText);
  if(userPredDisplay) {
    userPredDisplay.remove();
  }
  userPredDisplay = $(userPredTemplate(data));
  $("#scroller").prepend(userPredDisplay);
}

function showSimilarQuestions(response) {
  data = JSON.parse(response.responseText);
  if(simQuestionDisplay) {
    simQuestionDisplay.remove();
  }
  simQuestionDisplay = $(simQuestionTemplate(data));
  $("#scroller").prepend(simQuestionDisplay);
}

$("#wmd-input").keypress(_.debounce(function() {
  if(lastRequest1) {
    lastRequest1.abort();
  }
  console.log("sending request 1");
  lastRequest1 = GM_xmlhttpRequest({
    url: "http://127.0.0.1:5000/predictUsers",
    method: "POST",
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    data: $.param({
      "method": "topicmodel",
      "document": $("#wmd-preview").html()
    }),
    onload: function(response) {
      console.log("got response 1");
      showPredictions(response);
      lastRequest1 = null;
    }
  });
  
  if(lastRequest2) {
    lastRequest2.abort();
  }
  console.log("sending request 2");
  lastRequest2 = GM_xmlhttpRequest({
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
