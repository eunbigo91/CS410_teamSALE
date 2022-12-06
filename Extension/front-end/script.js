$('#inputText').change(function () {
    $('#result').empty();
    search_func($('#inputText').val());
  });
  

function search_func(query) {
    $.getJSON("back-end/output/final_mapping.json", function(json) {
      // process query to all lower 
      var results = [];
      var searchVal = query.toLowerCase();
      
      // searching for title. if found, get label
      for (var i=0 ; i < json.length ; i++) {
          title = json[i]["title"];
          title = String(title).toLowerCase();
          if (title == searchVal && results.includes(json[i]["title"]) == false) {
            
            // push title to results array
              results.push(json[i]["title"]);
              results.push(json[i]["label"]);
         }
      }

      var final = "";
      // building the final output string
      if (results.length > 0) {
        var sentiment_string = "";

        if (results[1] == "pos") {
        sentiment_string = "positive";

        } else if (results[1] == "neg") {
        sentiment_string = "negative";
        } else {
        sentiment_string = "neutral";
        }

        final = "Based on many reader's reviews, the overall sentiment around the novel " + results[0].bold() + " is " + sentiment_string.bold() + ".";
      } else {
        final = "No results were found for that title.";
      }

     $('#result').html(final);
  });
}