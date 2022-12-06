$('#inputText').change(function () {
    $('#result').empty();
    search_func($('#inputText').val());
  });
  

function search_func(query) {
    $.getJSON("back-end/output/final_mapping.json", function(json) {
      // process query to all lower 
      query = query.toLowerCase()
      var results = [];
      var searchVal = query;
      
      // searching for title. if found, pass asin to other json file to find sentiment label
      for (var i=0 ; i < json.length ; i++) {
          title = json[i]["title"];
          title = String(title).toLowerCase();
          if (title.includes(searchVal)) {
            
            // push title to results array
            if (results.includes(json[i]["title"]) == false) {
              results.push(json[i]["title"]);
              asin = json[i]["asin"];
            }

            

            // look for sentiment value based on asin
            $.getJSON("back-end/output/sentiment_output.json", function(json2) {
              for (var i=0; i < json2.length; i++) {
                
                // push label to results array
                if (json2[i]["asin"] == asin) {
                  if (results.includes(json2[i]["label"]) == false) {
                    results.push(json2[i]["label"]);
                  }                  
                } 
                
                var final = "";
                // building the final output string
                if (!results.length) {
                  var sentiment_string = "";

                  if (results[1] == "pos") {
                  sentiment_string = "positive";

                  } else if (results[1] == "neg") {
                  sentiment_string = "negative";
                  } else {
                  sentiment_string = "neutral";
                  }

                  final = "Based on many reader's reviews, the overall sentiment around the novel " + results[0] + " is " + sentiment_string + ".";
                } else {
                  final = "No results were found for that title";
                }

                $('#result').html(final);
              }
            });
         }
      }
  });
}