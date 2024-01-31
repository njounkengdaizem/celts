$(document).ready(function(){
    $("#expressInterest").on("click", function() {
      let username = $("#username").val()
      let data = {"username":username}
      $.ajax({
          url: "/cceMinor/"+username+"/indicateInterest",
          type: "POST",
          data: data,
          success: function(s) {
            location.reload()
          },
          error: function(request, status, error) {
            console.log(error)
            msgFlash("Error saving changes!", "danger")
          }
      });
    })    

    $("#summerExperienceSave").click(function(){
      let data = {'summerExperience': $("#summerExperience").val(),
                  'selectedSummerTerm': $("#summerExperienceTerm").find(":selected").text()}
      let username = $("#username").val()
      $.ajax({
        type: "POST", 
        url: "/cceMinor/"+username+"/addSummerExperience",
        data: data,
        success: function(s){
          
        },
        error: function(error){
          console.error("Error:", error);
        }
      })

    });

    $('.engagement-row').on("click", function() {
        showEngagementInformation($(this).data('engagement-data'));
    });

    $('.engagement-row input').on("click", function(e) {
        e.stopPropagation()

        engagementData = $(this).parents('.engagement-row').data('engagement-data');
        toggleEngagementCredit($(this).is(':checked'), engagementData)
    });
    
})

function showEngagementInformation(dataDict) {
  let type = dataDict['type'],
      id = dataDict['id'],
      term= dataDict['term'];
  let username = $("#username").val()

  // based on how long the type is, get the remaining characters afterwards that represent the id
  $.ajax({
    url: `/cceMinor/${username}/getEngagementInformation/${type}/${term}/${id}`,
    type: "GET",
    data: "",
    success: function(response) {
      // create the list that will store the html
      // will be joined later to make a string
      var html = [] 
      html.push("<div>")
      if (type == "program") {
        let program = response["program"]
        let events = response["events"]
        let totalHours = response["totalHours"]

        html.push(`<h4>${program} History</h4>`)
        html.push(`Total volunteer hours: ${totalHours}`)
        html.push("<ul>")

        // add a list element to the html for each event in our list of events
        // link to the event view page as well
        for (let i = 0; i < events.length; i++) {
          html.push(`<li><a href="/event/${events[i]["id"]}/view" target="_blank">${events[i]["name"]}</a> - ${events[i]["hoursEarned"]} hrs</li>`)
        }

        html.push("</ul>")
      } else {
        let course = response["course"]
        let instructors = response["instructors"]

        // only show the course abbreviation and name if they exist, or only show the ones that exist
        if (course["courseAbbreviation"] && course["courseName"]) {
          html.push(`<h4>${course["courseAbbreviation"]}: ${course["courseName"]}</h4>`)
        } else if (course["courseAbbreviation"]) {
          html.push(`<h4>${course["courseAbbreviation"]}</h4>`)
        } else {
          html.push(`<h4>${course["courseName"]}</h4>`)
        }
        // add important fields to display
        html.push(`<p><b>Instructors:</b> ${instructors.join(", ")}</p>`)
        html.push(`<p><b>Section Designation:</b> ${course["sectionDesignation"] || "None"}</p>`)
        html.push(`<p><b>Course Credit:</b> ${course["courseCredit"]}</p>`)
        html.push(`<p><b>SLC Component:</b> ${Boolean(course["hasSlcComponent"]) ? "Yes" : "No"}</p>`)
      }
      html.push("</div>")
      // modify the displayed html by joining together the list we have been pushing to
      $(`#set${term}`).html(html.join(""))
    },
    error: function(request, status, error) {
      msgFlash("Error displaying information!", "danger")
    }
  });
}

function stopPropagation(event) {
  // prevent the checkbox from displaying the course/program information
  console.log(event.target)
}

function toggleEngagementCredit(isChecked, engagementData){
    engagementData['username'] = $("#username").val();

    $.ajax({
          url: `/cceMinor/${engagementData['username']}/modifyCommunityEngagement`,
          type: isChecked ? "PUT" : "DELETE",
          data: engagementData,
          success: function(response) {
              if (response == ""){ 
                let header = isChecked ? 'Added' : 'Removed';
                msgToast("Success!", header + " engagement for " + engagementData['name'])
              } else {
                msgToast("Error saving changes!", response)
              }
            },
          error: function(request, status, error) {
            console.log(error)
            msgFlash("Error saving changes!", "danger")
          }
    });
}
