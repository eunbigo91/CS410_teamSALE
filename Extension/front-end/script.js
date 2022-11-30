$('#inputText').change(function () {
    $('#result').empty();
    search_func($('#inputText').val());
  });
  
function search_func(query) {
    $('#result').CSVToTable('back-end/output/sentiment_output.csv',{
        tableClass: "result_table",
        thClass: "table_header",
        trClass: "table_row",
        tdClass: "table_cell"
      });
}
