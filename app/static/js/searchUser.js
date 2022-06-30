export default function searchUser(inputId, callback, clear=false, parentElementId=null, columnRequested=null, category = null){
  var query = $(`#${inputId}`).val()
  let columnDict={};
  $(`#${inputId}`).autocomplete({
    appendTo: (parentElementId === null) ? null : `#${parentElementId}`,
    minLength: 2,
    source: function(request, response) {
      $.ajax({
        url: `/searchUser/${query}`,
        type: "GET",
        dataType: "json",
        data:{"category":category},
        success: function(searchResults) {
          response(Object.entries(searchResults).map( (item) => {
            if (!columnRequested){
              return {
                // label: firstName lastName (username)
                // value: username
                label: (item[1]["firstName"]+" "+item[1]["lastName"]+" ("+item[0]+")"),
                value: item[0]
              }
            } else {
              for (const column of columnRequested) {
                columnDict[column]=item[1][column];
              };
              return {
                // label: firstName lastName (username)
                // value: "{column: response, column2: response2, ...}"
                // must JSON.parse
                label: (item[1]["firstName"]+" "+item[1]["lastName"]+" ("+item[0]+")"),
                dictvalue:JSON.stringify(columnDict),
                
                
                
                
              }
            }
          }
        ))},
        error: function(request, status, error) {
          console.log(status, error);
        }
      })
    },
     select: function(event, ui) {
       var user = ui.item.value
       $(`#${inputId}`).val(ui.item.dictvalue);
       callback();
       if(clear){
         $(`#${inputId}`).val("");
       return false;
     }
     }
  });
};
